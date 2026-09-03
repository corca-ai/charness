"""Executable contract for the parent-side reviewer delivery state machine."""

from __future__ import annotations

import hashlib
import json
import threading

import pytest

from skills.shared.scripts import reviewer_delivery as delivery
from skills.shared.scripts import reviewer_runner_support


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


@pytest.mark.parametrize("terminal_state", [delivery.TIMED_OUT, delivery.INTERRUPTED])
def test_partial_output_is_typed_non_delivery_and_survives_terminal_failure(
    tmp_path, terminal_state: str
) -> None:
    ledger = _ledger()
    attempt = ledger.require("a1")
    attempt.transition(delivery.RUNNING, "reviewer worker started", "2026-08-21T00:00:05Z")
    partial_path = tmp_path / "result.json.partial"
    partial_path.write_text('{"findings": ["observed before timeout"]}\n', encoding="utf-8")
    descriptor = {
        "schema_version": "charness.reviewer_partial_output.v1",
        "kind": "backend-output",
        "path": str(partial_path),
        "bytes": partial_path.stat().st_size,
        "sha256": hashlib.sha256(partial_path.read_bytes()).hexdigest(),
    }

    assert attempt.record_partial(partial_output=descriptor, recorded_at="2026-08-21T00:00:06Z") is True
    assert attempt.state == delivery.PARTIAL
    assert attempt.terminal is False
    assert attempt.delivery_complete is False
    with pytest.raises(delivery.DeliveryError, match="requires record_partial"):
        attempt.transition(delivery.PARTIAL, "duplicate partial", "2026-08-21T00:00:07Z")

    attempt.transition(terminal_state, f"host signal: {terminal_state}", "2026-08-21T00:00:10Z")
    assert attempt.delivery_complete is False
    assert attempt.partial_output == descriptor
    assert attempt.history[-2]["state"] == delivery.PARTIAL
    assert attempt.history[-2]["partial_output"] == descriptor
    restored = delivery.DeliveryLedger.from_dict(ledger.to_dict()).require("a1")
    assert restored.state == terminal_state
    assert restored.partial_output == descriptor


def test_partial_history_cannot_be_attached_to_a_non_partial_event() -> None:
    payload = _ledger().to_dict()
    event = payload["attempts"][0]["history"][0]
    event["partial_output"] = {
        "schema_version": "charness.reviewer_partial_output.v1",
        "kind": "backend-output",
        "path": "result.json.partial",
        "bytes": 1,
        "sha256": "a" * 64,
    }
    with pytest.raises(delivery.DeliveryError, match="only valid on a partial history event"):
        delivery.DeliveryLedger.from_dict(payload)


def test_parent_receipt_identity_is_case_sensitive_and_round_trips() -> None:
    ledger = delivery.DeliveryLedger.empty()
    ledger.start(
        attempt_id="case-a1",
        scope="scope-sha",
        packet_identity="packet-sha",
        parent_receipt_identity="Parent.Receipt:1",
        boundary_fingerprint="fingerprint-a1",
        recorded_at="2026-08-21T00:00:00Z",
    )
    assert _findings(
        ledger,
        attempt_id="case-a1",
        parent_receipt_identity="Parent.Receipt:1",
    ) is True
    restored = delivery.DeliveryLedger.from_dict(ledger.to_dict())
    assert restored.require("case-a1").parent_receipt_identity == "Parent.Receipt:1"


@pytest.mark.parametrize("receipt", ["", "bad receipt", "bad\nreceipt", "@bad"])
def test_parent_receipt_identity_rejects_malformed_values(receipt: str) -> None:
    with pytest.raises(delivery.DeliveryError, match="parent_receipt_identity"):
        delivery.DeliveryLedger.empty().start(
            attempt_id="bad-a1",
            scope="scope-sha",
            packet_identity="packet-sha",
            parent_receipt_identity=receipt,
            boundary_fingerprint="fingerprint-a1",
            recorded_at="2026-08-21T00:00:00Z",
        )


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


def test_retry_refuses_an_active_parent() -> None:
    ledger = _ledger()
    with pytest.raises(delivery.DeliveryError, match="terminal retryable"):
        ledger.retry("a1", new_attempt_id="a2", recorded_at="2026-08-21T00:02:00Z")


def test_readback_refuses_foreign_retry_lineage() -> None:
    ledger = _ledger()
    ledger.require("a1").transition(
        delivery.COLLECTION_FAILED, "collection rejected the receipt", "2026-08-21T00:00:10Z"
    )
    payload = ledger.to_dict()
    retry = delivery.DeliveryAttempt.start(
        attempt_id="a2",
        scope="scope-sha",
        packet_identity="packet-sha",
        parent_receipt_identity="receipt-a1",
        boundary_fingerprint="fingerprint-a1",
        recorded_at="2026-08-21T00:02:00Z",
        retry_of="foreign",
        retry_count=1,
    )
    payload["attempts"].append(retry.to_dict())
    with pytest.raises(delivery.DeliveryError, match="existing attempt"):
        delivery.DeliveryLedger.from_dict(payload)


def test_readback_refuses_retry_count_gap_and_non_immediate_predecessor() -> None:
    ledger = _ledger()
    ledger.require("a1").transition(
        delivery.TIMED_OUT, "host signal: timeout", "2026-08-21T00:00:10Z"
    )
    retry = ledger.retry("a1", new_attempt_id="a2", recorded_at="2026-08-21T00:02:00Z")
    payload = ledger.to_dict()
    forged = {**retry.to_dict(), "attempt_id": "a3", "retry_of": "a1", "retry_count": 1}
    forged["history"] = [{**event, "attempt_id": "a3"} for event in forged["history"]]
    payload["attempts"].append(forged)
    with pytest.raises(delivery.DeliveryError, match="immediate predecessor"):
        delivery.DeliveryLedger.from_dict(payload)


def test_runner_collection_failure_is_typed_and_retryable(tmp_path) -> None:
    ledger_path = tmp_path / "delivery.json"
    receipt_path = tmp_path / "receipt.json"
    ledger = _ledger()
    delivery._write(ledger_path, ledger)
    receipt_path.write_text(
        json.dumps({"status": "succeeded", "finished_at": "2026-08-21T00:00:10Z"}),
        encoding="utf-8",
    )
    reports: list[dict[str, object]] = []

    def build_report(**kwargs: object) -> dict[str, object]:
        reports.append(kwargs)
        if len(reports) == 1:
            return {"collection_ready": False, "reason": "typed result chain is invalid"}
        restored = delivery._read(ledger_path)
        return {"delivery_state": restored.require("a1").state}

    report = reviewer_runner_support.finalize_attempt(
        receipt_path=receipt_path,
        ledger_path=ledger_path,
        attempt_id="a1",
        scope="scope-sha",
        packet_identity="packet-sha",
        reviewed_input_identity="reviewed-sha",
        parent_receipt_identity="receipt-a1",
        execution_mode="file-backed-worker",
        build_report=build_report,
    )
    assert report["delivery_state"] == delivery.COLLECTION_FAILED
    assert delivery._read(ledger_path).require("a1").state == delivery.COLLECTION_FAILED
    retry = delivery._read(ledger_path).retry("a1", new_attempt_id="a2")
    assert retry.retry_of == "a1"
    assert retry.retry_count == 1
    assert len(reports) == 2


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
    with pytest.raises(delivery.DeliveryError, match="parent attempt_id"):
        delivery.DeliveryLedger.from_dict(payload)


def _lock_path_for(path) -> object:
    """The lock file `delivery.ledger_lock` opens for `path`.

    Mirrors `skills/shared/scripts/reviewer_delivery.py::ledger_lock`, which
    derives it inline (`path.with_name(f".{path.name}.lock")`) rather than
    through a helper a test could import. Keep the two in step.
    """
    return path.with_name(f".{path.name}.lock")


def test_ledger_lock_serializes_concurrent_read_modify_write(tmp_path) -> None:
    """Second writer's read-modify-write starts only after the first one released.

    The window used to be widened with a sleep inside the critical section and
    the threads raced for it, so a no-op lock could still pass whenever the
    scheduler happened to interleave kindly. The interleaving is now ORDERED by
    events with no timeout: B announces its attempt while A is provably inside
    the lock, and A only finishes once that announcement has landed. A correct
    lock can then produce exactly one log, because B's acquire cannot precede
    A's release; a no-op lock puts "b-acquire" before "a-release" every time.
    """
    path = tmp_path / "delivery.json"
    a_inside = threading.Event()
    b_attempted = threading.Event()
    log: list[str] = []

    def start_attempt(index: int) -> None:
        ledger = delivery._read(path)
        ledger.start(
            attempt_id=f"a{index}",
            scope=f"scope-{index}",
            packet_identity=f"packet-{index}",
            parent_receipt_identity=f"receipt-{index}",
            boundary_fingerprint=f"fingerprint-{index}",
            recorded_at=f"2026-08-21T00:00:0{index}Z",
        )
        delivery._write(path, ledger)

    def first_writer() -> None:
        with delivery.ledger_lock(path):
            log.append("a-acquire")
            a_inside.set()
            b_attempted.wait()
            start_attempt(0)
        log.append("a-release")

    def second_writer() -> None:
        a_inside.wait()
        log.append("b-attempt")
        b_attempted.set()
        with delivery.ledger_lock(path):
            log.append("b-acquire")
            start_attempt(1)

    threads = [
        threading.Thread(target=first_writer),
        threading.Thread(target=second_writer),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert log == ["a-acquire", "b-attempt", "a-release", "b-acquire"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert {attempt["attempt_id"] for attempt in payload["attempts"]} == {"a0", "a1"}


def test_ledger_lock_holds_a_real_exclusive_file_lock(tmp_path) -> None:
    """While the ledger lock is held, an independent open cannot take it.

    The interleaving test above reads the lock through its effect on a second
    caller. This reads the primitive directly: `ledger_lock` is an `fcntl.flock`
    on a per-path lock file, so a separate descriptor on that same file must be
    refused while a holder is inside. Without it, "serialized" could still be an
    ordering the events imposed rather than the lock.
    """
    # Linux-only, like the runner: `ledger_lock` itself imports fcntl on posix
    # and msvcrt elsewhere, and the repo has no non-posix runner to exercise.
    import fcntl

    path = tmp_path / "delivery.json"
    holder_inside = threading.Event()
    release_holder = threading.Event()

    def hold_the_lock() -> None:
        with delivery.ledger_lock(path):
            holder_inside.set()
            release_holder.wait()

    holder = threading.Thread(target=hold_the_lock)
    holder.start()
    try:
        holder_inside.wait()
        with _lock_path_for(path).open("a+b") as handle:
            with pytest.raises(BlockingIOError):
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    finally:
        release_holder.set()
        holder.join()
