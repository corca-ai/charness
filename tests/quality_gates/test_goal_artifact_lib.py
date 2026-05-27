from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_LIB = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts/goal_artifact_lib.py"
_spec = importlib.util.spec_from_file_location("goal_artifact_lib", _LIB)
gal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gal)


def _goal_text(tmp_path: Path, slug: str = "g", date: str = "2026-05-27") -> str:
    path = gal.goal_path(tmp_path, date, slug)
    return path.read_text(encoding="utf-8")


def test_upsert_creates_then_updates_status_only(tmp_path: Path) -> None:
    first = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="First", goal_body="BODY-AAA")
    assert first["action"] == "created"

    again = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="Second", status="active", goal_body="BODY-BBB")
    assert again["action"] in ("updated", "unchanged")
    assert "note" in again  # signals the existing-artifact / collision case

    text = _goal_text(tmp_path)
    assert "BODY-AAA" in text and "BODY-BBB" not in text  # body never overwritten
    assert "First" in text and "Second" not in text  # title never overwritten
    assert "Status: active" in text


def test_check_goal_passes_on_scaffold_and_reports_gaps(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    assert gal.check_goal(_goal_text(tmp_path))["ok"] is True

    bad = gal.check_goal("# Achieve Goal: T\n\nStatus: bogus\n\n## Goal\n")
    assert bad["ok"] is False
    assert "Non-Goals" in bad["missing_sections"]
    assert any("bogus" in issue for issue in bad["issues"])


def test_append_slice_numbers_and_spacing(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="T")
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    text = path.read_text(encoding="utf-8")
    assert gal.next_slice_number(text) == 1
    text = gal.append_slice(text, gal.render_slice_block(1, "one", {"Objective": "a"}))
    text = gal.append_slice(text, gal.render_slice_block(gal.next_slice_number(text), "two", {}))
    assert "### Slice 1: one" in text and "### Slice 2: two" in text
    assert "\n\n\n" not in text  # single blank-line separation
    assert "- Objective:\n" in text  # empty field carries no trailing space


def test_slugify_neutralizes_path_chars() -> None:
    assert gal.slugify("../../etc/passwd") == "etc-passwd"
    assert gal.slugify("Mixed CASE!!") == "mixed-case"


def test_set_status_rejects_invalid_and_preserves_crlf() -> None:
    with pytest.raises(ValueError):
        gal.set_status("Status: draft\n", "bogus")
    crlf = "# Achieve Goal: T\r\nStatus: draft\r\nCreated: 2026-05-27\r\n"
    out = gal.set_status(crlf, "active")
    assert "Status: active\r\n" in out  # CRLF on the status line preserved
    assert "Status: draft" not in out


def test_goal_path_rejects_malformed_dates(tmp_path: Path) -> None:
    for bad in ("2026/05/27", "../escape", "2026-5-7", "not-a-date"):
        with pytest.raises(ValueError):
            gal.goal_path(tmp_path, bad, "g")
    # well-formed date is accepted and stays inside the goals namespace
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    assert path.parent == tmp_path / "charness-artifacts" / "goals"


def test_fenced_headings_are_ignored(tmp_path: Path) -> None:
    doc = (
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n"
        "## Slice Log\n\n"
        "### Slice 1: real\n- Objective: x\n\n"
        "```md\n### Slice 9: fake-in-fence\n## Off-Goal Findings\n```\n\n"
        "## Off-Goal Findings\n\nKEEP-THIS\n"
    )
    # fenced "### Slice 9" must not bump the counter
    assert gal.next_slice_number(doc) == 2
    out = gal.append_slice(doc, gal.render_slice_block(2, "second", {"Objective": "y"}))
    # inserted into the real Slice Log (before the real Off-Goal section), trailing content intact
    assert "KEEP-THIS" in out
    assert out.index("### Slice 2: second") < out.rindex("## Off-Goal Findings")
    assert "### Slice 9: fake-in-fence" in out  # fenced content untouched


def test_check_goal_does_not_count_fenced_sections() -> None:
    fenced_only = (
        "# Achieve Goal: T\n\nStatus: draft\nActivation: `/goal @x`\n\n"
        "```md\n## Goal\n## Non-Goals\n## Boundaries\n```\n"
    )
    result = gal.check_goal(fenced_only)
    assert result["ok"] is False
    assert "Goal" in result["missing_sections"]
