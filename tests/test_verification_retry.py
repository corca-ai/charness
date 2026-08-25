from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from skills.public.critique.scripts.verification_retry import (
    build_retry_key,
    canonical_failure_code,
    canonical_identity,
    decide_retry,
    main,
)


def _key(input_identity: str = "input-v1", failure: str = "gate-failed") -> str:
    return build_retry_key(
        subject="sha256:" + "1" * 64,
        verifier="sha256:" + "2" * 64,
        input_identity="sha256:" + ("3" if input_identity == "input-v1" else "4") * 64,
        failure=failure,
    )


def test_first_attempt_is_not_a_retry() -> None:
    result = decide_retry(current_key=_key(), current_evidence="none")
    assert result.disposition == "first-attempt"


def test_same_failure_without_new_evidence_stops() -> None:
    key = _key()
    result = decide_retry(
        current_key=key,
        current_evidence="none",
        previous_key=key,
    )
    assert result.disposition == "stop-no-progress"


def test_same_claim_with_new_evidence_still_stops() -> None:
    key = _key()
    result = decide_retry(
        current_key=key,
        current_evidence="sha256:" + "5" * 64,
        previous_key=key,
    )
    assert result.disposition == "stop-no-progress"
    assert "does not authorize" in result.reason


def test_changed_input_can_retry_without_new_receipt() -> None:
    result = decide_retry(current_key=_key("input-v2"), current_evidence="none", previous_key=_key())
    assert result.disposition == "retry-new-identity"


def test_failure_code_rejects_changing_log_prose() -> None:
    with pytest.raises(ValueError, match="stable lowercase slug"):
        canonical_failure_code("failed at 12:42 /tmp/run.log")


def test_identity_rejects_caller_labels() -> None:
    with pytest.raises(ValueError, match="sha256"):
        canonical_identity("input-label")


def test_identity_rejects_empty_values() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        canonical_identity("   ")


def test_retry_rejects_invalid_current_key() -> None:
    with pytest.raises(ValueError, match="current retry key"):
        decide_retry(current_key="not-a-digest", current_evidence="none")


def test_retry_rejects_invalid_previous_key() -> None:
    with pytest.raises(ValueError, match="previous retry key"):
        decide_retry(current_key=_key(), current_evidence="none", previous_key="not-a-digest")


def test_cli_renders_the_retry_decision(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(
        [
            "--subject", "sha256:" + "1" * 64,
            "--verifier", "sha256:" + "2" * 64,
            "--input", "sha256:" + "3" * 64,
            "--failure-code", "gate-failed",
        ]
    ) == 0
    output = capsys.readouterr().out
    assert "retry_key: sha256:" in output
    assert "evidence_identity: none" in output
    assert "retry_disposition: first-attempt" in output
    assert "reason: no previous attempt for this claim" in output


def test_cli_reports_invalid_identity(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(
        [
            "--subject", "caller-label",
            "--verifier", "sha256:" + "2" * 64,
            "--input", "sha256:" + "3" * 64,
            "--failure-code", "gate-failed",
        ]
    ) == 2
    assert "error: identity must be sha256" in capsys.readouterr().out


def test_module_entrypoint_runs_the_same_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    source = Path(__file__).resolve().parents[1] / "skills/public/critique/scripts/verification_retry.py"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(source),
            "--subject", "sha256:" + "1" * 64,
            "--verifier", "sha256:" + "2" * 64,
            "--input", "sha256:" + "3" * 64,
            "--failure-code", "gate-failed",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(source), run_name="__main__")
    assert exc.value.code == 0
