"""Consumer proof: receipt success alone cannot become reviewer approval."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from skills.shared.scripts import reviewer_delivery

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/shared/scripts/reviewer_worker_report.py"


def _receipt(tmp_path: Path, *, status: str = "succeeded") -> Path:
    output = tmp_path / "result.json"
    output.write_text('{"verdict":"PASS"}\n', encoding="utf-8")
    payload = {
        "schema_version": "charness.reviewer_worker.v1",
        "run_id": "worker-1",
        "backend": "codex_exec",
        "terminal": True,
        "status": status,
        "output_fresh": status == "succeeded",
        "output_file": str(output),
        "output_size": output.stat().st_size,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
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
    )
    if findings:
        attempt.record_findings(
            scope="scope-1",
            packet_identity="packet-1",
            parent_receipt_identity="parent-1",
            findings_identity="findings-1",
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
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["approval_eligible"] is True
    assert payload["execution_mode"] == "file-backed-worker"
    assert payload["delivery_state"] == "findings-received"


def test_success_receipt_without_findings_is_not_approval(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path, findings=False)
    result = _run(tmp_path, receipt, ledger)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["approval_eligible"] is False
    assert "findings-received" in payload["reason"]


def test_receipt_failure_cannot_be_laundered_by_findings_ledger(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path, status="timed-out")
    ledger, _ = _ledger(tmp_path)
    result = _run(tmp_path, receipt, ledger)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["approval_eligible"] is False
    assert payload["receipt_ok"] is False


def test_provenance_mismatch_is_not_approval(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    ledger, _ = _ledger(tmp_path)
    result = _run(tmp_path, receipt, ledger, scope="wrong-scope")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["provenance_ok"] is False
    assert payload["approval_eligible"] is False
