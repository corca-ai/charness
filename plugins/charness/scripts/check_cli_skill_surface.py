#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shlex
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
REQUIRED_PRODUCT_SURFACES = {"installable_cli", "bundled_skill"}
DEFAULT_COMMAND_DOCS = (".agents/command-docs.yaml",)
DEFAULT_CHANGE_GLOBS = (
    "charness",
    "scripts/**",
    "skills/public/**",
    "skills/support/**",
    "plugins/**",
    ".claude-plugin/**",
    ".agents/plugins/**",
    "packaging/**",
    ".agents/command-docs.yaml",
)
DEFAULT_PROBE_TIMEOUT_SECONDS = 20.0
TIMEOUT_EXIT_CODE = 124
PROBE_ATTEMPTS = 2
DRAIN_TIMEOUT_SECONDS = 5.0
PROBE_TIMEOUT_ENV = "CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"
DRAIN_TIMEOUT_ENV = "CHARNESS_CLI_SKILL_SURFACE_DRAIN_TIMEOUT_SECONDS"
_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file
validate_adapter_version = _adapter_lib.validate_adapter_version
_agent_browser_probe_policy = import_repo_module(__file__, "scripts.agent_browser_probe_policy")
unsafe_agent_browser_probe_reason = _agent_browser_probe_policy.unsafe_agent_browser_probe_reason


def _string_list(data: dict[str, Any], field: str) -> list[str]:
    value = data.get(field)
    return list(value) if isinstance(value, list) and all(isinstance(item, str) for item in value) else []


def _load_adapter(repo_root: Path, adapter_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Return adapter data and any version errors, refusing the data on a version this
    reader does not speak.

    This gate SELECTS SUBPROCESSES to run (`cli_skill_surface_probe_commands`) and can be
    switched off entirely by `product_surfaces`, so honoring an unreconciled schema version
    here is a strictly harder trust boundary than a resolver that only echoes fields. An
    unspeakable version yields no data at all, not partially honored data.
    """
    path = adapter_path if adapter_path.is_absolute() else repo_root / adapter_path
    raw = load_yaml_file(path) if path.is_file() else {}
    if not isinstance(raw, dict):
        return {}, []
    errors: list[str] = []
    validate_adapter_version(raw, {}, errors)
    return ({}, errors) if errors else (raw, [])


def _required(data: dict[str, Any]) -> bool:
    return REQUIRED_PRODUCT_SURFACES.issubset(set(_string_list(data, "product_surfaces")))


def _default_skill_paths(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    public_root = repo_root / "skills" / "public"
    generated_support_root = repo_root / "skills" / "support" / "generated"
    direct_skill_root = repo_root / "skills"
    if public_root.is_dir():
        paths.extend(sorted(public_root.glob("*/SKILL.md")))
    if generated_support_root.is_dir():
        paths.extend(sorted(generated_support_root.glob("*/SKILL.md")))
    if direct_skill_root.is_dir():
        paths.extend(sorted(direct_skill_root.glob("*/SKILL.md")))
    return paths


def _has_root_executable(repo_root: Path) -> bool:
    if not repo_root.is_dir():
        return False
    for path in repo_root.iterdir():
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix in {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".lock"}:
            continue
        if path.stat().st_mode & 0o111:
            return True
    return False


def _has_cli_marker(repo_root: Path, data: dict[str, Any]) -> bool:
    return bool(_probe_commands(data)) or bool(_existing_docs(_command_doc_paths(repo_root, data))) or _has_root_executable(repo_root)


def _product_surface_source(repo_root: Path, data: dict[str, Any], skills: list[Path]) -> str | None:
    if _required(data):
        return "declared"
    if skills and _has_cli_marker(repo_root, data):
        return "inferred"
    return None


def _relevant_change(data: dict[str, Any], changed_paths: list[str]) -> bool:
    if not changed_paths:
        return True
    globs = _string_list(data, "cli_skill_surface_change_globs") or list(DEFAULT_CHANGE_GLOBS)
    return any(fnmatch.fnmatch(path, pattern) for path in changed_paths for pattern in globs)


def _skill_paths(repo_root: Path, data: dict[str, Any]) -> list[Path]:
    configured = _string_list(data, "cli_skill_surface_skill_paths")
    if configured:
        return [(repo_root / path).resolve() for path in configured]
    return _default_skill_paths(repo_root)


def _command_doc_paths(repo_root: Path, data: dict[str, Any]) -> list[Path]:
    configured = _string_list(data, "cli_skill_surface_command_docs") or list(DEFAULT_COMMAND_DOCS)
    return [(repo_root / path).resolve() for path in configured]


def _existing_docs(paths: list[Path]) -> list[Path]:
    return [path for path in paths if path.is_file()]


def _probe_commands(data: dict[str, Any]) -> list[str]:
    return _string_list(data, "cli_skill_surface_probe_commands")


def _positive_timeout_seconds(env_name: str, default: float) -> float:
    raw = os.environ.get(env_name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _probe_timeout_seconds() -> float:
    return _positive_timeout_seconds(PROBE_TIMEOUT_ENV, DEFAULT_PROBE_TIMEOUT_SECONDS)


def _drain_timeout_seconds() -> float:
    return _positive_timeout_seconds(DRAIN_TIMEOUT_ENV, DRAIN_TIMEOUT_SECONDS)


def _decoded(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value if isinstance(value, str) else ""


def _kill_group_and_drain(process: subprocess.Popen[str]) -> tuple[str, str]:
    """Kill the probe's whole process group, then drain under its own deadline.

    A bare `subprocess.run(..., timeout=)` kills only the DIRECT child and then
    drains with no deadline at all, so a surviving grandchild holding the
    inherited pipes hangs the drain forever -- and `run-quality.sh` puts no wall
    clock around a queued label, so nothing above would recover. `doctor.py`
    shells out per capability, so grandchildren are the normal case here, not an
    exotic one.
    """
    # Signal the group by the child's OWN pid, never by `os.getpgid(child)`.
    # `start_new_session=True` makes the child its own group leader, so the two
    # are equal in the normal case -- but `getpgid` returns the SHARED group the
    # moment that flag stops applying, and killpg on it SIGKILLs the whole
    # quality run: every sibling check, the runner, and the shell. Measured, not
    # theorised: a mutant flipping that flag did exactly that three times during
    # this slice, each time killing the sweep mid-run and leaving the tree
    # mutated. This narrows the blast radius; it does not prove one, and it
    # rests on `start_new_session` holding. If that flag ever stops applying,
    # a recycled pid could still name a stranger group, and no test here can
    # construct that state -- untestable, not observed-absent.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        process.kill()
    try:
        return process.communicate(timeout=_drain_timeout_seconds())
    except subprocess.TimeoutExpired as exc:
        # Keep what the pipe already yielded. `TimeoutExpired` carries every byte
        # read so far -- INCLUDING the bytes the probe-deadline `communicate`
        # consumed, because the resumed call reuses the same buffers -- so
        # returning empty strings here would discard the partial verdict this
        # whole repair exists to preserve, one call deeper than the defect it
        # replaced. Bytes even in text mode: CPython joins raw chunks and only
        # decodes on the success path.
        return _decoded(exc.output), _decoded(exc.stderr)
    finally:
        # killpg can succeed WITHOUT reaching the direct child (a probe that
        # re-parents its own group), and then `Popen.__exit__` would call an
        # unbounded `wait()` on a live child -- B2's hang, narrowed but not
        # closed. Killing the child outright is the containment. UNPROVEN by
        # test: a mutation sweep confirmed this line can be deleted with the
        # suite green, because no fixture constructs a probe that re-parents
        # its own group. Kept as cheap defence, not claimed as covered.
        process.kill()


def _attempt_probe(repo_root: Path, command: str, timeout_seconds: float) -> dict[str, object]:
    """Run `command` once in its own process group."""
    with subprocess.Popen(
        shlex.split(command),
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            # The deadline can expire with a verdict ALREADY PRODUCED and merely
            # unread -- a child that exited while a grandchild still held the
            # pipe. So keep whatever was captured instead of discarding it: the
            # honest claim is that this run did not OBSERVE a verdict, which is
            # weaker than saying the command never rendered one.
            stdout, stderr = _kill_group_and_drain(process)
            return {
                "command": command,
                "returncode": TIMEOUT_EXIT_CODE,
                "stdout_preview": (stdout or "")[:400],
                "stderr_preview": (stderr or "")[:400],
                "timed_out": True,
            }
        return {
            "command": command,
            "returncode": process.returncode,
            "stdout_preview": stdout[:400],
            "stderr_preview": stderr[:400],
            "timed_out": False,
        }


def _run_probe(repo_root: Path, command: str) -> dict[str, object]:
    # This gate queues ~85 checks concurrently, so a probe's wall-clock deadline
    # is spent competing with its own siblings. A single starved run cost a real
    # session a push cycle: the probe needed 1.6s alone and 5.5s in-gate, but one
    # tail run hit the 20s deadline and was read as "the probe costs 21s". Retry
    # once, so a transient starve does not become a standing belief about cost.
    # Two attempts is a cheap hedge against contention, NOT a proof that a
    # command failing both is unhealthy -- the payload says unobserved either way.
    timeout_seconds = _probe_timeout_seconds()
    result: dict[str, object] = {}
    for attempt in range(1, PROBE_ATTEMPTS + 1):
        result = _attempt_probe(repo_root, command, timeout_seconds)
        result["attempts"] = attempt
        if not result["timed_out"]:
            return result
    result["deadline_seconds"] = timeout_seconds
    return result


def _unsafe_agent_browser_probe(command: str) -> str | None:
    return unsafe_agent_browser_probe_reason(command)


def _adapter_weaknesses(data: dict[str, Any], *, source: str, skills: list[Path]) -> list[str]:
    declared = set(_string_list(data, "product_surfaces"))
    weaknesses: list[str] = []
    if source == "inferred":
        for surface in sorted(REQUIRED_PRODUCT_SURFACES - declared):
            weaknesses.append(f"adapter does not declare `{surface}` in product_surfaces despite detected CLI plus skill shape")
    if not _string_list(data, "cli_skill_surface_probe_commands"):
        weaknesses.append("cli_skill_surface_probe_commands is empty for a CLI plus bundled-skill surface")
    if not _string_list(data, "cli_skill_surface_command_docs"):
        weaknesses.append("cli_skill_surface_command_docs is empty; using default command-doc discovery only")
    if skills and not _string_list(data, "cli_skill_surface_skill_paths"):
        weaknesses.append("cli_skill_surface_skill_paths is empty; using common skill layout discovery only")
    globs = _string_list(data, "cli_skill_surface_change_globs")
    if not globs:
        weaknesses.append("cli_skill_surface_change_globs is empty; using default broad change globs")
    elif not any(fnmatch.fnmatch("skills/public/demo/SKILL.md", pattern) for pattern in globs):
        weaknesses.append("cli_skill_surface_change_globs does not match common public skill paths")
    elif not any(fnmatch.fnmatch("plugins/demo/SKILL.md", pattern) for pattern in globs):
        weaknesses.append("cli_skill_surface_change_globs does not match common plugin export paths")
    return weaknesses


def build_payload(
    repo_root: Path,
    *,
    adapter_path: Path,
    changed_paths: list[str],
    run_probes: bool,
) -> dict[str, object]:
    data, adapter_version_errors = _load_adapter(repo_root, adapter_path)
    if adapter_version_errors:
        # Not `not_applicable`: reporting "nothing to check" would let an adapter this
        # reader cannot speak turn the gate off, which is the wrong failure direction.
        return {
            "status": "blocked",
            "adapter_path": str(adapter_path),
            "reason": "adapter declares a version this reader does not speak",
            "adapter_weaknesses": [],
            "blockers": [
                f"CLI plus skill adapter {adapter_path} is unusable: "
                + "; ".join(adapter_version_errors)
                + ". Probe commands and product surfaces were not read from it."
            ],
            "unobserved": [],
        }
    skills = [path for path in _skill_paths(repo_root, data) if path.is_file()]
    source = _product_surface_source(repo_root, data, skills)
    if source is None:
        return {
            "status": "not_applicable",
            "reason": "no declared or inferred installable CLI plus bundled-skill surface",
            "adapter_weaknesses": [],
        }
    if not _relevant_change(data, changed_paths):
        return {"status": "skipped", "reason": "no CLI, skill, plugin, package, or install-surface change matched"}

    probes = _probe_commands(data)
    docs = _existing_docs(_command_doc_paths(repo_root, data))
    adapter_weaknesses = _adapter_weaknesses(data, source=source, skills=skills)
    blockers: list[str] = []
    if not skills:
        blockers.append("No bundled public/support skill path was available to inspect.")
    if not docs and not any("--help" in command for command in probes):
        blockers.append("No command-docs file or `--help` probe delegates broad command discovery to the binary.")
    if not any(("doctor" in command or "--version" in command) for command in probes):
        blockers.append("No doctor/readiness or version probe demonstrates installable CLI readiness.")
    if not (docs or any(token in " ".join(probes).lower() for token in ("example", "catalog", "registry", "--json"))):
        blockers.append("No command-owned example, registry, catalog, or JSON probe is declared for packet/example shapes.")
    for command in probes:
        unsafe_reason = _unsafe_agent_browser_probe(command)
        if unsafe_reason:
            blockers.append(f"Unsafe CLI plus skill probe `{command}`: {unsafe_reason}.")

    # A probe that never returned did not FAIL -- nothing about the CLI was
    # observed. Both still refuse (the floor is unchanged), but they are kept in
    # separate lists so a reader cannot mistake "we never heard the CLI answer"
    # for "the CLI answered wrongly". Conflating them is how one starved run
    # became a session-long belief that the probe costs 21 seconds.
    probe_results = [_run_probe(repo_root, command) for command in probes] if run_probes else []
    unobserved: list[str] = []
    for result in probe_results:
        if result.get("timed_out"):
            deadline = result.get("deadline_seconds")
            unobserved.append(
                f"CLI plus skill probe verdict NOT OBSERVED: `{result['command']}` did not close its "
                f"output within {deadline:g}s on each of {result['attempts']} attempts; "
                f"readiness is unobserved, not failing"
            )
        elif result["returncode"] != 0:
            blockers.append(f"CLI plus skill probe failed: `{result['command']}` exited {result['returncode']}")

    findings = [
        {
            "type": "skill_core_review_prompt",
            "message": "Inspect bundled skill cores for agent-facing delegation to binary help, registries, examples, and readiness probes before prose review.",
            "skill_count": len(skills),
        }
    ]
    if blockers:
        status = "blocked"
    elif unobserved:
        status = "unobserved"
    else:
        status = "ok"
    return {
        "status": status,
        "adapter_path": str(adapter_path),
        "product_surface_source": source,
        "product_surfaces": _string_list(data, "product_surfaces"),
        "adapter_weaknesses": adapter_weaknesses,
        "changed_paths": changed_paths,
        "skill_paths": [str(path.relative_to(repo_root)) for path in skills],
        "command_docs": [str(path.relative_to(repo_root)) for path in docs],
        "probe_commands": probes,
        "probe_results": probe_results,
        "findings": findings,
        "blockers": blockers,
        "unobserved": unobserved,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--adapter-path", type=Path, default=Path(".agents/quality-adapter.yaml"))
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--run-probes", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build_payload(
        args.repo_root.resolve(),
        adapter_path=args.adapter_path,
        changed_paths=args.changed_path,
        run_probes=args.run_probes,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"CLI plus bundled-skill surface check: {payload['status']}")
        for blocker in payload.get("blockers", []):
            print(f"- {blocker}", file=sys.stderr)
        for item in payload.get("unobserved", []):
            print(f"- UNOBSERVED: {item}", file=sys.stderr)
    return 1 if payload["status"] in {"blocked", "unobserved"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
