"""Typed lifecycle projection for partial reviewer progress (#731)."""

from __future__ import annotations

import hashlib

import pytest

from skills.shared.scripts.reviewer_lifecycle import build_lifecycle


def _partial_descriptor() -> dict[str, object]:
    return {
        "schema_version": "charness.reviewer_partial_output.v1",
        "kind": "backend-output",
        "path": ".charness/reviewer-round-a/result.json.partial",
        "bytes": 7,
        "sha256": hashlib.sha256(b"partial").hexdigest(),
    }


def _report(state: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "charness.reviewer_worker_report.v1",
        "delivery_state": state,
        "approval_eligible": False,
        "review_verdict": None,
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    ("state", "expected_lifecycle"),
    [
        ("spawn-accepted", "accepted"),
        ("running", "running"),
        ("partial", "partial"),
    ],
)
def test_active_states_are_typed_and_never_approval_eligible(state: str, expected_lifecycle: str) -> None:
    partial = [_partial_descriptor()] if state == "partial" else []
    payload = build_lifecycle(
        status="runner-completed",
        report=_report(state),
        reviewer_started=True,
        boundary_ok=True,
        partial_outputs=partial,
    )

    assert payload["lifecycle_state"] == expected_lifecycle
    assert payload["approval_eligible"] is False
    assert payload["output"]["approval_eligible"] is False
    assert payload["output_state"] == ("partial" if partial else "none")


def test_timeout_preserves_partial_output_but_remains_non_delivery() -> None:
    partial = _partial_descriptor()
    payload = build_lifecycle(
        status="runner-completed",
        report=_report(
            "collection-failed",
            receipt_status="timed-out",
            partial_output=partial,
            partial_output_ok=True,
        ),
        reviewer_started=True,
        returncode=1,
        boundary_ok=True,
        partial_outputs=[{"schema_version": partial["schema_version"], **partial}],
    )

    assert payload["lifecycle_state"] == "timed-out"
    assert payload["delivery_state"] == "timed-out"
    assert payload["execution_state"] == "started"
    assert payload["approval_eligible"] is False
    assert payload["output_state"] == "partial"
    assert payload["output"]["approval_eligible"] is False


def test_only_terminal_findings_received_pass_can_be_approval_eligible() -> None:
    payload = build_lifecycle(
        status="runner-completed",
        report=_report(
            "findings-received",
            approval_eligible=True,
            review_verdict="pass",
            findings_identity="f" * 64,
        ),
        reviewer_started=True,
        boundary_ok=True,
    )

    assert payload["lifecycle_state"] == "terminal"
    assert payload["delivery_state"] == "findings-received"
    assert payload["output_state"] == "terminal"
    assert payload["approval_eligible"] is True
    assert payload["output"]["approval_eligible"] is True


def test_terminal_worker_report_without_findings_is_not_terminal_output() -> None:
    payload = build_lifecycle(
        status="runner-completed",
        report=_report("collection-failed", receipt_status="backend-failed"),
        reviewer_started=True,
        boundary_ok=True,
    )

    assert payload["lifecycle_state"] == "terminal"
    assert payload["approval_eligible"] is False
    assert payload["output_state"] == "none"
