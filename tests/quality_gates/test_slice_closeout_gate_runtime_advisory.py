"""Gate-baseline runtime advisory (spec achieve-efficiency-improvements C).

A gate that PASSES but is slow by design is code-quality debt the retro must be
able to see. These cover the evaluator (over/under budget, cached-skip), the
durable verdict shape, the stderr advisory polarity, and the env-override budget.
"""
from __future__ import annotations

import pytest

from scripts.slice_closeout_advisories import (
    DEFAULT_GATE_RUNTIME_BUDGET_SECONDS,
    advise_gate_runtime_budget,
    attach_gate_runtime_advisory,
    evaluate_gate_runtime_budget,
    resolve_gate_runtime_budget_seconds,
)


def test_over_budget_gate_is_recorded_with_verdict_fields() -> None:
    executed = [
        {"phase": "verify", "command": "pytest -q", "elapsed_seconds": 200.0, "returncode": 0},
    ]
    over = evaluate_gate_runtime_budget(executed, budget_seconds=120.0)
    assert len(over) == 1
    record = over[0]
    assert record["phase"] == "verify"
    assert record["elapsed_seconds"] == 200.0
    assert record["budget_seconds"] == 120.0
    assert record["over_budget"] is True


def test_under_budget_gate_emits_nothing() -> None:
    executed = [
        {"phase": "sync", "command": "python3 scripts/sync.py", "elapsed_seconds": 3.0},
        {"phase": "verify", "command": "ruff check", "elapsed_seconds": 119.9},
    ]
    assert evaluate_gate_runtime_budget(executed, budget_seconds=120.0) == []


def test_cached_gate_without_timing_is_skipped() -> None:
    # Reused/cached broad-pytest proofs carry no elapsed_seconds; they must not
    # crash the evaluator or be reported as over budget.
    executed = [
        {"phase": "verify", "command": "pytest -q", "returncode": 0, "cached": True},
    ]
    assert evaluate_gate_runtime_budget(executed, budget_seconds=1.0) == []


def test_advise_prints_only_when_over_budget(capsys: pytest.CaptureFixture[str]) -> None:
    advise_gate_runtime_budget([])
    assert capsys.readouterr().err == ""

    advise_gate_runtime_budget(
        [{"phase": "verify", "command": "pytest -q", "elapsed_seconds": 200.0, "budget_seconds": 120.0}]
    )
    err = capsys.readouterr().err
    assert "gate-baseline runtime over budget" in err
    assert "200.0s" in err
    # The honest-scope non-claim (spec C1) must travel with the advisory.
    assert "pre-push hook" in err


def test_budget_honors_env_override_and_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHARNESS_GATE_RUNTIME_BUDGET_SECONDS", raising=False)
    assert resolve_gate_runtime_budget_seconds() == DEFAULT_GATE_RUNTIME_BUDGET_SECONDS

    monkeypatch.setenv("CHARNESS_GATE_RUNTIME_BUDGET_SECONDS", "45")
    assert resolve_gate_runtime_budget_seconds() == 45.0

    # A non-numeric override falls back to the default rather than raising.
    monkeypatch.setenv("CHARNESS_GATE_RUNTIME_BUDGET_SECONDS", "not-a-number")
    assert resolve_gate_runtime_budget_seconds() == DEFAULT_GATE_RUNTIME_BUDGET_SECONDS


def test_attach_populates_durable_payload_and_advises(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The orchestrator main() calls: attaches the verdict to the durable payload
    # (spec C2) and emits the advisory when a gate is over budget.
    monkeypatch.setenv("CHARNESS_GATE_RUNTIME_BUDGET_SECONDS", "10")
    payload: dict = {
        "executed_commands": [
            {"phase": "verify", "command": "pytest -q", "elapsed_seconds": 50.0},
            {"phase": "sync", "command": "noop", "elapsed_seconds": 1.0},
        ]
    }
    attach_gate_runtime_advisory(payload)
    verdict = payload["gate_runtime_advisory"]
    assert verdict["budget_seconds"] == 10.0
    assert [r["command"] for r in verdict["over_budget"]] == ["pytest -q"]
    assert "gate-baseline runtime over budget" in capsys.readouterr().err
