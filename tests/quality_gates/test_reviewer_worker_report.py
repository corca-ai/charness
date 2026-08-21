"""Consumer proof: receipt success alone cannot become reviewer approval."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

from skills.shared.scripts import reviewer_delivery

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/shared/scripts/reviewer_worker_report.py"


def _receipt(tmp_path: Path, *, status: str = "succeeded") -> Path:
    output = tmp_path / "result.json"
    output.write_text(
        '{"verdict":"PASS","packet_sha256":"packet-1",'
        '"reviewed_input_identity_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}\n',
        encoding="utf-8",
    )
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
        "packet_identity": "packet-1",
        "reviewed_input_identity": "a" * 64,
        "parent_receipt_identity": "parent-1",
        "execution_mode": "file-backed-worker",
        "prompt_sha256": "b" * 64,
        "schema_sha256": "c" * 64,
    }
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _ledger(tmp_path: Path, *, findings: bool = True) -> tuple[Path, str]:
    path = tmp_path / "delivery.json"
    ledger = reviewer_delivery.DeliveryLedger.empty()
    attempt = ledger.start(
        attempt_id="attempt-1",
        scope="scope-1",
        packet_identity="packet-1",
        parent_receipt_identity="parent-1",
        boundary_fingerprint="boundary-1",
        reviewed_input_identity="a" * 64,
        execution_mode="file-backed-worker",
        backend="codex_exec",
        prompt_sha256="b" * 64,
        schema_sha256="c" * 64,
    )
    if findings:
        attempt.record_findings(
            scope="scope-1",
            packet_identity="packet-1",
            parent_receipt_identity="parent-1",
            findings_identity=hashlib.sha256((tmp_path / "result.json").read_bytes()).hexdigest(),
            recorded_at="2026-08-21T00:00:00Z",
        )
    path.write_text(json.dumps(ledger.to_dict()), encoding="utf-8")
    return path, attempt.attempt_id


def _run(tmp_path: Path, receipt: Path, ledger: Path, *, scope: str = "scope-1") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
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
            "packet-1",
            "--reviewed-input-identity",
            "a" * 64,
            "--parent-receipt-identity",
            "parent-1",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
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
