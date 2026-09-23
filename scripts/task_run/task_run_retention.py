"""Finished-lane worktree retention for task-run receipts.

A finished worktree is released only when its commit carries the whole
candidate; receipt and logs survive cleanup either way. Incomplete or
unknown content stays in the worktree with keep_worktree set, so the
runtime sweep preserves its only copy.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.gates_support.runtime_root_retention import _rmtree_writable  # noqa: E402
from scripts.task_run import task_run_changed_line as _changed_line  # noqa: E402

_candidate_has_work = _changed_line._candidate_has_work


def _apply_lane_retention(
    payload: dict[str, Any],
    candidate: Mapping[str, Any],
    *,
    result_state: str,
    resolved_repo: Path,
    resolved_target: Path,
    record_dir: Path,
    git: Callable[..., Any],
    persist: Callable[[dict[str, Any], Path], None],
    runtime_path: Path,
) -> None:
    retention = release_finished_lane(
        payload,
        resolved_repo=resolved_repo,
        resolved_target=resolved_target,
        record_dir=record_dir,
        git=git,
    )
    if retention is not None:
        payload["retention"] = retention
        payload["keep_worktree"] = retention.get("worktree") != "removed"
        if retention.get("worktree") == "removed":
            if retention.get("carrier"):
                payload["next_step"] = payload["next_step"].rstrip(".") + (
                    "; the lane worktree was released because that commit carries the whole candidate."
                )
            else:
                payload["next_step"] = payload["next_step"].rstrip(".") + (
                    "; the empty lane worktree was released because it carries nothing to consume."
                )
        persist(payload, runtime_path)
        return
    if result_state in {"completed", "validated-partial-result", "completed-needs-review", "failed"}:
        payload["keep_worktree"] = bool(
            _candidate_has_work(candidate) and not candidate.get("head_is_complete")
        )
        persist(payload, runtime_path)


def _empty_lane_removal(
    payload: Mapping[str, Any],
    candidate: Mapping[str, Any] | None,
    *,
    resolved_repo: Path,
    resolved_target: Path,
    record_dir: Path,
    git: Callable[..., Any],
) -> dict[str, Any] | None:
    """Remove a task worktree that holds no commits and no changes (#833).

    A failed, aborted, or no-op lane whose HEAD never moved past the base
    and whose tree is clean carries no result to consume, so it is released
    immediately instead of lingering as a registered worktree. Cleanliness
    is verified with an independent `git status`, never trusted from
    candidate metadata alone. Commits, changed or disallowed paths, dirty
    trees, and unobservable state keep the existing retention path.
    """
    base_sha = payload.get("base_sha")
    if not isinstance(base_sha, str) or not base_sha:
        return None
    try:
        head_sha = git(resolved_target, "rev-parse", "HEAD").stdout.strip()
        status = git(resolved_target, "status", "--porcelain")
    except (OSError, ValueError, TypeError, AttributeError):
        return None
    if head_sha != base_sha:
        return None
    if status.returncode != 0 or status.stdout.strip():
        return None
    if isinstance(candidate, Mapping) and (
        candidate.get("changed_paths") or candidate.get("disallowed_paths")
    ):
        return None
    retention: dict[str, Any] = {"worktree": "retained", "runtime": "retained"}
    removal = git(resolved_repo, "worktree", "remove", "--force", str(resolved_target))
    if removal.returncode != 0:
        retention["reason"] = f"git worktree remove failed: {removal.stderr.strip()[-300:]}"
        return retention
    retention["worktree"] = "removed"
    runtime_dir = record_dir / "runtime"
    if runtime_dir.is_dir():
        try:
            _rmtree_writable(runtime_dir)
            retention["runtime"] = "removed"
        except OSError as exc:
            retention["reason"] = f"runtime removal failed: {exc}"
    else:
        retention["runtime"] = "absent"
    retention.setdefault(
        "reason",
        "empty lane: no commits beyond the base and a clean tree; nothing to consume",
    )
    retention["kept"] = ["result.json", *sorted(p.name for p in record_dir.glob("*.log"))]
    return retention


def release_finished_lane(
    payload: Mapping[str, Any],
    *,
    resolved_repo: Path,
    resolved_target: Path,
    record_dir: Path,
    git: Callable[..., Any],
) -> dict[str, Any] | None:
    """Release a finished worktree only when its commit carries the whole candidate.

    Receipt and logs survive cleanup. Incomplete or unknown content stays in the
    worktree with keep_worktree set, so the runtime sweep preserves its only copy.
    """
    candidate = payload.get("candidate")
    empty = _empty_lane_removal(
        payload,
        candidate if isinstance(candidate, Mapping) else None,
        resolved_repo=resolved_repo,
        resolved_target=resolved_target,
        record_dir=record_dir,
        git=git,
    )
    if empty is not None:
        return empty
    if not isinstance(candidate, Mapping) or payload.get("status") not in {
        "completed",
        "validated-partial-result",
        "completed-needs-review",
    }:
        return None
    if not candidate.get("head_is_complete") or candidate.get("carrier_kind") != "commit-only":
        return {
            "worktree": "retained",
            "runtime": "retained",
            "reason": (
                f"carrier {candidate.get('carrier_kind')!r} is not carried whole by lane HEAD; "
                "keep_worktree stays true so the sweep cannot delete the named copy"
            ),
        }
    # A complete commit is not enough for a changed candidate.  The changed-line
    # gate is the proof that the commit is safe to release, and a missing or
    # skipped gate must leave the named worktree available for an explicit retry.
    # No-change lanes have no changed lines to prove and retain the historical
    # cheap release path.
    if _candidate_has_work(candidate):
        gate = payload.get("changed_line_gate")
        proof_status = gate.get("proof_status") if isinstance(gate, Mapping) else None
        if proof_status is None and isinstance(gate, Mapping):
            proof_status = gate.get("status")
        if (
            not isinstance(gate, Mapping)
            or proof_status not in {"clean", "noop"}
            or gate.get("blocking")
        ):
            return {
                "worktree": "retained",
                "runtime": "retained",
                "reason": (
                    "changed-line proof is absent or not clean/noop; keep_worktree stays true "
                    "until the candidate is re-observed after a passing gate"
                ),
            }
    retention: dict[str, Any] = {"worktree": "retained", "runtime": "retained"}
    removal = git(resolved_repo, "worktree", "remove", "--force", str(resolved_target))
    if removal.returncode != 0:
        retention["reason"] = f"git worktree remove failed: {removal.stderr.strip()[-300:]}"
        return retention
    retention["worktree"] = "removed"
    runtime_dir = record_dir / "runtime"
    if runtime_dir.is_dir():
        try:
            _rmtree_writable(runtime_dir)
            retention["runtime"] = "removed"
        except OSError as exc:
            retention["reason"] = f"runtime removal failed: {exc}"
    else:
        retention["runtime"] = "absent"
    retention["carrier"] = f"{payload.get('target_branch')}@{payload.get('target_sha')}"
    retention["kept"] = ["result.json", *sorted(p.name for p in record_dir.glob("*.log"))]
    return retention
