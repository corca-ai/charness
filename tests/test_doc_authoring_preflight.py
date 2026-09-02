"""Small contract tests for the general-document authoring preflight.

The retired handoff artifact had its own length, routing, and regenerable-fact
test matrix. General docs only need the live, non-blocking forecast: inline-code
and link findings, plus an actionable rules payload.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_pf = import_repo_module(__file__, "scripts.check_doc_authoring_preflight")
_rules = import_repo_module(__file__, "scripts.gates_support.doc_authoring_rules")


def _repo(tmp_path: Path, body: str = "# Guide\n\nPlain text.\n") -> Path:
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "guide.md").write_text(body, encoding="utf-8")
    return tmp_path


def test_general_doc_forecast_reports_an_inline_code_violation(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "# Guide\n\nA `span that\nbreaks` here.\n")
    report = _pf.build_report(repo, "docs/guide.md")

    assert report.wrapped_inline_code
    assert report.blocked


def test_general_doc_forecast_is_clean_for_plain_content(tmp_path: Path) -> None:
    report = _pf.build_report(_repo(tmp_path), "docs/guide.md")

    assert not report.blocked
    assert not report.wrapped_inline_code
    assert not report.doc_links


def test_rules_mode_has_no_retired_surface_selector() -> None:
    rules = _rules.build_rules(ROOT)

    assert rules["mode"] == "rules"


def test_outside_repo_path_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path / "repo")
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")

    with pytest.raises(_pf.PreflightError, match="outside repo root"):
        _pf.build_report(repo, str(outside))


def test_preflight_remains_an_affordance_not_a_commit_gate() -> None:
    gate_plan = (ROOT / "scripts" / "staged_commit_gate_plan.py").read_text(encoding="utf-8")
    assert "check_doc_authoring_preflight" not in gate_plan
    assert "affordance" in (_pf.__doc__ or "").lower()
