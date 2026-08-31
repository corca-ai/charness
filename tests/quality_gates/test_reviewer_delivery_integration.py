"""Process-boundary proof for the durable reviewer delivery state packet."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/shared/scripts/reviewer_delivery.py"


def _run(ledger: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_script(str(SCRIPT), "--ledger", str(ledger), *args, cwd=ROOT)


def _payload(result: subprocess.CompletedProcess[str]) -> dict:
    return yaml.safe_load(result.stdout)


def test_cli_keeps_interrupted_attempt_and_retry_as_distinct_records(tmp_path: Path) -> None:
    ledger = tmp_path / "review" / "delivery.json"
    started = _run(
        ledger,
        "start",
        "--attempt-id",
        "a1",
        "--scope",
        "scope-sha",
        "--packet-identity",
        "packet-sha",
        "--parent-receipt-identity",
        "receipt-a1",
        "--boundary-fingerprint",
        "fingerprint-a1",
        "--recorded-at",
        "2026-08-21T00:00:00Z",
    )
    assert started.returncode == 0, started.stderr

    interrupted = _run(
        ledger,
        "transition",
        "--attempt-id",
        "a1",
        "--state",
        "interrupted",
        "--signal",
        "host signal: interrupted",
        "--recorded-at",
        "2026-08-21T00:00:10Z",
    )
    assert interrupted.returncode == 0, interrupted.stderr
    assert _payload(interrupted)["delivery_complete"] is False

    retried = _run(
        ledger,
        "retry",
        "--from-attempt",
        "a1",
        "--attempt-id",
        "a2",
        "--recorded-at",
        "2026-08-21T00:02:00Z",
    )
    assert retried.returncode == 0, retried.stderr
    shown = _run(ledger, "show")
    assert shown.returncode == 0, shown.stderr
    attempts = _payload(shown)["ledger"]["attempts"]
    assert [attempt["attempt_id"] for attempt in attempts] == ["a1", "a2"]
    assert attempts[0]["state"] == "interrupted"
    assert attempts[1]["retry_of"] == "a1"


def test_cli_requires_matching_provenance_before_findings_received(tmp_path: Path) -> None:
    ledger = tmp_path / "delivery.json"
    assert _run(
        ledger,
        "start",
        "--attempt-id",
        "a1",
        "--scope",
        "scope-sha",
        "--packet-identity",
        "packet-sha",
        "--parent-receipt-identity",
        "receipt-a1",
        "--boundary-fingerprint",
        "fingerprint-a1",
    ).returncode == 0
    foreign = _run(
        ledger,
        "findings",
        "--attempt-id",
        "a1",
        "--scope",
        "foreign-scope",
        "--packet-identity",
        "packet-sha",
        "--parent-receipt-identity",
        "receipt-a1",
        "--findings-identity",
        "f" * 64,
    )
    assert foreign.returncode == 1
    result = _payload(foreign)
    assert result["ok"] is False
    assert result["attempt"]["state"] == "non-delivery-unknown"
    assert result["delivery_complete"] is False

def test_cli_does_not_allow_recovery_to_become_approval(tmp_path: Path) -> None:
    ledger = tmp_path / "delivery.json"
    assert _run(
        ledger,
        "start",
        "--attempt-id",
        "a1",
        "--scope",
        "scope-sha",
        "--packet-identity",
        "packet-sha",
        "--parent-receipt-identity",
        "receipt-a1",
        "--boundary-fingerprint",
        "fingerprint-a1",
    ).returncode == 0
    recovered = _run(
        ledger,
        "recover",
        "--attempt-id",
        "a1",
        "--signal",
        "host transcript contains reviewer text; parent receipt absent",
    )
    assert recovered.returncode == 0
    result = _payload(recovered)
    assert result["attempt"]["observations"][-1]["state"] == "findings-recovered-from-transcript"
    assert result["delivery_complete"] is False
