"""Finalize task-run receipts from execution and completion evidence."""

from __future__ import annotations

import sys
import time
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
from scripts.task_run.task_run_contract import TaskRunError  # noqa: E402
from scripts.task_run.task_run_git import (  # noqa: E402
    PERSIST_CANDIDATE_COMMIT_MESSAGE,
    _candidate_carrier,
    _commit_lane_snapshot,
)


def complete_task(
    payload: dict[str, Any],
    *,
    runtime_path: Path,
    resolved_target: Path,
    resolved_repo: Path,
    before_exec: dict[str, list[str]],
    base_sha: str,
    scope_specs: list[dict[str, Any]],
    require_change: bool,
    parent_before: dict[str, list[str]],
    parent_before_head: str,
    stdout_log: Path,
    execution: dict[str, Any],
    started_at: float,
    persist: Callable[[dict[str, Any], Path], None],
    result_delivery: Callable[[Path], dict[str, Any]],
    completion_evidence: Callable[..., tuple[dict[str, Any], dict[str, Any], dict[str, Any]]],
    execution_state: Callable[[dict[str, Any], dict[str, Any]], str],
    candidate_result_state: Callable[..., tuple[dict[str, Any], str]],
    candidate_commit: dict[str, Any] | None,
    git: Callable[..., Any],
    git_output: Callable[..., str],
    pass_value: str,
    target_head: str | None = None,
    changed_line_gate: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    delivery = result_delivery(stdout_log)
    evidence, scope, parent_progress = completion_evidence(
        target_path=resolved_target,
        parent_root=resolved_repo,
        before_exec=before_exec,
        base_sha=base_sha,
        scope_specs=scope_specs,
        require_change=require_change,
        parent_before=parent_before,
        parent_before_head=parent_before_head,
        target_head=target_head,
    )
    carrier = scope.get("candidate_carrier", {})
    observed_head = carrier.get("observed_head_sha") if isinstance(carrier, Mapping) else None
    target_branch = carrier.get("observed_branch") if isinstance(carrier, Mapping) else None
    if target_branch is None and not observed_head:
        branch_result = git(resolved_target, "symbolic-ref", "--quiet", "--short", "HEAD")
        target_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    target_sha = observed_head or git_output(resolved_target, "rev-parse", "HEAD").strip()
    payload.update(
        {
            "phase": "terminal",
            "execution": execution,
            "result_delivery": delivery,
            "duration_ms": int((time.monotonic() - started_at) * 1000),
            "target_sha": target_sha,
            "target_branch": target_branch,
            **evidence,
        }
    )
    structured = delivery.get("structured")
    if (
        isinstance(structured, Mapping)
        and structured.get("schema_version") == "charness.reviewer_lifecycle.v1"
    ):
        payload["reviewer_lifecycle"] = structured

    execution_status = execution_state(execution, delivery)
    payload["execution"]["status"] = execution_status
    candidate, result_state = candidate_result_state(
        execution_state=execution_status,
        scope=scope,
        parent_progress=parent_progress,
        candidate_commit=candidate_commit,
    )
    payload["candidate"] = candidate

    blockers = _completion_blockers(
        execution_status=execution_status,
        scope=scope,
        parent_progress=parent_progress,
        pass_value=pass_value,
    )
    gate, blockers, result_state = _prove_ready_candidate(
        payload,
        candidate,
        blockers=blockers,
        result_state=result_state,
        execution_status=execution_status,
        resolved_target=resolved_target,
        base_sha=base_sha,
        stdout_log=stdout_log,
        changed_line_gate=changed_line_gate,
        git=git,
        git_output=git_output,
    )
    payload["changed_line_gate"] = gate

    payload["status"] = result_state
    payload["approval_eligibility"] = (
        "eligible" if result_state == "completed" and not blockers else "ineligible"
    )

    warnings = [
        f"{population}: {data['reason']}"
        for population, data in evidence["populations"].items()
        if data.get("verdict") == "warn"
    ]
    if parent_progress["classification"] == "concurrent-parent-progress":
        warnings.append("parent made disjoint progress while the task ran")
    if warnings:
        payload["warnings"] = warnings

    payload["next_step"] = _next_step(
        payload,
        resolved_target=resolved_target,
        candidate=candidate,
        execution_status=execution_status,
        result_state=result_state,
        blockers=blockers,
    )
    persist(payload, runtime_path)
    _apply_lane_retention(
        payload,
        candidate,
        result_state=result_state,
        resolved_repo=resolved_repo,
        resolved_target=resolved_target,
        record_dir=stdout_log.parent,
        git=git,
        persist=persist,
        runtime_path=runtime_path,
    )
    print(f"task run: {payload['status']} ({payload['task_id']})", file=sys.stderr)
    return payload


def _completion_blockers(
    *,
    execution_status: str,
    scope: Mapping[str, Any],
    parent_progress: Mapping[str, Any],
    pass_value: str,
) -> list[str]:
    blockers = [f"execution: {execution_status}"] if execution_status != "completed" else []
    if scope["verdict"] != pass_value:
        blockers.append(str(scope["reason"]))
    if parent_progress["blocking"]:
        blockers.append("parent changed within the resolved candidate scope")
    return blockers


def _prove_ready_candidate(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    *,
    blockers: list[str],
    result_state: str,
    execution_status: str,
    resolved_target: Path,
    base_sha: str,
    stdout_log: Path,
    changed_line_gate: Callable[..., dict[str, Any]] | None,
    git: Callable[..., Any],
    git_output: Callable[..., str],
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

    if blockers and result_state == "completed" and candidate.get("useful"):
        result_state = "validated-partial-result"
    return gate, blockers, result_state


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
    if (
        execution_status != "completed"
        or not _candidate_has_work(candidate)
    ):
        return None
    if _carrier_is_complete(candidate):
        return None
    snapshot = persist_incomplete_candidate(
        resolved_target, git=git, git_output=git_output
    )
    candidate["persist"] = snapshot
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


def _candidate_has_work(candidate: Mapping[str, Any]) -> bool:
    """Whether a completed candidate has bytes worth preserving, even if invalid."""
    return bool(candidate.get("useful") or candidate.get("changed_paths"))


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
    """Make retention fail closed after a carrier read cannot establish state."""
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


def _next_step(
    payload: Mapping[str, Any],
    *,
    resolved_target: Path,
    candidate: Mapping[str, Any],
    execution_status: str,
    result_state: str,
    blockers: list[str],
) -> str:
    location = _candidate_location(payload, resolved_target, candidate)
    if execution_status == "timed-out":
        suffix = f"; {'; '.join(blockers)}." if blockers else "."
        return (
            f"Review the committed WIP candidate in {resolved_target}; "
            "interrupted mid-edit — state unknown; the commit is not a correctness claim"
            + suffix
        )
    if blockers:
        return (
            f"Inspect the retained candidate {location}, typed result, and captured logs; "
            + "; ".join(blockers)
            + "."
        )
    if result_state == "validated-partial-result":
        return (
            f"Review the validated candidate {location}; "
            "it is useful but not approval-eligible."
        )
    return f"Review the candidate {location}; the typed result is approval-eligible."


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
            payload["next_step"] = payload["next_step"].rstrip(".") + (
                "; the lane worktree was released because that commit carries the whole candidate."
            )
        persist(payload, runtime_path)
        return
    if result_state in {"completed", "validated-partial-result", "failed"}:
        payload["keep_worktree"] = bool(
            _candidate_has_work(candidate) and not candidate.get("head_is_complete")
        )
        persist(payload, runtime_path)


def persist_incomplete_candidate(
    worktree: Path,
    *,
    git: Callable[..., Any],
    git_output: Callable[..., str],
) -> dict[str, Any]:
    """Copy a useful dirty candidate onto the lane branch so HEAD carries it (#797)."""
    try:
        return _commit_lane_snapshot(
            worktree,
            message=PERSIST_CANDIDATE_COMMIT_MESSAGE,
            git=git,
            git_output=git_output,
        )
    except (OSError, TaskRunError, TypeError, AttributeError, ValueError) as exc:
        return {"status": "failed", "error": str(exc), "correctness_verified": False}


def _candidate_location(
    payload: Mapping[str, Any], resolved_target: Path, candidate: Mapping[str, Any]
) -> str:
    if candidate.get("head_is_complete") and payload.get("target_branch") and payload.get("target_sha"):
        return f"on branch {payload['target_branch']} at {payload['target_sha']}"
    return f"in {resolved_target}"


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
    if not isinstance(candidate, Mapping) or payload.get("status") not in {
        "completed",
        "validated-partial-result",
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


def _changed_line_verdict(
    changed_line_gate: Callable[..., dict[str, Any]] | None,
    *,
    execution_status: str,
    candidate: Mapping[str, Any],
    worktree: Path,
    base_sha: str,
    log_dir: Path,
    skip_reason: str | None = None,
) -> dict[str, Any]:
    """Run the gate for a validated candidate; otherwise say why it did not run."""
    if changed_line_gate is None:
        return {
            "status": "not-run",
            "blocking": False,
            "reason": "no changed-line gate was supplied to completion",
            "summary": "changed-line gate not run: none supplied",
        }
    if skip_reason:
        return {
            "status": "skipped",
            "blocking": False,
            "reason": skip_reason,
            "summary": f"changed-line gate skipped: {skip_reason}",
        }
    if execution_status != "completed" or not candidate.get("useful"):
        reason = (
            f"execution ended {execution_status} with candidate status "
            f"{candidate.get('status')!r}; there is no validated candidate to judge"
        )
        return {
            "status": "skipped",
            "blocking": False,
            "reason": reason,
            "summary": f"changed-line gate skipped: {reason}",
        }
    return changed_line_gate(worktree, base_sha=base_sha, log_dir=log_dir)
