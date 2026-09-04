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

    blockers: list[str] = []
    if execution_status != "completed":
        blockers.append(f"execution: {execution_status}")
    if scope["verdict"] != pass_value:
        blockers.append(scope["reason"])
    if parent_progress["blocking"]:
        blockers.append("parent changed within the resolved candidate scope")

    # The changed-line gate runs where the claim is made. A lane whose candidate
    # the pre-push hook would refuse is useful but not done: the receipt says
    # `validated-partial-result`, names the unproven line, and the parent reads
    # at the receipt what it used to learn at the fourth refused push.
    gate = _changed_line_verdict(
        changed_line_gate,
        execution_status=execution_status,
        candidate=candidate,
        worktree=resolved_target,
        base_sha=base_sha,
        log_dir=stdout_log.parent,
    )
    payload["changed_line_gate"] = gate
    if gate.get("blocking"):
        blockers.append(str(gate.get("summary") or "changed-line gate refused the candidate"))
        if result_state == "completed":
            result_state = "validated-partial-result"

    payload["status"] = result_state
    payload["approval_eligibility"] = "eligible" if result_state == "completed" else "ineligible"
    _persist_useful_dirty_candidate(
        payload,
        candidate,
        resolved_target=resolved_target,
        base_sha=base_sha,
        execution_status=execution_status,
        git=git,
        git_output=git_output,
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


def _persist_useful_dirty_candidate(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    *,
    resolved_target: Path,
    base_sha: str,
    execution_status: str,
    git: Callable[..., Any],
    git_output: Callable[..., str],
) -> None:
    if (
        execution_status != "completed"
        or not candidate.get("useful")
        or candidate.get("head_is_complete")
    ):
        return
    snapshot = persist_incomplete_candidate(
        resolved_target, git=git, git_output=git_output
    )
    candidate["persist"] = snapshot
    if snapshot.get("status") != "committed":
        return
    payload["target_sha"] = str(snapshot["sha"])
    try:
        candidate.update(
            _candidate_carrier(
                resolved_target,
                base_sha,
                head=str(snapshot["sha"]),
                branch=payload.get("target_branch"),
            )
        )
    except (OSError, TaskRunError, TypeError, ValueError):
        candidate["head_sha"] = snapshot["sha"]
        candidate["carrier_kind"] = "commit-only"
        candidate["head_is_complete"] = True
        candidate["dirty_paths"] = []


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
            candidate.get("useful") and not candidate.get("head_is_complete")
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
    """Drop a finished lane to `result.json` plus logs when its commit carries everything.

    A finished lane kept a 1.4 GB worktree and a 1.1 GB runtime beside a 60 KB
    receipt, 254 times over, and no rule reached them (#787). The candidate a
    parent integrates is the lane branch's commit; once `head_is_complete` says
    that commit IS the candidate, the worktree adds nothing the branch does not
    hold. A useful incomplete candidate is committed onto the lane branch first
    (#797); if that persist fails, the worktree stays and `keep_worktree` stays
    true so the sweep cannot delete the only copy.
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
) -> dict[str, Any]:
    """Run the gate for a validated candidate; otherwise say why it did not run."""
    if changed_line_gate is None:
        return {
            "status": "not-run",
            "blocking": False,
            "reason": "no changed-line gate was supplied to completion",
            "summary": "changed-line gate not run: none supplied",
        }
    if execution_status != "completed" or not candidate.get("useful"):
        return {
            "status": "skipped",
            "blocking": False,
            "reason": (
                f"execution ended {execution_status} with candidate status "
                f"{candidate.get('status')!r}; there is no validated candidate to judge"
            ),
            "summary": "changed-line gate skipped: no validated candidate",
        }
    return changed_line_gate(worktree, base_sha=base_sha, log_dir=log_dir)
