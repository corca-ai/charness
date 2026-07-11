"""Execute slice-closeout commands with broad-pytest proof reuse."""
from __future__ import annotations

import subprocess
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
    stop_on_sync_drift: bool = False,
) -> bool:
    """Run commands, mutating ``payload``; return true when closeout should stop.

    When ``broad_pytest_producer`` is set, the broad pytest command is run
    through it (instrumented for plain mutation coverage) instead of the plain
    ``run_command``, and the proof-reuse path is bypassed so the producing run
    always executes — fresh coverage is the whole point of producer mode.
    """
    # The verification lock is the point at which generated output must stop
    # being discovered by an expensive proof run.  Snapshot only tracked git
    # state: an otherwise harmless untracked cache/temp file must not invalidate
    # the lock.  The snapshot is taken before any sync command and compared once
    # all sync commands have succeeded, immediately before the first verify.
    sync_state = (
        _tracked_state(repo_root)
        if stop_on_sync_drift and any(phase == "sync" for phase, _ in command_plan)
        else None
    )
    sync_completed = False
    for phase, command in command_plan:
        if phase != "sync" and sync_completed and sync_state is not None:
            current_state = _tracked_state(repo_root)
            if current_state != sync_state:
                drift_paths = sorted(
                    path
                    for path in set(sync_state) | set(current_state)
                    if sync_state.get(path) != current_state.get(path)
                )
                payload["status"] = "blocked"
                payload["sync_drift_paths"] = drift_paths
                payload["sync_drift"] = {
                    "phase": "sync",
                    "changed_paths": drift_paths,
                    "tracked_only": True,
                }
                payload["error"] = (
                    "sync phase changed tracked files before verification; commit the generated "
                    "sync output and rerun with --verification-lock"
                )
                return True
            # There is no need to probe again for later verify commands.
            sync_state = None

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
        if phase == "sync":
            sync_completed = True
        if is_broad:
            _record_broad(repo_root, payload, command, result, collect_changed_paths)
    return False


def _tracked_state(repo_root: Path) -> dict[str, tuple[bytes | None, bytes | None]]:
    """Return per-path worktree/index fingerprints, excluding untracked files."""

    def _git(*args: str) -> bytes:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            # A closeout that cannot inspect its tracked state must not silently
            # proceed into verification.  Keep the failure deterministic for the
            # caller; normal repositories have a resolvable HEAD here.
            raise RuntimeError(
                result.stderr.decode(errors="replace").strip()
                or result.stdout.decode(errors="replace").strip()
                or "git command failed while checking tracked sync drift"
            )
        return result.stdout

    dirty_paths: set[str] = set()
    for args in (
        ("diff", "--name-only", "-z", "--no-ext-diff", "--no-textconv", "HEAD", "--"),
        ("diff", "--name-only", "-z", "--no-ext-diff", "--no-textconv", "--cached", "--"),
    ):
        dirty_paths.update(
            raw_path.decode("utf-8", errors="surrogateescape")
            for raw_path in _git(*args).split(b"\0")
            if raw_path
        )

    state: dict[str, tuple[bytes, bytes]] = {}
    for path in dirty_paths:
        state[path] = (
            _git("diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD", "--", path),
            _git("diff", "--no-ext-diff", "--no-textconv", "--binary", "--cached", "--", path),
        )
    return state


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
            "cached broad pytest proof exists for a different locked diff fingerprint; "
            "this is expected after any file content, staged diff, or HEAD change "
            "since the cached proof. Inspect the changed files and rerun with "
            "--refresh-broad-pytest-proof only after the mutation set is final"
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
