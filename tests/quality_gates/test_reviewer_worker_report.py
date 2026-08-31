"""Consumer proof: receipt success alone cannot become reviewer approval."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

# provenance-contract fixture: reviewer_delivery
import pytest
import yaml

from skills.shared.scripts import reviewer_delivery
from tests.quality_gates.reviewer_capability_support import (
    non_claims_sha256,
    receipt_capability_fields,
    result_capability_fields,
    target_non_claim,
    unavailable_optional_capability,
)
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/shared/scripts/reviewer_worker_report.py"


def _receipt(tmp_path: Path, *, status: str = "succeeded", capability: dict | None = None) -> Path:
    capability = capability or unavailable_optional_capability("attempt-1")
    output = tmp_path / "result.json"
    result = {
        "kind": "charness.bounded_review.v1",
        "lens": "report test",
        "verdict": "pass",
        "findings": [],
        "counterweight_triage": [],
        "next_move": "test",
        "non_claims": ["test"],
        "packet_sha256": "a" * 64,
        "reviewed_input_identity_sha256": "a" * 64,
        **result_capability_fields(capability),
    }
    output.write_text(json.dumps(result) + "\n", encoding="utf-8")
    payload = {
        "schema_version": "charness.reviewer_worker.v1",
        "run_id": "worker-1",
        "backend": "codex_exec",
        "terminal": True,
        "status": status,
        "exit_code": 0 if status == "succeeded" else 124,
        "output_fresh": status == "succeeded",
        "output_file": str(output),
        "output_size": output.stat().st_size,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "attempt_id": "attempt-1",
        "scope": "scope-1",
        "packet_identity": "a" * 64,
        "reviewed_input_identity": "a" * 64,
        "parent_receipt_identity": "parent-1",
        "boundary_fingerprint": "boundary-1",
        "execution_mode": "file-backed-worker",
        "prompt_sha256": "b" * 64,
        "schema_sha256": "c" * 64,
    }
    payload.update(receipt_capability_fields("attempt-1", payload=capability))
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _ledger(
    tmp_path: Path, *, findings: bool = True, capability: dict | None = None
) -> tuple[Path, str]:
    capability = capability or unavailable_optional_capability("attempt-1")
    path = tmp_path / "delivery.json"
    ledger = reviewer_delivery.DeliveryLedger.empty()
    attempt = ledger.start(
        attempt_id="attempt-1",
        scope="scope-1",
        packet_identity="a" * 64,
        parent_receipt_identity="parent-1",
        boundary_fingerprint="boundary-1",
        reviewed_input_identity="a" * 64,
        execution_mode="file-backed-worker",
        backend="codex_exec",
        prompt_sha256="b" * 64,
        schema_sha256="c" * 64,
        capability_launch_envelope_sha256=receipt_capability_fields("attempt-1", payload=capability)[
            "capability_launch_envelope_sha256"
        ],
        output_file=str((tmp_path / "result.json").resolve()),
        receipt_file=str((tmp_path / "receipt.json").resolve()),
        producer_run_id="worker-1",
    )
    if findings:
        attempt.record_findings(
            scope="scope-1",
            packet_identity="a" * 64,
            parent_receipt_identity="parent-1",
            findings_identity=hashlib.sha256((tmp_path / "result.json").read_bytes()).hexdigest(),
            recorded_at="2026-08-21T00:00:00Z",
        )
    path.write_text(json.dumps(ledger.to_dict()), encoding="utf-8")
    return path, attempt.attempt_id


def _run(tmp_path: Path, receipt: Path, ledger: Path, *, scope: str = "scope-1") -> subprocess.CompletedProcess[str]:
    return run_script(
        str(SCRIPT),
        "--receipt-file",
        str(receipt),
        "--ledger-file",
        str(ledger),
        "--attempt-id",
        "attempt-1",
        "--scope",
        scope,
        "--packet-identity",
        "a" * 64,
        "--reviewed-input-identity",
        "a" * 64,
        "--parent-receipt-identity",
        "parent-1",
        cwd=tmp_path,
    )


def test_matching_typed_receipt_and_findings_ledger_is_approval_eligible(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path)
    result = _run(tmp_path, receipt, ledger)
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0
    assert payload["approval_eligible"] is True
    assert payload["execution_mode"] == "file-backed-worker"
    assert payload["delivery_state"] == "findings-received"
    assert payload["producer_run_id"] == "worker-1"
    assert payload["producer_binding"] == {
        "output_file": str((tmp_path / "result.json").resolve()),
        "receipt_file": str((tmp_path / "receipt.json").resolve()),
        "producer_run_id": "worker-1",
    }


def test_timed_out_partial_output_is_reported_without_approval(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path, status="timed-out")
    ledger_path, _ = _ledger(tmp_path, findings=False)
    output = tmp_path / "result.json"
    partial = output.with_name("result.json.partial")
    partial.write_text('{"partial":true}\n', encoding="utf-8")
    receipt_payload = json.loads(receipt.read_text(encoding="utf-8"))
    receipt_payload["partial_output"] = {
        "schema_version": "charness.reviewer_partial_output.v1",
        "kind": "backend-output",
        "path": str(partial),
        "bytes": partial.stat().st_size,
        "sha256": hashlib.sha256(partial.read_bytes()).hexdigest(),
    }
    receipt.write_text(json.dumps(receipt_payload), encoding="utf-8")

    ledger_payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger = reviewer_delivery.DeliveryLedger.from_dict(ledger_payload)
    ledger.require("attempt-1").record_partial(
        partial_output=receipt_payload["partial_output"],
        recorded_at="2026-08-21T00:00:00Z",
    )
    ledger_path.write_text(json.dumps(ledger.to_dict()), encoding="utf-8")

    result = _run(tmp_path, receipt, ledger_path)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert report["delivery_state"] == "partial"
    assert report["partial_output_ok"] is True
    assert report["partial_output"] == receipt_payload["partial_output"]
    assert report["approval_eligible"] is False


def test_producer_output_join_is_checked_at_collection(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path)
    payload = json.loads(ledger.read_text(encoding="utf-8"))
    payload["attempts"][0].update(
        {
            "output_file": str((tmp_path / "result.json").resolve()),
            "receipt_file": str(receipt.resolve()),
            "producer_run_id": "worker-1",
        }
    )
    ledger.write_text(json.dumps(payload), encoding="utf-8")
    result = _run(tmp_path, receipt, ledger)
    assert result.returncode == 0

    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["run_id"] = "foreign-run"
    receipt.write_text(json.dumps(payload), encoding="utf-8")
    rejected = _run(tmp_path, receipt, ledger)
    report = yaml.safe_load(rejected.stdout)
    assert rejected.returncode == 1
    assert report["receipt_ok"] is False
    assert "run_id" in report["reason"]


@pytest.mark.parametrize("field", ["output_file", "receipt_file", "producer_run_id"])
def test_missing_producer_binding_is_not_approval_eligible(tmp_path: Path, field: str) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path)
    payload = json.loads(ledger.read_text(encoding="utf-8"))
    payload["attempts"][0].pop(field)
    ledger.write_text(json.dumps(payload), encoding="utf-8")
    result = _run(tmp_path, receipt, ledger)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert report["approval_eligible"] is False
    assert report["receipt_ok"] is False
    assert field in report["reason"]


@pytest.mark.parametrize("mutation", ["missing", "contradictory", "rebound"])
def test_optional_non_claim_result_mutations_are_not_approval_eligible(
    tmp_path: Path, mutation: str
) -> None:
    capability = unavailable_optional_capability("attempt-1")
    receipt = _receipt(tmp_path, capability=capability)
    ledger, _ = _ledger(tmp_path, capability=capability)
    output = tmp_path / "result.json"
    result = json.loads(output.read_text(encoding="utf-8"))
    if mutation == "missing":
        result.pop("capability_non_claims")
    elif mutation == "contradictory":
        claim = dict(capability["capability_non_claims"][0])
        claim["disposition"] = "unavailable"
        result["capability_non_claims"] = [claim]
    else:
        result["capability_non_claims"] = [target_non_claim("github:issue:690", "unproved")]
    if mutation != "contradictory":
        result["capability_non_claims_sha256"] = non_claims_sha256(result.get("capability_non_claims", []))
    output.write_text(json.dumps(result) + "\n", encoding="utf-8")
    output_hash = hashlib.sha256(output.read_bytes()).hexdigest()
    receipt_payload = json.loads(receipt.read_text(encoding="utf-8"))
    receipt_payload["output_sha256"] = output_hash
    receipt_payload["output_size"] = output.stat().st_size
    receipt.write_text(json.dumps(receipt_payload), encoding="utf-8")
    ledger_payload = json.loads(ledger.read_text(encoding="utf-8"))
    ledger_payload["attempts"][0]["findings_identity"] = output_hash
    ledger_payload["attempts"][0]["history"][-1]["findings_identity"] = output_hash
    ledger.write_text(json.dumps(ledger_payload), encoding="utf-8")

    result_process = _run(tmp_path, receipt, ledger)
    report = yaml.safe_load(result_process.stdout)
    assert result_process.returncode == 1
    assert report["approval_eligible"] is False
    assert report["receipt_ok"] is False
    assert "non-claim" in report["reason"]


def test_success_receipt_without_capability_denial_is_not_approval(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload.pop("effective_capabilities")
    receipt.write_text(json.dumps(payload), encoding="utf-8")
    ledger, _ = _ledger(tmp_path)
    result = _run(tmp_path, receipt, ledger)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert report["approval_eligible"] is False
    assert report["receipt_ok"] is False
    assert "capability envelope" in report["reason"]


def test_receipt_capability_rebinding_cannot_escape_the_delivery_attempt(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload.update(receipt_capability_fields("attempt-1", target="github:issue:690"))
    receipt.write_text(json.dumps(payload), encoding="utf-8")
    ledger, _ = _ledger(tmp_path)

    result = _run(tmp_path, receipt, ledger)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert report["approval_eligible"] is False
    assert report["receipt_ok"] is False
    assert "capability_launch_envelope_sha256" in report["reason"]


def test_success_receipt_without_findings_is_not_approval(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path, findings=False)
    result = _run(tmp_path, receipt, ledger)
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["approval_eligible"] is False
    assert "findings-received" in payload["reason"]


def test_receipt_failure_cannot_be_laundered_by_findings_ledger(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path, status="timed-out")
    ledger, _ = _ledger(tmp_path)
    result = _run(tmp_path, receipt, ledger)
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["approval_eligible"] is False
    assert payload["receipt_ok"] is False


def test_provenance_mismatch_is_not_approval(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path)
    result = _run(tmp_path, receipt, ledger, scope="wrong-scope")
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["provenance_ok"] is False
    assert payload["approval_eligible"] is False


def test_foreign_receipt_cannot_pair_with_current_attempt(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["attempt_id"] = "foreign-attempt"
    receipt.write_text(json.dumps(payload), encoding="utf-8")
    ledger, _ = _ledger(tmp_path)
    result = _run(tmp_path, receipt, ledger)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert report["receipt_ok"] is False
    assert report["approval_eligible"] is False


def test_findings_identity_must_match_worker_result_hash(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path)
    payload = json.loads(ledger.read_text(encoding="utf-8"))
    payload["attempts"][0]["findings_identity"] = "d" * 64
    ledger.write_text(json.dumps(payload), encoding="utf-8")
    result = _run(tmp_path, receipt, ledger)
    report = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert report["ledger_ok"] is False
    assert report["approval_eligible"] is False
