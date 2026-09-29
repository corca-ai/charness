"""Small typed lifecycle carrier for one file-backed reviewer run.

The worker receipt and delivery ledger remain the approval authority. This
module only projects their observed state into the fields an operator needs to
choose the next action without reading several low-level files.
"""

from __future__ import annotations

import hashlib
from typing import Any

SCHEMA_VERSION = "charness.reviewer_lifecycle.v1"
EXECUTION_STATES = frozenset({"preflight-blocked", "started", "terminal"})
DELIVERY_STATES = frozenset(
    {
        "none",
        "spawn-accepted",
        "running",
        "partial",
        "findings-received",
        "timed-out",
        "interrupted",
        "invalid",
    }
)
LIFECYCLE_STATES = frozenset(
    {"preflight-blocked", "accepted", "running", "partial", "timed-out", "interrupted", "terminal"}
)
OUTPUT_STATES = frozenset({"none", "partial", "terminal"})
VERDICT_STATES = frozenset({"not-applicable", "pass", "block"})


def _failure_identity(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def _delivery_state(report: dict[str, Any] | None) -> str:
    if not isinstance(report, dict):
        return "none"
    state = report.get("delivery_state")
    if state in DELIVERY_STATES:
        return state
    # The runner's final report is emitted after collection terminalizes a
    # failed attempt.  Preserve the worker's typed deadline/interruption
    # signal instead of collapsing it to the implementation detail
    # ``collection-failed``.
    receipt_status = report.get("receipt_status")
    if receipt_status in {"timed-out", "interrupted"}:
        return receipt_status
    if report.get("partial_output_ok") is True:
        return "partial"
    return "invalid"


def _lifecycle_state(
    *, status: str, delivery: str, started: bool, valid_report: bool, dry_run: bool
) -> str:
    if dry_run or not started:
        return "preflight-blocked"
    if status == "runner-timeout" or delivery == "timed-out":
        return "timed-out"
    if status == "runner-interrupted" or delivery == "interrupted":
        return "interrupted"
    if delivery == "spawn-accepted":
        return "accepted"
    if delivery == "running":
        return "running"
    if delivery == "partial":
        return "partial"
    if valid_report or status == "runner-completed":
        return "terminal"
    return "terminal"


def _typed_output(
    *,
    lifecycle_state: str,
    delivery: str,
    valid_report: bool,
    report: dict[str, Any] | None,
    approval: bool,
    partial_outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    report_partial = report.get("partial_output") if valid_report and report else None
    if isinstance(report_partial, dict) and report_partial not in partial_outputs:
        partial_outputs = [report_partial, *partial_outputs]
    if lifecycle_state == "terminal" and delivery == "findings-received" and valid_report:
        output = {
            "state": "terminal",
            "approval_eligible": approval,
            "schema_version": report.get("schema_version") if report else None,
            "findings_identity": report.get("findings_identity") if report else None,
        }
        if partial_outputs:
            output["partial_artifacts"] = partial_outputs
        return output
    if partial_outputs:
        return {
            "state": "partial",
            "approval_eligible": False,
            "artifacts": partial_outputs,
        }
    return {"state": "none", "approval_eligible": False, "artifacts": []}


def build_lifecycle(
    *,
    status: str,
    report: dict[str, Any] | None = None,
    error: str | None = None,
    returncode: int | None = None,
    reviewer_started: bool | None = None,
    boundary_mode: str | None = None,
    boundary_ok: bool | None = None,
    boundary_reason: str | None = None,
    dry_run: bool = False,
    paths: dict[str, str] | None = None,
    partial_outputs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build one operator-facing state without upgrading weak evidence."""
    valid_report = isinstance(report, dict) and report.get("schema_version") == "charness.reviewer_worker_report.v1"
    delivery = _delivery_state(report if valid_report else None)
    if dry_run:
        execution = "preflight-blocked"
        started = False
        delivery = "none"
    else:
        started = reviewer_started if reviewer_started is not None else valid_report
        if not started:
            delivery = "none"
            execution = "preflight-blocked"
        elif status == "runner-timeout" or delivery == "timed-out":
            delivery = "timed-out"
            execution = "started"
        elif status == "runner-interrupted" or delivery == "interrupted":
            delivery = "interrupted"
            execution = "started"
        elif valid_report:
            execution = "terminal"
        else:
            delivery = "invalid"
            execution = "terminal"
    lifecycle_state = _lifecycle_state(
        status=status,
        delivery=delivery,
        started=started,
        valid_report=valid_report,
        dry_run=dry_run,
    )
    verdict = report.get("review_verdict") if valid_report else None
    verdict_state = verdict if verdict in {"pass", "block"} else "not-applicable"
    approval = bool(
        valid_report
        and lifecycle_state == "terminal"
        and delivery == "findings-received"
        and report.get("approval_eligible") is True
        and verdict_state == "pass"
    )
    if boundary_ok is False:
        approval = False
    typed_output = _typed_output(
        lifecycle_state=lifecycle_state,
        delivery=delivery,
        valid_report=valid_report,
        report=report,
        approval=approval,
        partial_outputs=list(partial_outputs or []),
    )
    failure_text = error or (report.get("reason") if valid_report else None)
    if boundary_ok is False:
        failure_text = boundary_reason or "reviewer boundary readback was not clean"
    if execution == "preflight-blocked":
        next_move = "repair the named preflight boundary and rerun; reviewer did not start"
    elif lifecycle_state in {"timed-out", "interrupted", "partial"} or delivery == "invalid":
        next_move = "inspect preserved partial carriers, repair the failed delivery boundary, then rerun"
    elif verdict_state == "block":
        next_move = "inspect the delivered findings; this is a reviewer block, not a runner failure"
    elif approval:
        next_move = "consume the identity-bound delivered reviewer result"
    else:
        next_move = "inspect the typed carrier before treating the run as approval"
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "dry-run-ready" if dry_run else status,
        "execution_state": execution,
        "lifecycle_state": lifecycle_state,
        "reviewer_started": started,
        "delivery_state": delivery,
        "verdict_state": verdict_state,
        "review_verdict": verdict,
        "classification": (
            report.get("classification", "unclassified") if verdict_state != "not-applicable" and valid_report else None
        ),
        "approval_eligible": approval,
        "output": typed_output,
        "output_state": typed_output["state"],
        "failure_identity": _failure_identity(failure_text),
        "next_move": next_move,
        "runner_returncode": returncode,
        "runner_status": status,
        "boundary_mode": boundary_mode,
        "boundary_ok": boundary_ok,
        "boundary_reason": boundary_reason,
        "paths": dict(paths or {}),
    }
    if valid_report:
        result["identities"] = {
            key: report.get(key)
            for key in (
                "attempt_id",
                "scope",
                "packet_identity",
                "reviewed_input_identity",
                "parent_receipt_identity",
                "findings_identity",
            )
            if report.get(key) is not None
        }
    return result
