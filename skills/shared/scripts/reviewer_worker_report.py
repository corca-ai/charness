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
import importlib.util
import json
from pathlib import Path
from typing import Any

try:
    from reviewer_delivery import DeliveryError, DeliveryLedger
except ImportError:
    from skills.shared.scripts.reviewer_delivery import DeliveryError, DeliveryLedger

try:
    from reviewer_capability import (
        CapabilityError,
        validate_receipt_capabilities,
        validate_result_capability_non_claims,
    )
except ImportError:
    from skills.shared.scripts.reviewer_capability import (
        CapabilityError,
        validate_receipt_capabilities,
        validate_result_capability_non_claims,
    )

try:
    from reviewer_output import emit_yaml
except ImportError:
    from skills.shared.scripts.reviewer_output import emit_yaml

try:
    from provenance_contract import BoundaryContractError, require_bound_fields
except ImportError:
    from skills.shared.scripts.provenance_contract import (
        BoundaryContractError,
        require_bound_fields,
    )

try:
    from reviewer_partial_output import validate_receipt_output
except ImportError:
    from skills.shared.scripts.reviewer_partial_output import validate_receipt_output

REPORT_SCHEMA_VERSION = "charness.reviewer_worker_report.v1"
WORKER_SCHEMA_VERSION = "charness.reviewer_worker.v1"
SUCCESS = "succeeded"
FINDINGS_RECEIVED = "findings-received"


class ReportError(ValueError):
    """Input cannot support a trustworthy consumer report."""


def _load_result_contract():
    candidate = Path(__file__).resolve().with_name("reviewer_result_contract.py")
    spec = importlib.util.spec_from_file_location("charness_reviewer_result_contract", candidate)
    if spec is None or spec.loader is None:
        raise ReportError(f"canonical result contract is unavailable: {candidate}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_result_output(receipt: dict[str, Any], attempt: Any) -> tuple[bool, str]:
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
    try:
        result = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return False, f"worker output is not readable JSON: {exc}"
    if not isinstance(result, dict):
        return False, "worker output must be a JSON object"
    if result.get("packet_sha256") != attempt.packet_identity:
        return False, "worker result packet_sha256 does not match the delivery attempt"
    if result.get("reviewed_input_identity_sha256") != attempt.reviewed_input_identity:
        return False, "worker result reviewed_input_identity_sha256 does not match the delivery attempt"
    try:
        validate_result_capability_non_claims(result, receipt)
    except CapabilityError as exc:
        return False, f"worker result capability non-claims are not approval-eligible: {exc}"
    return True, "typed worker receipt and fresh output agree"


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


def _receipt_join_error(receipt: dict[str, Any], attempt: Any) -> str | None:
    joins = {
        "attempt_id": attempt.attempt_id,
        "scope": attempt.scope,
        "packet_identity": attempt.packet_identity,
        "reviewed_input_identity": attempt.reviewed_input_identity,
        "parent_receipt_identity": attempt.parent_receipt_identity,
        "boundary_mode": attempt.boundary_mode,
        "boundary_fingerprint": attempt.boundary_fingerprint,
        "execution_mode": attempt.execution_mode,
        "backend": attempt.backend,
        "prompt_sha256": attempt.prompt_sha256,
        "schema_sha256": attempt.schema_sha256,
        "capability_launch_envelope_sha256": attempt.capability_launch_envelope_sha256,
    }
    for field, expected in joins.items():
        observed = receipt.get(field)
        if field == "boundary_mode" and observed is None and receipt.get("boundary_fingerprint") is not None:
            # Receipts emitted before boundary_mode was introduced remain
            # readable; their non-empty fingerprint unambiguously identifies
            # the old shared-tree path.
            observed = "shared-tree-fingerprint"
        if expected is None:
            if field == "boundary_fingerprint" and observed is None:
                continue
            return f"delivery attempt has no bound {field}"
        if observed != expected:
            return f"worker receipt {field} does not match the delivery attempt"
    return None


def _validate_receipt(
    receipt: dict[str, Any],
    *,
    attempt: Any,
    expected_execution_mode: str,
    receipt_path: Path,
) -> tuple[bool, str]:
    if expected_execution_mode != "file-backed-worker":
        return False, "the file-backed consumer cannot approve a typed-subagent execution"
    if receipt.get("schema_version") != WORKER_SCHEMA_VERSION:
        return False, "worker receipt schema_version is not the Charness worker schema"
    if receipt.get("terminal") is not True:
        return False, "worker receipt is not terminal"
    if receipt.get("status") != SUCCESS:
        return False, f"worker receipt status is {receipt.get('status')!r}"
    if receipt.get("exit_code") != 0:
        return False, "successful worker receipt must carry exit_code 0"
    join_error = _receipt_join_error(receipt, attempt)
    if join_error is not None:
        return False, join_error
    producer_joins = {
        "output_file": attempt.output_file,
        "receipt_file": attempt.receipt_file,
        "producer_run_id": attempt.producer_run_id,
    }
    try:
        require_bound_fields("reviewer_delivery", producer_joins)
    except BoundaryContractError as exc:
        return False, str(exc)
    expected_output = Path(attempt.output_file).expanduser().resolve()
    if Path(str(receipt.get("output_file", ""))).expanduser().resolve() != expected_output:
        return False, "worker receipt output_file does not match the producer binding"
    expected_receipt = Path(attempt.receipt_file).expanduser().resolve()
    if receipt_path.expanduser().resolve() != expected_receipt:
        return False, "worker receipt receipt_file does not match the producer binding"
    if receipt.get("run_id") != attempt.producer_run_id:
        return False, "worker receipt run_id does not match the producer binding"
    try:
        validate_receipt_capabilities(receipt, attempt_id=attempt.attempt_id)
    except CapabilityError as exc:
        return False, f"worker receipt capability envelope is not approval-eligible: {exc}"
    return _validate_result_output(receipt, attempt)


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
        receipt_path=receipt_file,
    )
    partial_output, partial_reason = validate_receipt_output(receipt, attempt=attempt)
    semantic_result: dict[str, Any] | None = None
    semantic_reason = "canonical bounded-review result is not approval-eligible"
    if receipt_ok:
        try:
            semantic_result = _load_result_contract().validate_bounded_result(
                Path(str(receipt["output_file"])).expanduser().resolve(),
                packet_identity=packet_identity,
                reviewed_input_identity=reviewed_input_identity,
                require_pass=False,
            )
            semantic_reason = (
                "typed reviewer verdict is not pass: "
                f"{semantic_result.get('verdict')!r}"
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            semantic_result = None
            semantic_reason = str(exc)
    provenance = {
        "scope": scope,
        "packet_identity": packet_identity,
        "reviewed_input_identity": reviewed_input_identity,
        "parent_receipt_identity": parent_receipt_identity,
        "attempt_id": attempt.attempt_id,
        "attempt_scope": attempt.scope,
        "attempt_packet_identity": attempt.packet_identity,
        "attempt_parent_receipt_identity": attempt.parent_receipt_identity,
        "result_packet_identity": packet_identity,
        "result_reviewed_input_identity": reviewed_input_identity,
        "boundary_mode": attempt.boundary_mode,
        "boundary_fingerprint": attempt.boundary_fingerprint,
        "execution_mode": attempt.execution_mode,
        "backend": attempt.backend,
        "prompt_sha256": attempt.prompt_sha256,
        "schema_sha256": attempt.schema_sha256,
        "capability_launch_envelope_sha256": attempt.capability_launch_envelope_sha256,
        "capability_non_claims_sha256": receipt.get("capability_non_claims_sha256"),
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
    semantic_ok = semantic_result is not None and semantic_result.get("verdict") == "pass"
    # This is the pre-terminalization collection gate used by the runner.  It
    # deliberately does not require a pass verdict: a typed ``block`` result
    # is still a delivered finding, while a malformed result or receipt must
    # leave a typed collection failure that can be retried.
    collection_ready = receipt_ok and semantic_result is not None and provenance_ok
    eligible = receipt_ok and semantic_ok and provenance_ok and ledger_ok
    if not receipt_ok:
        reason = receipt_reason
    elif not provenance_ok:
        reason = "delivery ledger provenance does not match the consumer request"
    elif not semantic_ok:
        reason = semantic_reason
    elif not ledger_ok:
        reason = (
            f"delivery ledger state/hash is not a matching findings-received record: "
            f"state={attempt.state!r}, findings_identity={attempt.findings_identity!r}"
        )
    else:
        reason = "typed worker receipt and matching delivery ledger permit approval"
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "execution_mode": attempt.execution_mode,
        "backend": receipt.get("backend"),
        "capability_status": receipt.get("capability_status"),
        "capability_envelope_sha256": receipt.get("capability_envelope_sha256"),
        "capability_launch_envelope_sha256": receipt.get("capability_launch_envelope_sha256"),
        "capability_collection_envelope_sha256": receipt.get("capability_collection_envelope_sha256"),
        "capability_non_claims": receipt.get("capability_non_claims"),
        "capability_non_claims_sha256": receipt.get("capability_non_claims_sha256"),
        "scope": attempt.scope,
        "attempt_id": attempt.attempt_id,
        "boundary_mode": attempt.boundary_mode,
        "boundary_fingerprint": attempt.boundary_fingerprint,
        "prompt_sha256": attempt.prompt_sha256,
        "schema_sha256": attempt.schema_sha256,
        "receipt_schema_version": receipt.get("schema_version"),
        "receipt_status": receipt.get("status"),
        "receipt_path": str(receipt_file),
        "ledger_path": str(ledger_file),
        # Retain the producer join in the final consumer's typed carrier.  The
        # receipt/ledger checks above prove this identity before a verdict is
        # considered, but dropping it here would make the durable report unable
        # to answer which producer run its approval (or refusal) describes.
        "producer_run_id": attempt.producer_run_id,
        "producer_binding": {
            "output_file": attempt.output_file,
            "receipt_file": attempt.receipt_file,
            "producer_run_id": attempt.producer_run_id,
        },
        "delivery_state": attempt.state,
        "approval_eligible": eligible,
        "provenance_ok": provenance_ok,
        "receipt_ok": receipt_ok,
        "ledger_ok": ledger_ok,
        "result_schema_ok": semantic_result is not None,
        "collection_ready": collection_ready,
        "partial_output": partial_output,
        "partial_output_ok": partial_output is not None,
        "review_verdict": semantic_result.get("verdict") if semantic_result else None,
        "receipt_provenance_ok": receipt_provenance_ok,
        "findings_identity": attempt.findings_identity,
        "receipt_output_sha256": receipt.get("output_sha256"),
        "packet_identity": packet_identity,
        "reviewed_input_identity": reviewed_input_identity,
        "parent_receipt_identity": parent_receipt_identity,
        "provenance": provenance,
        "reason": reason,
        "partial_output_reason": partial_reason,
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
            "execution_mode": args.expected_execution_mode,
            "approval_eligible": False,
            "receipt_ok": False,
            "ledger_ok": False,
            "provenance_ok": False,
            "reason": str(exc),
        }
        emit_yaml(report)
        return 1
    emit_yaml(report)
    return 0 if report["approval_eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
