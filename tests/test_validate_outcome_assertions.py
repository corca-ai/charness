from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# The validator does `import grade_skill_outcome` (a sibling), so scripts/ must be importable.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

v = load_script_module("validate_outcome_assertions_under_test", ROOT / "scripts" / "validate_outcome_assertions.py")


def _good_set() -> dict:
    return {"evalId": "demo", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "s", "check": {"type": "summary_contains", "value": "x"}}]}


def _make_set(repo_root: Path, skill: str, obj: object) -> Path:
    d = repo_root / "evals" / "cautilus" / f"{skill}-claim-fidelity"
    d.mkdir(parents=True, exist_ok=True)
    path = d / "outcome-assertions.json"
    path.write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8")
    return path


def test_validate_file_accepts_valid(tmp_path: Path) -> None:
    path = _make_set(tmp_path, "demo", _good_set())
    assert v.validate_file(path) == []


def test_validate_file_reports_malformed_json(tmp_path: Path) -> None:
    path = _make_set(tmp_path, "demo", "{ not json")
    problems = v.validate_file(path)
    assert len(problems) == 1 and "not valid JSON" in problems[0]


def test_validate_file_reports_schema_problems(tmp_path: Path) -> None:
    path = _make_set(tmp_path, "demo", {"evalId": "x", "assertions": []})
    assert any("non-empty list" in p for p in v.validate_file(path))


def test_validate_file_rejects_malformed_regex(tmp_path: Path) -> None:
    # The surface gate catches a bad `regex: true` pattern before it ships.
    path = _make_set(tmp_path, "demo", {"evalId": "x", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "s",
         "check": {"type": "summary_contains", "value": "(", "regex": True}}]})
    assert any("invalid regex" in p for p in v.validate_file(path))


def test_find_and_validate_all_globs_every_set(tmp_path: Path) -> None:
    _make_set(tmp_path, "alpha", _good_set())
    _make_set(tmp_path, "beta", {"evalId": "x", "assertions": []})  # invalid
    # A non-matching sibling file under the same tree must NOT be picked up.
    (tmp_path / "evals" / "cautilus" / "alpha-claim-fidelity" / "spec.json").write_text("{}", encoding="utf-8")
    found = v.find_assertion_sets(tmp_path)
    assert len(found) == 2 and all(p.name == "outcome-assertions.json" for p in found)
    results = v.validate_all(tmp_path)
    assert results["evals/cautilus/alpha-claim-fidelity/outcome-assertions.json"] == []
    assert results["evals/cautilus/beta-claim-fidelity/outcome-assertions.json"]  # non-empty problems


def test_main_returns_zero_when_all_valid(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _make_set(tmp_path, "demo", _good_set())
    assert v.main(["--repo-root", str(tmp_path)]) == 0
    assert "Validated 1 outcome assertion set(s)." in capsys.readouterr().out


def test_main_returns_one_and_reports_on_problem(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _make_set(tmp_path, "demo", {"evalId": "x", "assertions": []})
    assert v.main(["--repo-root", str(tmp_path)]) == 1
    assert "FAIL" in capsys.readouterr().err


def test_main_no_sets_is_clean(tmp_path: Path) -> None:
    # An empty repo (no sets yet) is not an error.
    assert v.main(["--repo-root", str(tmp_path)]) == 0


def test_main_json_mode_reports_problems(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _make_set(tmp_path, "demo", {"evalId": "x", "assertions": []})
    rc = v.main(["--repo-root", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1 and payload["problems"]


def test_shipped_assertion_sets_all_conform() -> None:
    # The durable surface check: every outcome-assertions.json that ships in the repo
    # must validate against the grader schema (generalizes the single hardcoded
    # conformance test to every set, present and future).
    results = v.validate_all(ROOT)
    assert results, "expected at least the hitl outcome-assertions.json to ship"
    bad = {rel: errs for rel, errs in results.items() if errs}
    assert not bad, f"shipped assertion sets failed validation: {bad}"
