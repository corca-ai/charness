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

from scripts.task_run import task_run_completion_proof as _proof  # noqa: E402
from scripts.task_run import task_run_evidence as _evidence  # noqa: E402
from scripts.task_run import task_run_execution as _execution  # noqa: E402
from scripts.task_run import task_run_friction as _friction  # noqa: E402
from scripts.task_run import task_run_lane_runner as _lane_runner  # noqa: E402
from scripts.task_run import task_run_ledger as _ledger  # noqa: E402
from scripts.task_run import task_run_lesson_injection as _lesson_injection  # noqa: E402
from scripts.task_run import task_run_persistence as _persistence  # noqa: E402
from scripts.task_run import task_run_prelaunch as _prelaunch  # noqa: E402
from scripts.task_run import task_run_progress as _progress  # noqa: E402
from scripts.task_run import task_run_retention as _retention  # noqa: E402
from scripts.task_run import task_run_state as _state  # noqa: E402
from scripts.task_run.task_run_completion_next_step import _next_step  # noqa: E402


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
    stderr_text = _evidence._lane_stderr_text(stdout_log, stderr_log)
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
    effective_scope_specs = scope.get("specs")
    if not isinstance(effective_scope_specs, list):
        effective_scope_specs = scope_specs
    blockers += _prelaunch.acceptance_deficit_blockers(
        payload, resolved_target, effective_scope_specs, candidate
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
    gate, blockers, result_state = _proof._prove_ready_candidate(
        payload,
        candidate,
        blockers=blockers,
        scope=scope,
        result_state=result_state,
        execution_status=execution_status,
        resolved_target=resolved_target,
        base_sha=base_sha,
        stdout_log=stdout_log,
        changed_line_gate=changed_line_gate,
        git=git,
        git_output=git_output,
        pass_value=pass_value,
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
    payload["lesson_injection"] = _lesson_injection.injection_result(
        payload.get("lesson_injection")
    )
    payload["blockers"] = list(blockers)
    payload["blocker"] = _state.blocker_for_receipt(payload)
    _friction.append_completion_friction(
        runtime_path,
        task_id=str(payload.get("task_id") or "unknown-task"),
        blockers=blockers,
        parent_classification=str(parent_progress.get("classification") or ""),
    )
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


def _execution_reviewer_result(delivery: Mapping[str, Any]) -> dict[str, Any] | None:
    return _execution._reviewer_result_carrier(delivery)


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


_apply_lane_retention = _retention._apply_lane_retention
release_finished_lane = _retention.release_finished_lane
