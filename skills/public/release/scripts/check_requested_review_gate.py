#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.subprocess_guard"
).run_process
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)
load_adapter = _resolve_adapter.load_adapter
REQUESTED_REVIEW_TIMEOUT_SECONDS = 300


def _contains_any(text: str, patterns: list[str]) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in patterns if pattern.lower() in lowered]


def _run_review_commands(repo_root: Path, commands: list[str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for command in commands:
        result = run_process(
            command,
            cwd=repo_root,
            shell=True,
            executable="/bin/bash",
            timeout_seconds=REQUESTED_REVIEW_TIMEOUT_SECONDS,
        )
        results.append(
            {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "ok": result.returncode == 0,
            }
        )
    return results


def build_payload(
    repo_root: Path, *, artifact_path: Path | None = None, run_commands: bool = True
) -> dict[str, Any]:
    # GUARDED AT THE READ SITE, not at `main()`. Three entrypoints reach this function:
    # its own CLI, and `plan_release_run` and `publish_release_cli`, which both import it.
    #
    # A round-1 bounded review REFUTED the harm claim this comment used to carry ("a
    # refusal in `main()` would leave two of them reading charness defaults") and it is
    # corrected rather than quietly dropped. Under an unhonored declaration `adapter`
    # is `valid: false`, and both importers already stop on that: `publish_release_cli`
    # at `_valid_adapter_data`, whose docstring calls itself "the one place an invalid
    # release adapter stops a run", and `plan_release_run` behind `if
    # adapter.get("valid")`. So the count of importers measured to reach a charness
    # default here is ZERO, not two. The read-site placement buys POSITIONAL
    # INDEPENDENCE -- the refusal is a property of this function rather than of two
    # callers' validity gates staying where they are -- which is a real property and a
    # smaller claim than the one it replaces.
    #
    # WHAT IT COSTS TO BE UNGUARDED, measured on the real CLI rather than argued: with
    # `version: 9` and a declared `requested_review_commands`, this gate printed
    # `configuration status: not_configured` and `requested_review_commands is empty;
    # requested-review enforcement is advisory-only for this release`, exit 0. The repo
    # declared a command; the gate reported the OPPOSITE of what the repo said.
    #
    # A round-1 bounded review deleted the second half of that narrative, which used to
    # add "and a `block-if-unconfigured` policy ... downgraded its own enforcement to
    # advisory". `block-if-unconfigured` is not a value this schema accepts -- see
    # `resolve_adapter`, which validates against exactly `{warn-if-unconfigured,
    # advisory-only}` -- so that clause described a configuration no repo can hold. The
    # measured half is the whole finding.
    #
    # Falling back to a charness default here is not the conservative arm -- it is a
    # charness-chosen answer wearing the repo's name, on the surface that gates a publish.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="release-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    resolved_artifact = artifact_path or (repo_root / adapter["artifact_path"])
    patterns = list(data.get("review_unavailable_patterns", []))
    waiver_phrases = list(data.get("review_waiver_phrases", []))
    commands = list(data.get("requested_review_commands", []))
    policy = str(
        data.get("requested_review_policy", "warn-if-unconfigured") or "warn-if-unconfigured"
    )
    artifact_text = (
        resolved_artifact.read_text(encoding="utf-8", errors="replace")
        if resolved_artifact.is_file()
        else ""
    )
    unavailable_hits = _contains_any(artifact_text, patterns) if artifact_text else []
    waiver_hits = _contains_any(artifact_text, waiver_phrases) if artifact_text else []
    command_results = _run_review_commands(repo_root, commands) if run_commands else []
    failed_commands = [item for item in command_results if item.get("ok") is not True]
    blockers: list[str] = []
    warnings: list[str] = []
    configuration_status = (
        "configured"
        if commands
        else ("advisory_only" if policy == "advisory-only" else "not_configured")
    )
    if not commands and policy != "advisory-only":
        warnings.append(
            "requested_review_commands is empty; requested-review enforcement is advisory-only for this release."
        )
    if unavailable_hits and not waiver_hits:
        blockers.append(
            "release artifact records requested review unavailability without an explicit review waiver: "
            + ", ".join(unavailable_hits)
        )
    for item in failed_commands:
        blockers.append(f"requested review command failed ({item['exit_code']}): {item['command']}")
    status = "blocked" if blockers else "ok"
    if unavailable_hits and waiver_hits and not failed_commands:
        status = "waived"
    return {
        "status": status,
        "artifact_path": str(resolved_artifact.relative_to(repo_root))
        if resolved_artifact.is_relative_to(repo_root)
        else str(resolved_artifact),
        "artifact_exists": resolved_artifact.is_file(),
        "unavailable_hits": unavailable_hits,
        "waiver_hits": waiver_hits,
        "requested_review_commands": commands,
        "requested_review_policy": policy,
        "configuration_status": configuration_status,
        "command_results": command_results,
        "blockers": blockers,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root used to resolve the release adapter",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        help="Release artifact file to scan for review waiver/unavailability phrases",
    )
    parser.add_argument(
        "--skip-commands",
        action="store_true",
        help="Skip executing the configured requested_review_commands",
    )
    parser.add_argument(
        "--detail", action="store_true", help="Emit the full review-gate payload as YAML"
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    artifact_path = args.artifact.resolve() if args.artifact else None
    payload = build_payload(
        repo_root, artifact_path=artifact_path, run_commands=not args.skip_commands
    )
    if args.detail:
        yaml_output.emit_yaml(payload)
    elif payload["status"] == "blocked":
        for blocker in payload["blockers"]:
            print(f"BLOCKED: {blocker}")
    else:
        print(f"requested release review gate: {payload['status']}")
        print(f"configuration status: {payload['configuration_status']}")
        for warning in payload.get("warnings", []):
            print(f"WARNING: {warning}")
    return 1 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
