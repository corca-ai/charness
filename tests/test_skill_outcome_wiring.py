from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# The module does `import grade_skill_outcome` (a sibling), so scripts/ must be importable.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

w = load_script_module("skill_outcome_wiring_under_test", ROOT / "scripts" / "skill_outcome_wiring.py")


# --- assertion set resolution ---------------------------------------------------


def _det_set(value: str = "/hitl") -> dict:
    return {"evalId": "demo", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "s",
         "check": {"type": "summary_contains", "value": value}}]}


def test_resolve_assertion_set_finds_sibling(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"prompt": "P"}), encoding="utf-8")
    (tmp_path / "outcome-assertions.json").write_text(json.dumps(_det_set()), encoding="utf-8")
    loaded = w.resolve_assertion_set(spec)
    assert loaded is not None and loaded["evalId"] == "demo"


def test_resolve_assertion_set_absent_is_none(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"prompt": "P"}), encoding="utf-8")
    assert w.resolve_assertion_set(spec) is None  # no sibling -> skip, not error


def test_resolve_assertion_set_malformed_raises(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"prompt": "P"}), encoding="utf-8")
    (tmp_path / "outcome-assertions.json").write_text(json.dumps({"evalId": "x", "assertions": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid assertion set"):  # fail fast before spend
        w.resolve_assertion_set(spec)


# --- grader gate ----------------------------------------------------------------


def test_grader_gate_runs_selftest_once_and_caches() -> None:
    calls = {"n": 0}

    def fake_selftest() -> int:
        calls["n"] += 1
        return 0

    gate = w.GraderGate(selftest=fake_selftest)
    assert gate.ok() is True and gate.ok() is True
    assert calls["n"] == 1  # selftest memoized


def test_grader_gate_false_when_selftest_fails(capsys: pytest.CaptureFixture) -> None:
    gate = w.GraderGate(selftest=lambda: 1)
    assert gate.ok() is False
    assert "grader self-test failed" in capsys.readouterr().err


# --- grade_arm ------------------------------------------------------------------


def _bundle(tmp_path: Path, name: str, summary: str) -> Path:
    d = tmp_path / name
    d.mkdir()
    (d / "observed.v1.json").write_text(
        json.dumps({"evaluations": [{"summary": summary, "outcome": "passed", "metrics": {}}]}), encoding="utf-8")
    return d


def test_grade_arm_no_assertion_set_returns_empty_without_gate(tmp_path: Path) -> None:
    # No assertion set -> short-circuit BEFORE the gate self-test even runs.
    gate = w.GraderGate(selftest=lambda: (_ for _ in ()).throw(AssertionError("gate must not run")))
    assert w.grade_arm([_bundle(tmp_path, "b0", "x")], None, None, gate) == []


def test_grade_arm_grades_bundles_and_writes_report(tmp_path: Path) -> None:
    bundles = [_bundle(tmp_path, "b0", "Execution of /hitl ok"),
               _bundle(tmp_path, "b1", "Execution of /hitl also ok")]
    gate = w.GraderGate(selftest=lambda: 0)
    outcomes = w.grade_arm(bundles, _det_set(), None, gate)
    assert len(outcomes) == 2
    assert all(o["pass_rate"] == 1.0 for o in outcomes)  # summary contains /hitl
    assert (bundles[0] / "outcome-grade.md").is_file()  # per-run report written alongside


def test_grade_arm_gate_failure_skips_grading(tmp_path: Path) -> None:
    gate = w.GraderGate(selftest=lambda: 1)
    assert w.grade_arm([_bundle(tmp_path, "b0", "x")], _det_set(), None, gate) == []


def test_grade_arm_one_bad_bundle_is_skipped_not_fatal(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    good = _bundle(tmp_path, "good", "Execution of /hitl")
    bad = tmp_path / "bad"
    bad.mkdir()  # missing observed.v1.json -> load_bundle raises FileNotFoundError
    gate = w.GraderGate(selftest=lambda: 0)
    outcomes = w.grade_arm([good, bad], _det_set(), None, gate)
    assert len(outcomes) == 1  # the bad bundle dropped, the good one survived
    assert "grade failed" in capsys.readouterr().err


def test_grade_arm_bad_regex_assertion_is_caught_not_fatal(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    # A regex:true value with a malformed pattern raises re.error inside grade();
    # _GRADE_FAULTS must catch it (defense-in-depth behind the schema regex-compile
    # check) so a set that slipped past validation cannot crash the whole arm.
    bad_regex_set = {"evalId": "demo", "assertions": [
        {"id": "r", "kind": "deterministic", "statement": "s",
         "check": {"type": "summary_contains", "value": "(", "regex": True}}]}
    gate = w.GraderGate(selftest=lambda: 0)
    outcomes = w.grade_arm([_bundle(tmp_path, "b0", "anything")], bad_regex_set, None, gate)
    assert outcomes == []  # re.error caught, bundle dropped, not a crash
    assert "grade failed" in capsys.readouterr().err


# --- aggregate_arm --------------------------------------------------------------


def test_aggregate_arm_mean_range_and_totals() -> None:
    outcomes = [
        {"pass_rate": 1.0, "skipped": 3, "errors": 0},
        {"pass_rate": 0.5, "skipped": 3, "errors": 1},
    ]
    summary = w.aggregate_arm(outcomes, _det_set())
    assert summary["eval_id"] == "demo"
    assert summary["runs_graded"] == 2
    assert summary["pass_rate"] == {"mean": 0.75, "min": 0.5, "max": 1.0, "n": 2}
    assert summary["skipped"] == 6 and summary["errors"] == 1


def test_aggregate_arm_counts_grade_failures() -> None:
    # attempted=3 but only 2 produced outcomes -> 1 bundle errored out of grading,
    # surfaced so an all-failed arm cannot read as a clean empty.
    summary = w.aggregate_arm([{"pass_rate": 1.0}, {"pass_rate": 0.5}], _det_set(), attempted=3)
    assert summary["grade_failed"] == 1 and summary["runs_graded"] == 2


def test_aggregate_arm_no_grade_failures_by_default() -> None:
    assert w.aggregate_arm([{"pass_rate": 1.0}], _det_set())["grade_failed"] == 0


def test_aggregate_arm_no_set_is_marked_none() -> None:
    summary = w.aggregate_arm([], None)
    assert summary["eval_id"] is None and summary["pass_rate"] is None and summary["runs_graded"] == 0


def test_aggregate_arm_all_none_rates_is_none_not_crash() -> None:
    # All runs all-skipped (pass_rate None) -> arm pass_rate None, not a stats crash.
    summary = w.aggregate_arm([{"pass_rate": None, "skipped": 4, "errors": 0}], _det_set())
    assert summary["pass_rate"] is None and summary["skipped"] == 4


# --- render_outcome_section -----------------------------------------------------


def test_render_outcome_section_empty_when_no_set() -> None:
    assert w.render_outcome_section(None) == ""
    assert w.render_outcome_section({"a": {"eval_id": None}}) == ""  # only no-set arms -> nothing to add


def test_render_outcome_section_table_and_caveat() -> None:
    section = w.render_outcome_section({
        "baseline": {"eval_id": "demo", "runs_graded": 2, "skipped": 4, "errors": 0,
                     "pass_rate": {"mean": 0.75, "min": 0.5, "max": 1.0, "n": 2}},
        "treatment": {"eval_id": "demo", "runs_graded": 2, "skipped": 0, "errors": 0,
                      "pass_rate": {"mean": 1.0, "min": 1.0, "max": 1.0, "n": 2}},
    })
    assert section.startswith("\n")  # leading blank so it folds into the report cleanly
    assert "## Outcome grade (advisory)" in section
    assert "0.75 [0.5–1]" in section and "baseline" in section and "treatment" in section
    assert "judge skipped" in section  # the judge-ran signal column
    assert "ask-before-run spend" in section  # honest caveat present


def test_render_outcome_section_shows_grade_failures() -> None:
    section = w.render_outcome_section({
        "arm": {"eval_id": "demo", "runs_graded": 2, "grade_failed": 1, "skipped": 0, "errors": 0,
                "pass_rate": {"mean": 1.0, "min": 1.0, "max": 1.0, "n": 2}}})
    assert "(+1 grade-failed)" in section  # all-failed cannot read as a clean empty


def test_render_outcome_section_marks_arm_without_set() -> None:
    section = w.render_outcome_section({
        "graded": {"eval_id": "demo", "runs_graded": 1, "skipped": 0, "errors": 0,
                   "pass_rate": {"mean": 1.0, "min": 1.0, "max": 1.0, "n": 1}},
        "ungraded": {"eval_id": None, "runs_graded": 0, "skipped": 0, "errors": 0, "pass_rate": None},
    })
    assert "no outcome-assertions.json — skipped" in section  # honest per-arm marker
