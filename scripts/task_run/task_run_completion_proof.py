"""Persistence, proof, and final carrier readback for task completion."""

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

from scripts.task_run import task_run_changed_line as _changed_line  # noqa: E402
from scripts.task_run import task_run_lane_runner as _lane_runner  # noqa: E402
from scripts.task_run import task_run_prelaunch as _prelaunch  # noqa: E402
from scripts.task_run import task_run_scope as _scope  # noqa: E402
from scripts.task_run.task_run_carrier import _candidate_carrier  # noqa: E402
from scripts.task_run.task_run_contract import TaskRunError  # noqa: E402


def _prove_ready_candidate(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    *,
    blockers: list[str],
    scope: dict[str, Any],
    result_state: str,
    execution_status: str,
    resolved_target: Path,
    base_sha: str,
    stdout_log: Path,
    changed_line_gate: Callable[..., dict[str, Any]] | None,
    git: Callable[..., Any],
    git_output: Callable[..., str],
    pass_value: str,
) -> tuple[dict[str, Any], list[str], str]:
    """Preserve, prove, and re-observe a candidate before returning its state."""
    carrier_reason = _persist_useful_dirty_candidate(
        payload,
        candidate,
        resolved_target=resolved_target,
        base_sha=base_sha,
        execution_status=execution_status,
        git=git,
        git_output=git_output,
    )
    if carrier_reason:
        blockers.append(carrier_reason)

    persistence = candidate.get("persist")
    if isinstance(persistence, Mapping) and persistence.get("status") == "committed":
        _reclassify_persisted_candidate(
            payload,
            candidate,
            scope,
            blockers,
            resolved_target=resolved_target,
            base_sha=base_sha,
            pass_value=pass_value,
        )

    proof_ready = not blockers and _carrier_is_complete(candidate) and bool(candidate.get("useful"))

    admitted = _carrier_identity(candidate)
    gate = _changed_line_verdict(
        changed_line_gate,
        execution_status=execution_status,
        candidate=candidate,
        worktree=resolved_target,
        base_sha=base_sha,
        log_dir=stdout_log.parent,
        skip_reason=("; ".join(blockers) if blockers else None),
    )
    gate, unmapped_blocker = _changed_line.block_unmapped_pool_files(gate)
    blockers.extend([unmapped_blocker] if unmapped_blocker else [])
    if gate.get("blocking"):
        blockers.append(str(gate.get("summary") or "changed-line gate refused the candidate"))

    if proof_ready and changed_line_gate is not None:
        post_gate_reason = _refresh_after_gate(
            payload,
            candidate,
            resolved_target=resolved_target,
            base_sha=base_sha,
            admitted=admitted,
        )
        if post_gate_reason:
            blockers.append(post_gate_reason)

    _reconcile_persisted_blockers(payload, candidate, blockers, resolved_target)

    if blockers and result_state == "completed" and candidate.get("useful"):
        result_state = "validated-partial-result"
    return gate, blockers, result_state


def _reclassify_persisted_candidate(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    scope: dict[str, Any],
    blockers: list[str],
    *,
    resolved_target: Path,
    base_sha: str,
    pass_value: str,
) -> None:
    """Re-run scope and acceptance classification on the persisted carrier."""
    specs = scope.get("specs")
    if not isinstance(specs, list):
        return
    refreshed_scope = _scope._scope_result(
        resolved_target,
        base_sha,
        specs,
        bool(scope.get("require_change")),
        head=str(payload.get("target_sha") or "") or None,
        branch=str(payload.get("target_branch") or "") or None,
    )
    carrier = refreshed_scope.get("candidate_carrier")
    if isinstance(carrier, Mapping):
        candidate.update(carrier)
    candidate["disallowed_paths"] = list(refreshed_scope.get("disallowed_paths") or [])
    scope.clear()
    scope.update(refreshed_scope)
    payload["scope"] = scope

    if scope.get("verdict") != pass_value:
        reason = str(scope.get("reason") or "persisted candidate failed scope classification")
        if reason not in blockers:
            blockers.append(reason)
    for blocker in _prelaunch.acceptance_deficit_blockers(payload, resolved_target, candidate):
        if blocker not in blockers:
            blockers.append(blocker)


def _reconcile_persisted_blockers(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    blockers: list[str],
    resolved_target: Path,
) -> None:
    """Name an intentional recovery commit beside pre-persist blockers (#823).

    Persistence, correctness, and approval are separate facts: a commit the
    persistence path writes after blockers were already reported is preserved
    for review, not a correctness or approval claim. Without this entry the
    lane agent's (executor's) pre-persist declaration (e.g. "staged but
    uncommitted") stands beside the persisted commit as a contradiction no
    caller can resolve. Clean persists (no blockers) record nothing.
    """
    persist = candidate.get("persist")
    if not isinstance(persist, dict) or persist.get("status") != "committed":
        return
    if not blockers or persist.get("after_block"):
        return
    persist["after_block"] = True
    sha = persist.get("sha") or payload.get("target_sha")
    where = payload.get("target_branch") or str(resolved_target)
    blockers.append(
        f"candidate persisted after blockers were reported as {sha} on {where}"
    )


def _persist_useful_dirty_candidate(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    *,
    resolved_target: Path,
    base_sha: str,
    execution_status: str,
    git: Callable[..., Any],
    git_output: Callable[..., str],
) -> str | None:
    """Make a useful completed candidate durable and observe its carrier again."""
    if execution_status != "completed" or not _candidate_has_work(candidate):
        return None
    if _carrier_is_complete(candidate):
        return None
    allowed = _lane_runner._in_scope_candidate_paths(candidate)
    if allowed is None:
        candidate["persist"] = {
            "status": "skipped",
            "reason": "candidate classification unavailable",
            "changed_paths": [],
            "correctness_verified": False,
        }
        return (
            "candidate persistence skipped: no usable scope classification; refusing the "
            "unscoped stage-everything shape"
        )
    snapshot = _lane_runner.persist_incomplete_candidate(
        resolved_target,
        paths=allowed,
        git=git,
        git_output=git_output,
    )
    candidate["persist"] = snapshot
    if snapshot.get("status") == "skipped":
        return (
            "candidate persistence skipped: no in-scope changes to carry on the lane branch; "
            "lane residue stays in the worktree"
        )
    if snapshot.get("status") != "committed":
        detail = snapshot.get("error") or "the lane snapshot was not committed"
        return f"candidate persistence failed: {detail}"
    payload["target_sha"] = str(snapshot["sha"])
    try:
        observed = _candidate_carrier(
            resolved_target,
            base_sha,
            head=str(snapshot["sha"]),
            branch=payload.get("target_branch"),
        )
    except (OSError, RuntimeError, TaskRunError, TypeError, AttributeError, ValueError) as exc:
        _mark_carrier_unreadable(candidate, phase="after persistence", error=exc)
        return f"candidate carrier could not be observed after persistence: {exc}"
    candidate.update(observed)
    if not _carrier_is_complete(candidate):
        return _carrier_not_ready_reason(candidate, phase="after persistence")
    return None


_candidate_has_work = _changed_line._candidate_has_work


def _carrier_is_complete(carrier: Mapping[str, Any]) -> bool:
    return bool(
        carrier.get("carrier_kind") == "commit-only"
        and carrier.get("head_is_complete") is True
        and carrier.get("dirty_paths") == []
        and carrier.get("observed_head_sha")
        and carrier.get("content_digest")
    )


def _carrier_identity(carrier: Mapping[str, Any]) -> tuple[Any, Any]:
    return carrier.get("observed_head_sha"), carrier.get("content_digest")


def _carrier_not_ready_reason(
    carrier: Mapping[str, Any], *, phase: str = "before proof"
) -> str:
    return (
        f"candidate carrier is incomplete {phase} ({carrier.get('carrier_kind')!r}); "
        "changed-line proof was skipped"
    )


def _mark_carrier_unreadable(candidate: dict[str, Any], *, phase: str, error: Exception) -> None:
    """Make retention fail closed after a candidate-carrier read cannot establish state."""
    candidate["carrier_observation"] = {"status": "unreadable", "phase": phase, "error": str(error)}
    candidate.update(carrier_kind="unknown", head_is_complete=False, state_known=False)


def _refresh_after_gate(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    *,
    resolved_target: Path,
    base_sha: str,
    admitted: tuple[Any, Any],
) -> str | None:
    try:
        observed = _candidate_carrier(resolved_target, base_sha)
    except (OSError, RuntimeError, TaskRunError, TypeError, AttributeError, ValueError) as exc:
        _mark_carrier_unreadable(candidate, phase="after changed-line gate", error=exc)
        return f"candidate carrier could not be observed after changed-line proof: {exc}"
    candidate.update(observed)
    if observed.get("observed_head_sha"):
        payload["target_sha"] = observed["observed_head_sha"]
    if not _carrier_is_complete(observed) or _carrier_identity(observed) != admitted:
        return (
            "candidate carrier changed after changed-line proof; approval was denied "
            "and gate-created work was not committed"
        )
    return None


_changed_line_verdict = _changed_line._changed_line_verdict
