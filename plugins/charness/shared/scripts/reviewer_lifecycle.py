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
DELIVERY_STATES = frozenset({"none", "findings-received", "timed-out", "interrupted", "invalid"})
VERDICT_STATES = frozenset({"not-applicable", "pass", "block"})


def _failure_identity(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def _delivery_state(report: dict[str, Any] | None) -> str:
    if not isinstance(report, dict):
        return "none"
    state = report.get("delivery_state")
    if state == "findings-received":
        return "findings-received"
    if state == "timed-out":
        return "timed-out"
    if state == "interrupted":
        return "interrupted"
    return "invalid"


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
    verdict = report.get("review_verdict") if valid_report else None
    verdict_state = verdict if verdict in {"pass", "block"} else "not-applicable"
    approval = bool(valid_report and report.get("approval_eligible") is True and verdict_state == "pass")
    if boundary_ok is False:
        approval = False
    failure_text = error or (report.get("reason") if valid_report else None)
    if boundary_ok is False:
        failure_text = boundary_reason or "reviewer boundary readback was not clean"
    if execution == "preflight-blocked":
        next_move = "repair the named preflight boundary and rerun; reviewer did not start"
    elif delivery in {"timed-out", "interrupted", "invalid"}:
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
        "reviewer_started": started,
        "delivery_state": delivery,
        "verdict_state": verdict_state,
        "review_verdict": verdict,
        "classification": (
            report.get("classification", "unclassified") if verdict_state != "not-applicable" and valid_report else None
        ),
        "approval_eligible": approval,
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
