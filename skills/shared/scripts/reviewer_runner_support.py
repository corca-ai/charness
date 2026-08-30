"""Collection and lane-path helpers for the canonical reviewer runner."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

try:
    from reviewer_delivery import (
        COLLECTION_FAILED,
        HOST_CHANNEL_UNREADABLE,
        INTERRUPTED,
        NON_DELIVERY_UNKNOWN,
        TIMED_OUT,
        _read,
        _write,
        ledger_lock,
        utc_now,
    )
except ImportError:
    from skills.shared.scripts.reviewer_delivery import (
        COLLECTION_FAILED,
        HOST_CHANNEL_UNREADABLE,
        INTERRUPTED,
        NON_DELIVERY_UNKNOWN,
        TIMED_OUT,
        _read,
        _write,
        ledger_lock,
        utc_now,
    )


def failure_state(receipt: dict[str, Any] | None) -> str:
    status = receipt.get("status") if isinstance(receipt, dict) else None
    if status == "timed-out":
        return TIMED_OUT
    if status == "interrupted":
        return INTERRUPTED
    if status in {"transport-unestablished", "credential-invalid", "authorization-insufficient"}:
        return HOST_CHANNEL_UNREADABLE
    return NON_DELIVERY_UNKNOWN


def _transition(ledger_path: Path, attempt_id: str, state: str, signal: str, recorded_at: str | None) -> None:
    with ledger_lock(ledger_path):
        ledger = _read(ledger_path)
        attempt = ledger.require(attempt_id)
        attempt.transition(state, signal, recorded_at or utc_now())
        _write(ledger_path, ledger)


def finalize_attempt(
    *,
    receipt_path: Path,
    ledger_path: Path,
    attempt_id: str,
    scope: str,
    packet_identity: str,
    reviewed_input_identity: str,
    parent_receipt_identity: str,
    execution_mode: str,
    build_report: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Validate collection before changing the attempt to findings-received."""
    receipt: dict[str, Any] | None = None
    receipt_error: Exception | None = None
    try:
        loaded = json.loads(receipt_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("worker receipt must be a JSON object")
        receipt = loaded
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        receipt_error = exc
    pre_report: dict[str, Any] | None = None
    if receipt is not None:
        try:
            pre_report = build_report(
                receipt_path=str(receipt_path), ledger_path=str(ledger_path), attempt_id=attempt_id,
                scope=scope, packet_identity=packet_identity,
                reviewed_input_identity=reviewed_input_identity,
                parent_receipt_identity=parent_receipt_identity,
                expected_execution_mode=execution_mode,
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            receipt_error = exc
        if (
            pre_report is not None
            and pre_report.get("partial_output_ok") is True
            and isinstance(pre_report.get("partial_output"), dict)
        ):
            with ledger_lock(ledger_path):
                ledger = _read(ledger_path)
                attempt = ledger.require(attempt_id)
                attempt.record_partial(
                    partial_output=pre_report["partial_output"],
                    recorded_at=(receipt or {}).get("finished_at", "") or utc_now(),
                )
                _write(ledger_path, ledger)
        if receipt.get("status") == "succeeded" and pre_report is not None and pre_report.get("collection_ready"):
            with ledger_lock(ledger_path):
                ledger = _read(ledger_path)
                attempt = ledger.require(attempt_id)
                attempt.record_findings(
                    scope=scope, packet_identity=packet_identity,
                    parent_receipt_identity=parent_receipt_identity,
                    findings_identity=receipt.get("output_sha256", ""),
                    recorded_at=receipt.get("finished_at", "") or utc_now(),
                )
                _write(ledger_path, ledger)
        else:
            terminal_failure = (
                failure_state(receipt)
                if receipt.get("status") in {"timed-out", "interrupted"}
                else COLLECTION_FAILED
            )
            _transition(
                ledger_path, attempt_id, terminal_failure,
                "worker collection validation failed before findings-received: "
                + (str(receipt_error) if receipt_error else str((pre_report or {}).get("reason"))),
                (receipt or {}).get("finished_at"),
            )
    else:
        status = receipt.get("status") if receipt is not None else "missing-receipt"
        failure = failure_state(receipt)
        signal = f"file-backed worker ended with status {status!r}" + (
            f": {receipt_error}" if receipt_error else ""
        )
        _transition(ledger_path, attempt_id, failure, signal, (receipt or {}).get("finished_at"))
    return build_report(
        receipt_path=str(receipt_path), ledger_path=str(ledger_path), attempt_id=attempt_id,
        scope=scope, packet_identity=packet_identity,
        reviewed_input_identity=reviewed_input_identity,
        parent_receipt_identity=parent_receipt_identity,
        expected_execution_mode=execution_mode,
    )
