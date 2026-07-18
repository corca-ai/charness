from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

ab = load_script_module("skill_efficiency_comparability_under_test", ROOT / "scripts/run_skill_efficiency_ab.py")
validation = load_script_module(
    "skill_efficiency_comparability_validation_under_test",
    ROOT / "scripts/run_skill_efficiency_ab_validation.py",
)


def _identity(**overrides: str) -> dict[str, str]:
    identity = {
        "source_class": "fixture",
        "command_id": "fixture-capture-v1",
        "corpus_id": "demo-corpus-v1",
        "signal_class": "deterministic",
        "reconstruction_status": "complete",
        "model_id": "not-applicable",
        "parser_id": "fixture-parser-v1",
    }
    identity.update(overrides)
    return identity


def _aggregates() -> dict:
    return {
        "baseline": ab.aggregate_metrics([{"outcome": "passed", "total_tokens": 100}]),
        "treatment": ab.aggregate_metrics([{"outcome": "passed", "total_tokens": 50}]),
    }


@pytest.mark.parametrize(
    "override, reason",
    [
        ({"source_class": "live"}, "mismatch:source_class"),
        ({"command_id": "other-capture"}, "mismatch:command_id"),
        ({"corpus_id": "other"}, "mismatch:corpus_id"),
        ({"signal_class": "live"}, "mismatch:signal_class"),
        ({"reconstruction_status": "partial"}, "mismatch:reconstruction_status"),
        ({"model_id": "different-model"}, "mismatch:model_id"),
        ({"parser_id": "parser-v2"}, "mismatch:parser_id"),
    ],
)
def test_incomparable_identity_suppresses_cost_delta(override: dict, reason: str) -> None:
    config = {
        "comparison_identity": _identity(),
        "arms": [{"name": "baseline"}, {"name": "treatment", "comparison_identity": override}],
    }
    entry = ab.build_comparison_summary(config, _aggregates())["arms"]["treatment"]
    assert entry["status"] == "incomparable" and entry["cost_deltas"] is None
    assert reason in entry["reasons"]
    report = ab.build_report(config, _aggregates())
    assert "not reported" in report and "-50%" not in report


def test_outcome_evidence_is_adjacent_to_cost_delta() -> None:
    config = {"comparison_identity": _identity(), "arms": [{"name": "baseline"}, {"name": "treatment"}]}
    agg = _aggregates()
    agg["treatment"] = ab.aggregate_metrics([{"outcome": "failed", "total_tokens": 50}])
    grades = {"treatment": {"pass_rate": {"mean": 0.25, "min": 0.0, "max": 0.5, "n": 2}}}
    entry = ab.build_comparison_summary(config, agg, grades)["arms"]["treatment"]
    assert entry["cost_deltas"]["total_tokens"] == -50.0
    assert entry["outcome"] == {"capture_pass_rate": 0.0, "grade_pass_rate": 0.25}
    assert "| treatment | comparable | 0.0 | 0.25 | total_tokens=-50%" in ab.build_report(config, agg, grades)


def test_missing_identity_is_incomparable_not_legacy_delta() -> None:
    entry = ab.build_comparison_summary({"arms": []}, _aggregates())["arms"]["treatment"]
    assert entry["status"] == "incomparable" and entry["cost_deltas"] is None


def test_empty_aggregate_records_return_an_empty_comparison_summary() -> None:
    assert ab.build_comparison_summary({}, {}) == {"baseline": None, "arms": {}}


def test_declared_order_owns_baseline_when_aggregates_are_reversed() -> None:
    config = {"comparison_identity": _identity(), "arms": [{"name": "baseline"}, {"name": "treatment"}]}
    aggregate = _aggregates()
    reversed_aggregate = {"treatment": aggregate["treatment"], "baseline": aggregate["baseline"]}
    summary = ab.build_comparison_summary(config, reversed_aggregate)
    assert summary["baseline"] == "baseline"
    assert summary["arms"]["treatment"]["cost_deltas"]["total_tokens"] == -50.0


def test_pure_report_deduplicates_malformed_declared_names() -> None:
    config = {
        "comparison_identity": _identity(),
        "arms": [{"name": "baseline"}, {"name": "baseline"}, {"name": "treatment"}],
    }
    summary = ab.build_comparison_summary(config, _aggregates())
    assert list(summary["arms"]) == ["treatment"]
    report = ab.build_report(config, _aggregates())
    assert "| baseline | comparable |" not in report and "total_tokens=+0%" not in report


@pytest.mark.parametrize(
    "identity, match",
    [
        ("fixture", "must be an object"),
        ({"corpus_id": ""}, "corpus_id must be a non-empty string"),
        ({"parser_id": 3}, "parser_id must be a non-empty string"),
    ],
)
def test_malformed_comparison_identity_is_rejected(identity: object, match: str) -> None:
    config = {
        "spec_path": "spec.json",
        "runs": 1,
        "comparison_identity": identity,
        "arms": [{"name": "a", "ref": "HEAD"}],
    }
    with pytest.raises(ValueError, match=match):
        validation.validate_run_config(config)
