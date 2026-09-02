#!/usr/bin/env python3
"""Runner environment, computed argv variables, and runtime-signal handoff."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_quality_engine_model import GateList, RunnerError

from runtime_bootstrap import configure_runtime_environment, import_repo_module

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _guard.run_process

_ARRAY_TOKEN = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\[@\]\}$")
_VALUE_TOKEN = re.compile(r"^\$([A-Za-z_][A-Za-z0-9_]*)$")


@dataclass
class RuntimeContext:
    repo_root: Path
    environment: dict[str, str]
    runtime_root: Path
    state_args: tuple[str, ...]
    temp_dir: Path
    regime: str

    @property
    def failure_log_dir(self) -> Path:
        return self.runtime_root / "quality-failure-logs"


def derive_regime(environment: dict[str, str], labels: str) -> str:
    override = environment.get("CHARNESS_RUNTIME_REGIME", "")
    if labels:
        return override or "filtered"
    extras = []
    if environment.get("CHARNESS_QUALITY_DEAD_CODE", "0") == "1":
        extras.append("-dead-code")
    if environment.get("CHARNESS_SUPPLY_CHAIN_ONLINE", "0") == "1":
        extras.append("-supply-chain")
    return "plus" + "".join(extras) if extras else ""


def prepare_runtime(
    repo_root: Path,
    *,
    mode: str,
    labels: str,
    base_environment: dict[str, str] | None = None,
) -> RuntimeContext:
    environment = configure_runtime_environment(
        repo_root, os.environ.copy() if base_environment is None else base_environment
    )
    environment["CHARNESS_QUALITY_MODE"] = mode
    regime = derive_regime(environment, labels)
    environment["CHARNESS_RUNTIME_REGIME"] = regime
    runtime_root = Path(environment["CHARNESS_RUNTIME_ROOT"])
    if environment.get("CHARNESS_RUNTIME_ROOT_AUTO") == "1":
        state_args: tuple[str, ...] = ()
    else:
        state_args = ("--state-root", str(runtime_root / "quality"))
    temp_dir = Path(tempfile.mkdtemp(prefix="quality-engine-", dir=environment.get("TMPDIR")))
    return RuntimeContext(repo_root, environment, runtime_root, state_args, temp_dir, regime)


def _probe(context: RuntimeContext, command: list[str]):
    return run_process(
        command, cwd=context.repo_root, env=context.environment, timeout_seconds=None
    )


def _changed_path_probe(context: RuntimeContext, label: str, command: list[str]):
    """Run one changed-path discovery command; a failure is named on stderr.

    The shell runner printed the context, command, exit code, and both streams
    (its `run_changed_path_git`), and a test pins the first line; a silent None
    would make the fail-closed coverage decision below indistinguishable from a
    clean tree.
    """
    result = _probe(context, command)
    if result.returncode == 0:
        return result
    print(f"run-quality: changed-path discovery command failed ({label})", file=sys.stderr)
    print("command: " + shlex.join(command), file=sys.stderr)
    print(f"exit_code: {result.returncode}", file=sys.stderr)
    print("STDOUT:", file=sys.stderr)
    print(result.stdout, end="", file=sys.stderr)
    print("STDERR:", file=sys.stderr)
    print(result.stderr, end="", file=sys.stderr)
    return None


def _git_merge_base(context: RuntimeContext) -> str:
    result = _probe(context, ["git", "merge-base", "origin/main", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else ""


def changed_paths(context: RuntimeContext) -> set[str] | None:
    inside = _probe(context, ["git", "rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0:
        return None
    paths: set[str] = set()
    upstream = _probe(
        context,
        [
            "git",
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{upstream}",
        ],
    )
    if upstream.returncode == 0:
        base = _changed_path_probe(
            context,
            "upstream-merge-base",
            ["git", "merge-base", "HEAD", upstream.stdout.strip()],
        )
        if base is None:
            return None
        diff = _changed_path_probe(
            context,
            "upstream-diff",
            [
                "git",
                "diff",
                "--name-only",
                f"{base.stdout.strip()}...HEAD",
            ],
        )
        if diff is None:
            return None
        paths.update(diff.stdout.splitlines())
    for label, command in (
        ("unstaged-diff", ["git", "diff", "--name-only"]),
        ("staged-diff", ["git", "diff", "--name-only", "--cached"]),
        (
            "untracked-list",
            ["git", "ls-files", "--others", "--exclude-standard"],
        ),
    ):
        result = _changed_path_probe(context, label, command)
        if result is None:
            return None
        paths.update(result.stdout.splitlines())
    return paths


def coverage_relevant_changes_present(context: RuntimeContext, labels: str) -> bool:
    if labels:
        return True
    paths = changed_paths(context)
    if paths is None:
        print(
            "run-quality: changed-path discovery failed; running check-coverage fail-closed.",
            file=sys.stderr,
        )
        return True
    prefixes = {
        "scripts/control_plane_lib.py",
        "scripts/control_plane_lifecycle_lib.py",
        "scripts/doctor.py",
        "scripts/install_provenance_lib.py",
        "scripts/install_tools.py",
        "scripts/support_sync_lib.py",
        "scripts/sync_support.py",
        "scripts/update_tools.py",
        "scripts/upstream_release_lib.py",
        "tools/check_coverage.py",  # export-guard: changed-path prefix list; a path pattern, never executed
        "scripts/check_coverage_lib.py",
        "tools/check_coverage_extra_lib.py",  # export-guard: changed-path prefix list; a path pattern, never executed
        "tests/control_plane/",
        "tests/quality_gates/test_check_coverage_inventory.py",
    }
    return any(
        path in prefixes
        or any(path.startswith(prefix) for prefix in prefixes if prefix.endswith("/"))
        for path in paths
    )


def changed_line_base_sha_available(context: RuntimeContext) -> bool:
    return bool(_git_merge_base(context))


def provenance_contract_checker_available(context: RuntimeContext) -> bool:
    return any(
        (context.repo_root / relative).is_file()
        for relative in (
            "skills/public/quality/scripts/check_provenance_contract.py",
            "skills/quality/scripts/check_provenance_contract.py",
        )
    )


def _pytest_variables(
    context: RuntimeContext,
    *,
    mode: str,
    release: bool,
    include_release_only: bool,
    selected_labels: set[str],
    needed: frozenset[str],
) -> dict[str, list[str] | str]:
    result: dict[str, list[str] | str] = {}
    flags = ["--repo-root", str(context.repo_root), "--mode", mode]
    if release or "pytest-release" in selected_labels or include_release_only:
        flags.append("--include-release-only")
    result["PYTEST_FLAGS"] = flags
    for name, flag in (
        ("STANDING_PYTEST_TARGETS", "--print-expanded-targets"),
        ("PYTEST_DEBUG_TEMPROOT", "--print-temp-root"),
    ):
        if name not in needed:
            continue
        output = _probe(
            context,
            [
                "python3",
                "scripts/run_standing_pytest.py",
                "--repo-root",
                str(context.repo_root),
                flag,
            ],
        )
        if output.returncode != 0:
            raise RunnerError(f"could not resolve {name}: {output.stderr.strip()}")
        if name == "STANDING_PYTEST_TARGETS":
            result[name] = [line for line in output.stdout.splitlines() if line]
        else:
            result[name] = output.stdout.strip()
            context.environment[name] = str(result[name])
    return result


def _git_variables(context: RuntimeContext) -> dict[str, str]:
    base = _git_merge_base(context)
    return {"CHANGED_LINE_BASE_SHA": base, "CRITIQUE_CHANGED_REF": f"{base}..HEAD" if base else ""}


def _file_variables(context: RuntimeContext) -> dict[str, str]:
    return {
        "PROVENANCE_CONTRACT_CHECKER": next(
            (
                str(context.repo_root / relative)
                for relative in (
                    "skills/public/quality/scripts/check_provenance_contract.py",
                    "skills/quality/scripts/check_provenance_contract.py",
                )
                if (context.repo_root / relative).is_file()
            ),
            "",
        ),
        "RUN_QUALITY_RUNTIME_PROFILE": context.environment.get("CHARNESS_RUNTIME_PROFILE", ""),
        "release_changed_line_coverage_json": str(
            context.runtime_root / "release-changed-line-coverage" / "coverage.json"
        ),
    }


def _python_files(context: RuntimeContext) -> list[str]:
    """py-compile's universe is the adapter's `python_sources` family, not a literal.

    The engine used to carry a second glob list that omitted tools/ and read no
    adapter; the universes family owns this scope for ruff, check-python-lengths,
    and runtime inheritance too, so the four cannot drift apart again.
    """
    universes = import_repo_module(__file__, "scripts.quality_universes_lib")
    adapter = import_repo_module(__file__, "scripts.quality_adapter_lib")
    payload = adapter.load_quality_adapter(context.repo_root)
    universe = universes.resolve_universe(
        payload, "python_sources", default=universes.DEFAULT_UNIVERSES["python_sources"]
    )
    files = sorted(
        path.relative_to(context.repo_root).as_posix()
        for path in universes.matching_files(context.repo_root, universe)
        if path.suffix == ".py"
    )
    refusal = universes.refuse_if_declared_and_empty(universe, files, "py-compile")
    if refusal:
        raise RunnerError(refusal)
    if not files:
        raise RunnerError("py-compile: refusing empty matched universe")
    return files


def compute_runner_variables(
    context: RuntimeContext,
    gate_list: GateList,
    *,
    mode: str,
    release: bool,
    include_release_only: bool,
    labels: str,
    selected_labels: set[str],
) -> dict[str, list[str] | str]:
    needed = gate_list.runner_variables
    variables: dict[str, list[str] | str] = {
        "REPO_ROOT": str(context.repo_root),
        "SPECDOWN_OUTPUT_DIR": str(context.temp_dir / "specdown-report"),
        "DOC_DUPLICATES_OUTPUT": str(context.temp_dir / "doc-duplicates.json"),
        "SLOC_OUTPUT": str(context.temp_dir / "sloc-inventory.json"),
    }
    if "PYTEST_FLAGS" in needed:
        variables.update(
            _pytest_variables(
                context,
                mode=mode,
                release=release,
                include_release_only=include_release_only,
                selected_labels=selected_labels,
                needed=needed,
            )
        )
    elif "STANDING_PYTEST_TARGETS" in needed or "PYTEST_DEBUG_TEMPROOT" in needed:
        variables.update(
            _pytest_variables(
                context,
                mode=mode,
                release=release,
                include_release_only=include_release_only,
                selected_labels=selected_labels,
                needed=needed,
            )
        )
    if "CHANGED_LINE_BASE_SHA" in needed or "CRITIQUE_CHANGED_REF" in needed:
        variables.update(_git_variables(context))
    if {
        "PROVENANCE_CONTRACT_CHECKER",
        "RUN_QUALITY_RUNTIME_PROFILE",
        "release_changed_line_coverage_json",
    } & needed:
        variables.update(_file_variables(context))
    if "RUN_QUALITY_STATE_ROOT_ARGS" in needed:
        variables["RUN_QUALITY_STATE_ROOT_ARGS"] = list(context.state_args)
    if "seed_budget_args" in needed:
        values = ["--repo-root", str(context.repo_root)]
        if context.environment.get("CHARNESS_SEED_FIXTURE_ADVISORY", ""):
            values.append("--advisory-on-scan-failure")
        variables["seed_budget_args"] = values
    if "python_files" in needed:
        variables["python_files"] = _python_files(context)
    for name in needed:
        variables.setdefault(name, context.environment.get(name, ""))
    return variables


def substitute_command(
    command: tuple[str, ...], variables: dict[str, list[str] | str]
) -> list[str]:
    result: list[str] = []
    for token in command:
        array = _ARRAY_TOKEN.fullmatch(token)
        if array:
            value = variables.get(array.group(1))
            if not isinstance(value, list):
                raise RunnerError(
                    f"command references non-array runner variable {array.group(1)!r}"
                )
            result.extend(value)
            continue
        value_match = _VALUE_TOKEN.fullmatch(token)
        if value_match:
            value = variables.get(value_match.group(1))
            if value is None or isinstance(value, list):
                raise RunnerError(
                    f"command references unknown or array runner variable {value_match.group(1)!r}"
                )
            result.append(value)
            continue
        if "$" in token:
            raise RunnerError(f"unsupported variable token {token!r}; use $VAR or ${{VAR[@]}}")
        result.append(token)
    return result


def run_preamble(context: RuntimeContext, *, read_only: bool) -> int:
    """Refresh or verify the generated plugin mirror before quality gates.

    The shell wrapper deliberately does not source ``.githooks/runtime-env.sh``.
    ``prepare_runtime`` therefore supplies ``CHARNESS_RUNTIME_ROOT`` from the
    external cache when that source-only file is absent, which is the installed
    tree fallback.  The mirror preamble is enabled only for a declared packaging
    manifest whose resolved plugin root is gitignored; a consumer's unrelated
    ``plugins/`` directory is never a reason to delete or regenerate anything.
    In read-only mode validation generates into a temporary directory internally
    and compares bytes without mutating the checkout.
    """
    manifest_path = context.repo_root / "packaging" / "charness.json"
    if not manifest_path.is_file():
        return 0
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        relative_root = manifest["codex"]["repo_marketplace"]["materialized_source_path"]
        plugin_root = (context.repo_root / str(relative_root).removeprefix("./")).resolve()
        plugin_root.relative_to(context.repo_root.resolve())
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f"run-quality: could not resolve packaged plugin root: {exc}", file=os.sys.stderr)
        return 1
    relative_plugin_root = plugin_root.relative_to(context.repo_root.resolve()).as_posix()
    ignored = _probe(
        context,
        [
            "git",
            "check-ignore",
            "--no-index",
            "-q",
            "--",
            relative_plugin_root,
        ],
    )
    if ignored.returncode != 0:
        return 0
    command = [
        "python3",
        "scripts/validate_packaging.py" if read_only else "scripts/sync_root_plugin_manifests.py",
        "--repo-root",
        str(context.repo_root),
    ]
    if read_only:
        command.append("--validate-export")
    result = _probe(context, command)
    if result.returncode != 0:
        print("run-quality: plugin manifest preamble failed", file=os.sys.stderr)
        if result.stdout:
            print(result.stdout, end="", file=os.sys.stderr)
        if result.stderr:
            print(result.stderr, end="", file=os.sys.stderr)
        if read_only:
            print(
                "run-quality: regenerate with `python3 scripts/sync_root_plugin_manifests.py "
                f"--repo-root {context.repo_root}`",
                file=os.sys.stderr,
            )
    return result.returncode


def record_runtime_batch(context: RuntimeContext, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    import json

    batch = context.temp_dir / "runtime-batch.jsonl"
    batch.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    result = _probe(
        context,
        [
            "python3",
            "scripts/record_quality_runtime.py",
            "--repo-root",
            str(context.repo_root),
            *context.state_args,
            "--runtime-regime",
            context.regime,
            "--batch",
            str(batch),
        ],
    )
    if result.returncode != 0:
        print("run-quality: warning: failed to record phase runtimes.", file=os.sys.stderr)


def record_runtime_single(
    context: RuntimeContext, label: str, elapsed_ms: int, status: str, timestamp: str
) -> None:
    result = _probe(
        context,
        [
            "python3",
            "scripts/record_quality_runtime.py",
            "--repo-root",
            str(context.repo_root),
            *context.state_args,
            "--label",
            label,
            "--elapsed-ms",
            str(elapsed_ms),
            "--status",
            status,
            "--timestamp",
            timestamp,
        ],
    )
    if result.returncode != 0:
        print(
            f"run-quality: warning: failed to record aggregate runtime for {label}.",
            file=os.sys.stderr,
        )


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def close_runtime(context: RuntimeContext) -> None:
    shutil.rmtree(context.temp_dir, ignore_errors=True)
