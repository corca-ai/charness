from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_LIB = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts/goal_artifact_lib.py"
_spec = importlib.util.spec_from_file_location("goal_artifact_lib_portability", _LIB)
gal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gal)


def _goal_text(tmp_path: Path, slug: str = "g", date: str = "2026-05-27") -> str:
    path = gal.goal_path(tmp_path, date, slug)
    return path.read_text(encoding="utf-8")


_GOAL_HEAD = "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n"
_REQUIRED_BODY = (
    "## Active Operating Frame\n## Goal\n## Non-Goals\n## Boundaries\n## User Acceptance\n"
    "## Agent Verification Plan\n"
)
_TAIL_SECTIONS = (
    "## Operator Decision Queue\n## Slice Log\n## Off-Goal Findings\n## Final Verification\n"
    "## User Verification Instructions\n## Auto-Retro\n"
)
_PORTABILITY_BODY = (
    "## Context Sources\n- src\n## Interview Decisions\n- Q1\n"
    "## Plan Critique Findings\n- blocker folded\n"
)


def _goal_with_table(rows: list[str], portability: str = "") -> str:
    body = _GOAL_HEAD + _REQUIRED_BODY
    body += "## Slice Plan\n\n"
    body += "| Slice | Objective | Why | Evidence | Status |\n"
    body += "| --- | --- | --- | --- | --- |\n"
    for row in rows:
        body += row + "\n"
    body += "\n" + portability + _TAIL_SECTIONS
    return body


def test_slice_plan_table_row_count_table_form() -> None:
    one_row = _goal_with_table(["| 1 | a | now | x | planned |"])
    assert gal.slice_plan_data_row_count(one_row) == 1
    two_rows = _goal_with_table([
        "| 1 | a | now | x | planned |",
        "| 2 | b | next | y | planned |",
    ])
    assert gal.slice_plan_data_row_count(two_rows) == 2


def test_single_slice_goal_still_requires_portability() -> None:
    one_row = _goal_with_table(["| 1 | a | now | x | planned |"])
    result = gal.check_goal(one_row)
    assert result["ok"] is False
    assert result["portability_missing_sections"] == list(gal.PORTABILITY_SECTIONS)


def test_marker_prose_does_not_exempt_portability() -> None:
    body = _goal_with_table([
        "| 1 | a | now | x | planned |",
        "| 2 | b | next | y | planned |",
    ])
    body = body.replace(
        "## Slice Plan\n",
        "## Slice Plan\n\nThis is not a single-slice goal; it has two slices.\n",
        1,
    )
    result = gal.check_goal(body)
    assert result["ok"] is False
    assert result["portability_missing_sections"] == list(gal.PORTABILITY_SECTIONS)


def test_marker_prose_with_portability_sections_passes() -> None:
    body = _goal_with_table(
        [
            "| 1 | a | now | x | planned |",
            "| 2 | b | next | y | planned |",
        ],
        portability=_PORTABILITY_BODY,
    )
    body = body.replace("## Goal\n", "## Goal\nThis mentions a single-slice goal in prose.\n", 1)
    result = gal.check_goal(body)
    assert result["ok"] is True
    assert result["portability_missing_sections"] == []


def test_check_goal_reports_missing_portability() -> None:
    body = _goal_with_table([
        "| 1 | a | now | x | planned |",
        "| 2 | b | next | y | planned |",
    ])
    result = gal.check_goal(body)
    assert result["ok"] is False
    assert result["portability_missing_sections"] == list(gal.PORTABILITY_SECTIONS)
    assert any("portability" in issue.lower() for issue in result["issues"])


def test_check_goal_rejects_executable_absolute_checkout_path() -> None:
    body = _goal_with_table(["| 1 | a | now | x | planned |"])
    body = body.replace("## Goal\n", "## Goal\nRun `/home/hwidong/codes/demo-repo` next.\n", 1)

    result = gal.check_goal(body)

    assert result["ok"] is False
    assert result["path_portability"]["ok"] is False
    assert (
        result["path_portability"]["executable_paths"][0]["path"]
        == "/home/hwidong/codes/demo-repo"
    )
    assert any("path portability" in issue for issue in result["issues"])


def test_pursue_readiness_shares_the_path_portability_floor() -> None:
    body = _goal_with_table(["| 1 | a | now | x | planned |"])
    body = body.replace("## Goal\n", "## Goal\nUse `/home/hwidong/codes/demo-repo` next.\n", 1)

    result = gal.pursue_readiness(body)

    assert result["pursue_ready"] is False
    assert result["activation_ready"] is False
    assert result["path_portability"]["ok"] is False
    assert "path portability floor" in result["reason"]


def test_evidence_absolute_path_is_observable_without_refusal() -> None:
    body = _goal_with_table(
        ["| 1 | a | now | x | planned |"], portability=_PORTABILITY_BODY
    )
    body = body.replace(
        "## Final Verification\n",
        "## Final Verification\nObserved reproduction at `/home/hwidong/codes/demo-repo`.\n",
        1,
    )

    result = gal.check_goal(body)

    assert result["ok"] is True
    assert result["path_portability"]["ok"] is True
    assert (
        result["path_portability"]["intentional_evidence"][0]["path"]
        == "/home/hwidong/codes/demo-repo"
    )


def test_portability_gate_reports_an_unloadable_sibling_loader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gal._portability_gate.importlib.util,
        "spec_from_file_location",
        lambda *_args, **_kwargs: None,
    )
    with pytest.raises(ImportError, match="not found beside goal_artifact_portability_gate"):
        gal._portability_gate._load_sibling("missing-portability-sibling")


def test_check_goal_passes_with_portability_sections_present() -> None:
    body = _goal_with_table(
        [
            "| 1 | a | now | x | planned |",
            "| 2 | b | next | y | planned |",
        ],
        portability=_PORTABILITY_BODY,
    )
    result = gal.check_goal(body)
    assert result["ok"] is True
    assert result["portability_missing_sections"] == []


def test_scaffold_carries_portability_headings(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    text = _goal_text(tmp_path)
    result = gal.check_goal(text)
    assert result["ok"] is True
    assert result["portability_missing_sections"] == []
