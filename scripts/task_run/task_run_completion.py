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

from scripts.task_run import task_run_changed_line as _changed_line  # noqa: E402
from scripts.task_run import task_run_lane_runner as _lane_runner  # noqa: E402
from scripts.task_run import task_run_persistence as _persistence  # noqa: E402
from scripts.task_run import task_run_prelaunch as _prelaunch  # noqa: E402
from scripts.task_run import task_run_progress as _progress  # noqa: E402
from scripts.task_run import task_run_retention as _retention  # noqa: E402
from scripts.task_run import task_run_evidence as _evidence  # noqa: E402
from scripts.task_run import task_run_ledger as _ledger  # noqa: E402
from scripts.task_run import task_run_execution as _execution, task_run_state as _state  # noqa: E402
from scripts.task_run.task_run_completion_next_step import _next_step  # noqa: E402
from scripts.task_run.task_run_contract import TaskRunError  # noqa: E402
from scripts.task_run.task_run_git import _candidate_carrier  # noqa: E402


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
    report_only: bool = False,
    parent_before: dict[str, list[str]],
    parent_before_head: str,
    stdout_log: Path,
    stderr_log: Path | None = None,
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
    try:
        delivery = result_delivery(stdout_log)
    except Exception as exc:  # noqa: BLE001 - delivery is diagnostic, completion must persist
        delivery = {
            "status": "non-delivery",
            "bytes": None,
            "truncated": False,
            "text": "",
            "log": str(stdout_log),
            "structured_status": "unavailable",
            "delivery_error": str(exc),
            "delivery_error_type": type(exc).__name__,
        }
    _evidence._write_full_report(delivery, stdout_log.with_name("full-report.log"))
    evidence, scope, parent_progress = completion_evidence(
        target_path=resolved_target,
        parent_root=resolved_repo,
        before_exec=before_exec,
        base_sha=base_sha,
        scope_specs=scope_specs,
        require_change=require_change,
        report_only=report_only,
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
    reviewer_result = _execution_reviewer_result(delivery)
    if reviewer_result is not None:
        reviewer_result["task_id"] = payload.get("task_id")
        reviewer_result["task_result_path"] = str(runtime_path)
        payload["reviewer_result"] = reviewer_result
    structured = delivery.get("structured")
    if (
        isinstance(structured, Mapping)
        and structured.get("schema_version") == "charness.reviewer_lifecycle.v1"
    ):
        payload["reviewer_lifecycle"] = structured

    execution_status = execution_state(execution, delivery)
    payload["execution"]["status"] = execution_status
    acceptance_skeleton = _prelaunch.finish_acceptance_skeleton(payload, resolved_target) if execution_status == "completed" else None
    stderr_text = _progress._lane_stderr_text(stdout_log, stderr_log)
    payload["failure"] = _state.classify_failure(execution, stderr_text=stderr_text, delivery=delivery)
    candidate, result_state = candidate_result_state(
        execution_state=execution_status,
        scope=scope,
        parent_progress=parent_progress,
        candidate_commit=candidate_commit,
    )
    payload["candidate"] = candidate
    payload["persistence"] = _persistence.scan_persistence_risks(
        resolved_target, base_sha, candidate.get("changed_paths") or [], git=git
    )
    payload["self_review"] = _execution.run_self_review(payload)

    blockers = _completion_blockers(
        execution_status=execution_status,
        scope=scope,
        parent_progress=parent_progress,
        pass_value=pass_value,
        delivery=delivery,
        report_only=report_only,
        persistence=payload["persistence"],
        acceptance_skeleton=acceptance_skeleton,
    )
    _lane_runner.apply_lane_receipt(
        payload,
        blockers,
        delivery=delivery,
        require_change=require_change,
        scope=scope,
        stderr_text=stderr_text,
        guard_phases=_progress._guard_phases(payload),
        guard_blocker=_progress._guard_stop_reason(payload),
    )
    _apply_self_revert_backstop(
        payload, scope, blockers, base_sha=base_sha, require_change=require_change
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
    result_state = _acceptance_result_state(result_state, acceptance_skeleton)

    if report_only and result_state in ("completed", "non-delivery") and blockers:
        # A report-only lane has no candidate to salvage as a partial result:
        # with blockers present the only remaining "completed" shape is a
        # clipped report, and "non-delivery" is the missing report (#827).
        result_state = "failed"
    result_state = _state.apply_persistence_state(result_state, payload["persistence"])
    payload["review_required"] = _state.review_reasons(
        scope=scope, parent_progress=parent_progress, persistence=payload["persistence"]
    )
    payload["status"] = result_state
    payload["result_kind"] = _state.result_kind_for_status(result_state).value
    payload["lesson_injection"] = _lesson_injection_result(
        payload.get("lesson_injection")
    )
    payload["blockers"] = list(blockers)
    payload["blocker"] = _state.blocker_for_receipt(payload)
    payload["approval_eligibility"] = (
        "eligible" if result_state == "completed" and not blockers else "ineligible"
    )

    warnings = [
        f"{population}: {data['reason']}"
        for population, data in evidence["populations"].items()
        if data.get("verdict") == "warn"
    ]
    if parent_progress["classification"] == "concurrent-parent-progress":
        scoped = report_only and parent_progress.get("overlap_paths")
        note = "parent progressed inside the read scope while the task ran; recorded without writer-conflict blocking"
        warnings.append(note if scoped else "parent made disjoint progress while the task ran")
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
    payload["decision_ledger"] = _ledger.decision_ledger_link(resolved_repo)
    _evidence._attach_short_summary(payload, delivery)
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


def _lesson_injection_result(value: object) -> dict[str, Any]:
    """Keep lesson facts in the WI-1 receipt without adding a verdict kind."""
    raw = value if isinstance(value, Mapping) else {}

    def string_list(key: str) -> list[str]:
        items = raw.get(key)
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, str)]

    result: dict[str, Any] = {
        "schema_version": _lane_runner.LESSON_INJECTION_SCHEMA,
        "ledger_path": raw.get("ledger_path")
        if isinstance(raw.get("ledger_path"), str)
        else _lane_runner.LESSON_LEDGER_RELATIVE_PATH,
        "declared_slugs": string_list("declared_slugs"),
        "injected_ids": string_list("injected_ids"),
        "unmatched_slugs": string_list("unmatched_slugs"),
        "budget_excluded_ids": string_list("budget_excluded_ids"),
        "budget_bytes": raw.get("budget_bytes"),
        "used_bytes": raw.get("used_bytes"),
        "prepared": isinstance(value, Mapping),
        "non_claim": _lane_runner.LESSON_INJECTION_NON_CLAIM,
    }
    error = raw.get("error")
    if isinstance(error, str) and error:
        result["error"] = error
    return result


def _execution_reviewer_result(delivery: Mapping[str, Any]) -> dict[str, Any] | None:
    return _execution._reviewer_result_carrier(delivery)


def _apply_self_revert_backstop(
    payload: dict[str, Any],
    scope: Mapping[str, Any],
    blockers: list[str],
    *,
    base_sha: str,
    require_change: bool,
) -> bool:
    """Flag an EDITING lane that ends BLOCKED with an unchanged worktree (#834).

    A worker that discovers a scope mismatch after editing must keep its
    candidate and emit the typed extension request; a lane that emitted
    EDITING/TESTING and then reports BLOCKED with no changes discarded its
    own tested candidate (usually via ``git restore``). That shape reads as
    ``candidate-self-reverted`` on the receipt instead of a plain
    skipped/unchanged stall, and the guard's first-scoped-diff snapshot rides
    along when observed so the parent can recover what was discarded.
    """
    lane_progress = payload.get("lane_progress")
    phases = lane_progress.get("phases") if isinstance(lane_progress, Mapping) else []
    blocker = lane_progress.get("blocker") if isinstance(lane_progress, Mapping) else None
    edited = isinstance(phases, list) and any(
        phase in ("EDITING", "TESTING") for phase in phases
    )
    unchanged = not scope.get("changed_paths") and not scope.get("disallowed_paths")
    same_head = payload.get("target_sha") == base_sha
    if not (require_change and edited and isinstance(blocker, str) and blocker and unchanged and same_head):
        return False
    payload["candidate_self_reverted"] = True
    candidate = payload.get("candidate")
    if isinstance(candidate, dict):
        candidate["self_reverted"] = True
    guard = payload.get("progress_guard")
    snapshot = guard.get("first_scoped_diff") if isinstance(guard, Mapping) else None
    if isinstance(snapshot, Mapping) and snapshot.get("observed"):
        # The diff text lives once at progress_guard.first_scoped_diff; this
        # snapshot carries only the recovery pointer, not a second copy.
        payload["recovered_scoped_snapshot"] = {
            "changed_paths": list(snapshot.get("changed_paths") or []),
            "diff_ref": "progress_guard.first_scoped_diff.diff",
            "truncated": bool(snapshot.get("truncated")),
        }
    else:
        payload["recovered_scoped_snapshot"] = {
            "changed_paths": [],
            "diff_ref": None,
            "truncated": False,
            "unobserved": True,
        }
    blockers.append(
        "candidate self-reverted after EDITING: the lane emitted EDITING "
        "then ended BLOCKED with an unchanged worktree; keep the candidate "
        "on a rescope instead of restoring scoped files"
    )
    return True


def _completion_blockers(
    *,
    execution_status: str,
    scope: Mapping[str, Any],
    parent_progress: Mapping[str, Any],
    pass_value: str,
    delivery: Mapping[str, Any],
    report_only: bool = False,
    persistence: Mapping[str, Any] | None = None,
    acceptance_skeleton: Mapping[str, Any] | None = None,
) -> list[str]:
    blockers = [f"execution: {execution_status}"] if execution_status != "completed" else []
    blockers.extend(_persistence.persistence_blockers(persistence))
    blockers.extend(_evidence._report_delivery_blockers(delivery, report_only=report_only))
    if acceptance_skeleton and acceptance_skeleton.get("status") != "green":
        blockers.append("acceptance skeleton did not turn green")
    if scope["verdict"] != pass_value:
        blockers.append(str(scope["reason"]))
    if parent_progress["blocking"]:
        blockers.append("parent changed within the resolved candidate scope")
    if delivery.get("delivery_error"):
        blockers.append(f"result delivery could not be read: {delivery['delivery_error']}")
    return blockers


def _acceptance_result_state(
    result_state: str, acceptance_skeleton: Mapping[str, Any] | None
) -> str:
    if result_state == "completed" and acceptance_skeleton and acceptance_skeleton.get("status") != "green":
        return "completed-needs-review"
    return result_state


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

    _reconcile_persisted_blockers(payload, candidate, blockers, resolved_target)

    if blockers and result_state == "completed" and candidate.get("useful"):
        result_state = "validated-partial-result"
    return gate, blockers, result_state


def _reconcile_persisted_blockers(
    payload: dict[str, Any],
    candidate: dict[str, Any],
    blockers: list[str],
    resolved_target: Path,
) -> None:
    """Name an intentional recovery commit beside pre-persist blockers (#823).

    Persistence, correctness, and approval are separate facts: a commit the
    carrier persists after blockers were already reported is preserved for
    review, not a correctness or approval claim. Without this entry the
    executor's pre-persist declaration (e.g. "staged but uncommitted")
    stands beside the persisted commit as a contradiction no caller can
    resolve. Clean persists (no blockers) record nothing.
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
    if (
        execution_status != "completed"
        or not _candidate_has_work(candidate)
    ):
        return None
    if _carrier_is_complete(candidate):
        return None
    allowed = _lane_runner._in_scope_candidate_paths(candidate)
    if allowed is None:
        # No usable classification: staging everything would preserve the exact
        # hole this path closes, so the residue stays in the worktree instead.
        candidate["persist"] = {"status": "skipped", "reason": "candidate classification unavailable", "changed_paths": [], "correctness_verified": False}
        return "candidate persistence skipped: no usable scope classification; refusing the unscoped stage-everything shape"
    snapshot = _lane_runner.persist_incomplete_candidate(
        resolved_target,
        paths=allowed,
        git=git,
        git_output=git_output,
    )
    candidate["persist"] = snapshot
    if snapshot.get("status") == "skipped":
        return (
            "candidate persistence skipped: no in-scope changes to carry on the "
            "lane branch; lane residue stays in the worktree"
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


_apply_lane_retention = _retention._apply_lane_retention
release_finished_lane = _retention.release_finished_lane
_changed_line_verdict = _changed_line._changed_line_verdict
