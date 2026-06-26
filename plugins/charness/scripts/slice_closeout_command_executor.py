"""Execute slice-closeout commands with broad-pytest proof reuse."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from runtime_bootstrap import import_repo_module

_broad_gate = import_repo_module(__file__, "scripts.slice_closeout_broad_gate")


def execute_command_plan(
    repo_root: Path,
    command_plan: list[tuple[str, str]],
    payload: dict[str, object],
    *,
    run_command: Callable[[Path, str, str], dict[str, object]],
    collect_changed_paths: Callable[[Path], list[str]],
    refresh_broad_pytest_proof: bool,
    broad_pytest_producer: Callable[[Path, str, str], dict[str, object]] | None = None,
) -> bool:
    """Run commands, mutating ``payload``; return true when closeout should stop.

    When ``broad_pytest_producer`` is set, the broad pytest command is run
    through it (instrumented for plain mutation coverage) instead of the plain
    ``run_command``, and the proof-reuse path is bypassed so the producing run
    always executes — fresh coverage is the whole point of producer mode.
    """
    for phase, command in command_plan:
        is_broad = _broad_gate.is_broad_pytest_command(command)
        producing = is_broad and broad_pytest_producer is not None
        if is_broad and not producing:
            if _maybe_reuse_or_block_broad(
                repo_root,
                payload,
                command,
                collect_changed_paths=collect_changed_paths,
                refresh=refresh_broad_pytest_proof,
            ):
                continue
            if payload.get("status") == "blocked":
                return True
        if producing:
            result = broad_pytest_producer(repo_root, command, phase)
        else:
            result = run_command(repo_root, command, phase)
        payload["executed_commands"].append(result)
        if result["returncode"] != 0:
            payload["status"] = "failed"
            return True
        if is_broad:
            _record_broad(repo_root, payload, command, result, collect_changed_paths)
    return False


def _maybe_reuse_or_block_broad(
    repo_root: Path,
    payload: dict[str, object],
    command: str,
    *,
    collect_changed_paths: Callable[[Path], list[str]],
    refresh: bool,
) -> bool:
    current_paths = collect_changed_paths(repo_root)
    fingerprint = _broad_gate.broad_pytest_fingerprint(repo_root, current_paths)
    cache_report = _broad_gate.broad_pytest_cache_report(
        repo_root, command=command, fingerprint=fingerprint
    )
    if cache_report["status"] == "reusable" and not refresh:
        payload.setdefault("reused_broad_pytest_proofs", []).append(cache_report)
        payload["executed_commands"].append(
            {
                "phase": "verify",
                "command": command,
                "returncode": 0,
                "stdout": "",
                "stderr": "reused cached broad pytest proof\n",
                "cached": True,
            }
        )
        return True
    if cache_report["status"] == "invalidated" and not refresh:
        payload.setdefault("invalidated_broad_pytest_proofs", []).append(cache_report)
        payload["status"] = "blocked"
        payload["error"] = (
            "cached broad pytest proof exists for a different mutation fingerprint; "
            "inspect the changed files and rerun with --refresh-broad-pytest-proof "
            "only after the mutation set is final"
        )
    return False


def _record_broad(
    repo_root: Path,
    payload: dict[str, object],
    command: str,
    result: dict[str, object],
    collect_changed_paths: Callable[[Path], list[str]],
) -> None:
    current_paths = collect_changed_paths(repo_root)
    proof = _broad_gate.record_broad_pytest_proof(
        repo_root,
        command=command,
        fingerprint=_broad_gate.broad_pytest_fingerprint(repo_root, current_paths),
        elapsed_seconds=float(result.get("elapsed_seconds") or 0),
        changed_paths=current_paths,
    )
    payload.setdefault("recorded_broad_pytest_proofs", []).append(
        {
            "cache_path": ".charness/closeout/broad-pytest-proof.json",
            **proof,
            **(
                {"mutation_coverage_extra_pytest_targets": result["mutation_coverage_extra_pytest_targets"]}
                if result.get("mutation_coverage_extra_pytest_targets")
                else {}
            ),
        }
    )
