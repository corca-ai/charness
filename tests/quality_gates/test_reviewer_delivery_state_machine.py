"""Executable contract for the parent-side reviewer delivery state machine."""

from __future__ import annotations

import pytest

from skills.shared.scripts import reviewer_delivery as delivery


def _ledger() -> delivery.DeliveryLedger:
    ledger = delivery.DeliveryLedger.empty()
    ledger.start(
        attempt_id="a1",
        scope="scope-sha",
        packet_identity="packet-sha",
        parent_receipt_identity="receipt-a1",
        boundary_fingerprint="fingerprint-a1",
        recorded_at="2026-08-21T00:00:00Z",
    )
    return ledger


def _findings(ledger: delivery.DeliveryLedger, attempt_id: str = "a1", **overrides: str) -> bool:
    values = {
        "scope": "scope-sha",
        "packet_identity": "packet-sha",
        "parent_receipt_identity": "receipt-a1",
        "findings_identity": "f" * 64,
        "recorded_at": "2026-08-21T00:01:00Z",
    }
    values.update(overrides)
    return ledger.require(attempt_id).record_findings(**values)


def test_spawn_acceptance_is_not_approval() -> None:
    attempt = _ledger().require("a1")
    assert attempt.state == delivery.SPAWN_ACCEPTED
    assert attempt.terminal is False
    assert attempt.delivery_complete is False
    assert attempt.history[0]["event_id"]


def test_findings_received_is_the_only_approval_state() -> None:
    ledger = _ledger()
    ledger.require("a1").transition(delivery.RUNNING, "reviewer started", "2026-08-21T00:00:10Z")
    assert _findings(ledger) is True
    attempt = ledger.require("a1")
    assert attempt.state == delivery.FINDINGS_RECEIVED
    assert attempt.terminal is True
    assert attempt.delivery_complete is True


@pytest.mark.parametrize(
    "state",
    [
        delivery.INTERRUPTED,
        delivery.TIMED_OUT,
        delivery.HOST_CHANNEL_UNREADABLE,
        delivery.HOST_CAPACITY_BLOCKED,
        delivery.SPAWN_ACCEPTED_NO_DELIVERY,
        delivery.NON_DELIVERY_UNKNOWN,
    ],
)
def test_non_delivery_states_are_terminal_refusals(state: str) -> None:
    ledger = _ledger()
    ledger.require("a1").transition(state, f"host signal: {state}", "2026-08-21T00:00:10Z")
    attempt = ledger.require("a1")
    assert attempt.terminal is True
    assert attempt.delivery_complete is False


def test_findings_provenance_mismatch_becomes_unknown_not_approval() -> None:
    ledger = _ledger()
    assert _findings(ledger, scope="foreign-scope") is False
    attempt = ledger.require("a1")
    assert attempt.state == delivery.NON_DELIVERY_UNKNOWN
    assert attempt.delivery_complete is False
    assert attempt.observations[-1]["state"] == "foreign-findings"


def test_late_findings_cannot_resurrect_interrupted_attempt() -> None:
    ledger = _ledger()
    ledger.require("a1").transition(delivery.INTERRUPTED, "host signal: interrupted", "2026-08-21T00:00:10Z")
    assert _findings(ledger) is False
    attempt = ledger.require("a1")
    assert attempt.state == delivery.INTERRUPTED
    assert attempt.delivery_complete is False
    assert attempt.observations[-1]["state"] == "late-or-duplicate-findings"
    assert attempt.observations[-1]["event_id"]


def test_transcript_recovery_is_an_observation_not_delivery() -> None:
    ledger = _ledger()
    ledger.require("a1").record_recovery("host transcript only; parent did not receive it", "2026-08-21T00:00:10Z")
    attempt = ledger.require("a1")
    assert attempt.state == delivery.SPAWN_ACCEPTED
    assert attempt.delivery_complete is False
    assert attempt.observations[-1]["state"] == delivery.RECOVERED_FROM_TRANSCRIPT
    assert attempt.observations[-1]["delivery_complete"] is False


def test_retry_preserves_original_and_is_bounded_to_one() -> None:
    ledger = _ledger()
    ledger.require("a1").transition(delivery.TIMED_OUT, "host signal: timeout", "2026-08-21T00:00:10Z")
    retry = ledger.retry("a1", new_attempt_id="a2", recorded_at="2026-08-21T00:02:00Z")
    assert retry.retry_of == "a1"
    assert retry.retry_count == 1
    assert ledger.require("a1").state == delivery.TIMED_OUT
    with pytest.raises(delivery.DeliveryError, match="bounded to one retry"):
        ledger.retry("a2", new_attempt_id="a3", recorded_at="2026-08-21T00:03:00Z")


def test_duplicate_canonical_transition_is_rejected() -> None:
    ledger = _ledger()
    with pytest.raises(delivery.DeliveryError, match="duplicate canonical state"):
        ledger.require("a1").transition(delivery.SPAWN_ACCEPTED, "duplicate", "2026-08-21T00:00:01Z")


def test_direct_transition_cannot_claim_findings_without_provenance() -> None:
    ledger = _ledger()
    with pytest.raises(delivery.DeliveryError, match="requires record_findings"):
        ledger.require("a1").transition(delivery.FINDINGS_RECEIVED, "unverified", "2026-08-21T00:00:01Z")


def test_malformed_terminal_flag_is_rejected_on_readback() -> None:
    payload = _ledger().to_dict()
    payload["attempts"][0]["terminal"] = True
    with pytest.raises(delivery.DeliveryError, match="terminal flag"):
        delivery.DeliveryLedger.from_dict(payload)


def test_forged_history_is_rejected_on_readback() -> None:
    payload = _ledger().to_dict()
    payload["attempts"][0]["history"].append(
        {
            "event_id": "forged",
            "state": delivery.FINDINGS_RECEIVED,
            "signal": "forged",
            "terminal": True,
            "recorded_at": "2026-08-21T00:00:02Z",
        }
    )
    with pytest.raises(delivery.DeliveryError, match="history final state"):
        delivery.DeliveryLedger.from_dict(payload)
