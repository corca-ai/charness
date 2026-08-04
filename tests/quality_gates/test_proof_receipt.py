from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.proof_receipt import (
    ReceiptContractError,
    _parse_recovery_spec,
    _recovery,
    closeout_receipt,
    quality_receipt,
    render_closeout_verdict,
    render_quality_summary,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("status", "path", "reason", "message"),
    [
        ("unknown", None, None, "unknown recovery status"),
        ("available", None, None, "available recovery requires a path"),
        ("unavailable", "failure.log", None, "unavailable recovery must not advertise a path"),
        ("not-applicable", "failure.log", None, "not-applicable recovery must not advertise a path"),
        ("unavailable", None, None, "unavailable recovery requires a reason"),
    ],
)
def test_recovery_contract_rejects_invalid_shapes(
    status: str, path: str | None, reason: str | None, message: str
) -> None:
    with pytest.raises(ReceiptContractError, match=message):
        _recovery(status, path=path, reason=reason)


def test_recovery_contract_accepts_explicit_path_and_reason_specs() -> None:
    assert _parse_recovery_spec("not-applicable").as_dict() == {"status": "not-applicable"}
    assert _parse_recovery_spec("available:failure.log").as_dict() == {
        "status": "available",
        "path": "failure.log",
    }
    assert _parse_recovery_spec("unavailable:inspect the captured output").as_dict() == {
        "status": "unavailable",
        "reason": "inspect the captured output",
    }


def test_receipt_contract_rejects_invalid_status_and_mismatched_adverse_recovery() -> None:
    with pytest.raises(ReceiptContractError, match="unknown quality status"):
        quality_receipt(status="unknown", measured_scope=[], effective_exit_code=1)
    with pytest.raises(ReceiptContractError, match="each adverse subject"):
        quality_receipt(
            status="fail",
            measured_scope=["tests"],
            adverse_subjects=["tests"],
            recoveries=[],
            effective_exit_code=1,
        )


def test_quality_summary_renders_not_applicable_and_unproven_subjects() -> None:
    receipt = quality_receipt(
        status="unestablished",
        measured_scope=["tests"],
        adverse_subjects=["not applicable finding"],
        recoveries=[_recovery("not-applicable", reason="not in this scope")],
        unproven_subjects=["provider behavior"],
        effective_exit_code=0,
        details={"passed": 1, "failed": 0, "elapsed": "3ms"},
    )

    assert render_quality_summary(receipt) == (
        "Quality summary: 1 passed, 0 failed (FAILED: not applicable finding), "
        "1 UNPROVEN (UNPROVEN: provider behavior) (ran; established nothing, or only part "
        "of its scope), total 3ms"
    )


def test_closeout_rejects_unknown_status() -> None:
    with pytest.raises(ReceiptContractError, match="unknown closeout status"):
        closeout_receipt({"status": "unknown"}, effective_exit_code=1)


def test_quality_receipt_keeps_mixed_recovery_and_actual_exit() -> None:
    receipt = quality_receipt(
        status="fail",
        measured_scope=["lint", "tests"],
        adverse_subjects=["lint", "tests"],
        recoveries=[
            _recovery("available", path=".charness/quality-failure-logs/lint.log"),
            _recovery("unavailable", reason="copy failed"),
        ],
        effective_exit_code=1,
        details={"passed": 0, "failed": 2, "elapsed": "12ms"},
    )

    data = receipt.as_dict()
    assert data["measured_scope"] == ["lint", "tests"]
    assert data["effective_exit_code"] == 1
    assert data["adverse_subjects"][0]["recovery"] == {
        "status": "available",
        "path": ".charness/quality-failure-logs/lint.log",
    }
    assert data["adverse_subjects"][1]["recovery"] == {
        "status": "unavailable",
        "reason": "copy failed",
    }
    assert render_quality_summary(receipt) == (
        "Quality summary: 0 passed, 2 failed (FAILED: lint "
        "[log: .charness/quality-failure-logs/lint.log]; tests [log unavailable]), total 12ms"
    )


def test_closeout_block_without_command_names_recorded_cause() -> None:
    receipt = closeout_receipt(
        {
            "status": "blocked",
            "changed_paths": ["README.md"],
            "unmatched_paths": [],
            "executed_commands": [],
            "error": "changed paths are not covered by the surfaces manifest",
        },
        effective_exit_code=1,
    )

    assert receipt.cause == "changed paths are not covered by the surfaces manifest"
    assert receipt.adverse_subjects[0].subject == receipt.cause
    assert render_closeout_verdict(receipt) == (
        "Closeout verdict: blocked (BLOCKED: changed paths are not covered by the surfaces manifest)"
    )


def test_closeout_rejects_adverse_state_without_cause() -> None:
    with pytest.raises(ReceiptContractError, match="requires a recorded cause"):
        closeout_receipt(
            {"status": "failed", "changed_paths": [], "executed_commands": []},
            effective_exit_code=1,
        )


def test_quality_cli_writes_explicit_opt_in_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "receipt.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "proof_receipt.py"),
            "quality",
            "--status",
            "pass",
            "--effective-exit-code",
            "0",
            "--passed",
            "1",
            "--failed",
            "0",
            "--elapsed",
            "4ms",
            "--measured-scope",
            "lint",
            "--json-path",
            str(receipt_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Quality summary: 1 passed, 0 failed, total 4ms"
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["surface"] == "quality"
    assert payload["effective_exit_code"] == 0
    assert payload["measured_scope"] == ["lint"]


def test_quality_cli_write_failure_precedes_final_human_line(tmp_path: Path) -> None:
    blocked_target = tmp_path / "existing-directory"
    blocked_target.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "proof_receipt.py"),
            "quality",
            "--status",
            "pass",
            "--effective-exit-code",
            "0",
            "--passed",
            "1",
            "--failed",
            "0",
            "--elapsed",
            "4ms",
            "--json-path",
            str(blocked_target),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "could not write" in result.stderr
    assert result.stdout.splitlines()[-1] == "Quality summary: 1 passed, 0 failed, total 4ms"


def test_closeout_cause_precedence_prefers_recorded_error_then_producer() -> None:
    command = {"phase": "verify", "command": "python3 broken.py", "returncode": 1}
    error_receipt = closeout_receipt(
        {
            "status": "failed",
            "changed_paths": [],
            "executed_commands": [command],
            "error": "recorded closeout error",
            "mutation_coverage_changed_line_proof": {"status": "failed", "error": "producer error"},
        },
        effective_exit_code=1,
    )
    assert error_receipt.cause == "recorded closeout error"
    assert render_closeout_verdict(error_receipt) == (
        "Closeout verdict: failed (CAUSE: recorded closeout error; FAILED: python3 broken.py)"
    )

    producer_receipt = closeout_receipt(
        {
            "status": "failed",
            "changed_paths": [],
            "executed_commands": [command],
            "mutation_coverage_changed_line_proof": {"status": "failed", "error": "producer error"},
        },
        effective_exit_code=1,
    )
    assert producer_receipt.cause == "producer error"
    assert "CAUSE: producer error" in render_closeout_verdict(producer_receipt)
