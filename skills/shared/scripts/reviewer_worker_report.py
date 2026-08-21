#!/usr/bin/env python3
"""Consume a worker receipt and delivery ledger without inferring delivery.

The consumer boundary is deliberately narrower than the worker boundary: a
fresh result file, process exit code, or successful receipt is not approval.
Only a succeeded typed receipt plus a matching ``findings-received`` ledger
attempt can produce ``approval_eligible: true``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from reviewer_delivery import DeliveryError, DeliveryLedger
except ImportError:
    from skills.shared.scripts.reviewer_delivery import DeliveryError, DeliveryLedger

try:
    from reviewer_output import emit_yaml
except ImportError:
    from skills.shared.scripts.reviewer_output import emit_yaml

REPORT_SCHEMA_VERSION = "charness.reviewer_worker_report.v1"
WORKER_SCHEMA_VERSION = "charness.reviewer_worker.v1"
SUCCESS = "succeeded"
FINDINGS_RECEIVED = "findings-received"


class ReportError(ValueError):
    """Input cannot support a trustworthy consumer report."""


def _read_json(path_value: str, label: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_value).expanduser().resolve()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReportError(f"{label} is not readable JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReportError(f"{label} must contain a JSON object: {path}")
    return path, payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_receipt(
    receipt: dict[str, Any],
    *,
    attempt: Any,
    expected_execution_mode: str,
) -> tuple[bool, str]:
    if receipt.get("schema_version") != WORKER_SCHEMA_VERSION:
        return False, "worker receipt schema_version is not the Charness worker schema"
    if receipt.get("terminal") is not True:
        return False, "worker receipt is not terminal"
    if receipt.get("status") != SUCCESS:
        return False, f"worker receipt status is {receipt.get('status')!r}"
    if receipt.get("exit_code") != 0:
        return False, "successful worker receipt must carry exit_code 0"
    joins = {
        "attempt_id": attempt.attempt_id,
        "scope": attempt.scope,
        "packet_identity": attempt.packet_identity,
        "reviewed_input_identity": attempt.reviewed_input_identity,
        "execution_mode": attempt.execution_mode,
        "backend": attempt.backend,
        "prompt_sha256": attempt.prompt_sha256,
        "schema_sha256": attempt.schema_sha256,
    }
    for field, expected in joins.items():
        if expected is None:
            return False, f"delivery attempt has no bound {field}"
        if receipt.get(field) != expected:
            return False, f"worker receipt {field} does not match the delivery attempt"
    output_value = receipt.get("output_file")
    if not isinstance(output_value, str) or not output_value:
        return False, "successful receipt has no output_file"
    output = Path(output_value).expanduser().resolve()
    if receipt.get("output_fresh") is not True or not output.is_file():
        return False, "successful receipt does not prove a fresh output file"
    expected_hash = receipt.get("output_sha256")
    if not isinstance(expected_hash, str) or _sha256(output) != expected_hash:
        return False, "worker output hash does not match the typed receipt"
    expected_size = receipt.get("output_size")
    if not isinstance(expected_size, int) or output.stat().st_size != expected_size:
        return False, "worker output size does not match the typed receipt"
    return True, "typed worker receipt and fresh output agree"


def build_report(
    *,
    receipt_path: str,
    ledger_path: str,
    attempt_id: str,
    scope: str,
    packet_identity: str,
    reviewed_input_identity: str,
    parent_receipt_identity: str,
    expected_execution_mode: str = "file-backed-worker",
) -> dict[str, Any]:
    receipt_file, receipt = _read_json(receipt_path, "receipt_file")
    ledger_file, ledger_payload = _read_json(ledger_path, "ledger_file")
    try:
        ledger = DeliveryLedger.from_dict(ledger_payload)
        attempt = ledger.require(attempt_id)
    except DeliveryError as exc:
        raise ReportError(f"delivery ledger is invalid or missing the attempt: {exc}") from exc

    receipt_ok, receipt_reason = _validate_receipt(
        receipt,
        attempt=attempt,
        expected_execution_mode=expected_execution_mode,
    )
    provenance = {
        "scope": scope,
        "packet_identity": packet_identity,
        "reviewed_input_identity": reviewed_input_identity,
        "parent_receipt_identity": parent_receipt_identity,
        "attempt_id": attempt.attempt_id,
        "attempt_scope": attempt.scope,
        "attempt_packet_identity": attempt.packet_identity,
        "attempt_parent_receipt_identity": attempt.parent_receipt_identity,
    }
    provenance_ok = (
        attempt.scope == scope
        and attempt.packet_identity == packet_identity
        and attempt.reviewed_input_identity == reviewed_input_identity
        and attempt.parent_receipt_identity == parent_receipt_identity
    )
    ledger_ok = (
        attempt.state == FINDINGS_RECEIVED
        and attempt.delivery_complete
        and attempt.findings_identity == receipt.get("output_sha256")
    )
    receipt_provenance_ok = receipt_ok
    eligible = receipt_ok and provenance_ok and ledger_ok
    if not receipt_ok:
        reason = receipt_reason
    elif not provenance_ok:
        reason = "delivery ledger provenance does not match the consumer request"
    elif not ledger_ok:
        reason = (
            f"delivery ledger state/hash is not a matching findings-received record: "
            f"state={attempt.state!r}, findings_identity={attempt.findings_identity!r}"
        )
    else:
        reason = "typed worker receipt and matching delivery ledger permit approval"
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "execution_mode": "file-backed-worker",
        "backend": receipt.get("backend"),
        "receipt_schema_version": receipt.get("schema_version"),
        "receipt_status": receipt.get("status"),
        "receipt_path": str(receipt_file),
        "ledger_path": str(ledger_file),
        "delivery_state": attempt.state,
        "approval_eligible": eligible,
        "provenance_ok": provenance_ok,
        "receipt_ok": receipt_ok,
        "ledger_ok": ledger_ok,
        "receipt_provenance_ok": receipt_provenance_ok,
        "findings_identity": attempt.findings_identity,
        "receipt_output_sha256": receipt.get("output_sha256"),
        "provenance": provenance,
        "reason": reason,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consume a typed reviewer worker result.")
    parser.add_argument("--receipt-file", required=True)
    parser.add_argument("--ledger-file", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--packet-identity", required=True)
    parser.add_argument("--reviewed-input-identity", required=True)
    parser.add_argument("--parent-receipt-identity", required=True)
    parser.add_argument(
        "--expected-execution-mode",
        choices=("file-backed-worker", "typed-subagent"),
        default="file-backed-worker",
    )
    args = parser.parse_args(argv)
    try:
        report = build_report(
            receipt_path=args.receipt_file,
            ledger_path=args.ledger_file,
            attempt_id=args.attempt_id,
            scope=args.scope,
            packet_identity=args.packet_identity,
            reviewed_input_identity=args.reviewed_input_identity,
            parent_receipt_identity=args.parent_receipt_identity,
            expected_execution_mode=args.expected_execution_mode,
        )
    except ReportError as exc:
        report = {
            "schema_version": REPORT_SCHEMA_VERSION,
            "execution_mode": "file-backed-worker",
            "approval_eligible": False,
            "reason": str(exc),
        }
        emit_yaml(report)
        return 1
    emit_yaml(report)
    return 0 if report["approval_eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
