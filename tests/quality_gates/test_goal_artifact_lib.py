from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/goal_artifact_lib.py"
spec = importlib.util.spec_from_file_location("goal_artifact_lib", SCRIPT)
gal = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(gal)


def test_upsert_creates_a_planning_record(tmp_path: Path) -> None:
    result = gal.upsert_goal(
        tmp_path,
        date="2026-05-27",
        slug="planning-record",
        title="Planning Record",
        goal_body="Make the intended outcome explicit.",
    )

    assert result == {"action": "created", "path": "charness-artifacts/goals/2026-05-27-planning-record.md"}
    text = gal.goal_path(tmp_path, "2026-05-27", "planning-record").read_text(encoding="utf-8")
    assert gal.check_planning_shape(text)["ok"] is True
    assert "Make the intended outcome explicit." in text
    assert "Status:" not in text
    assert "Activation:" not in text
    assert "Slice Log" not in text
    assert "Auto-Retro" not in text


def test_upsert_updates_only_planning_fields_before_binding(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="Old", goal_body="old body")
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    original = path.read_text(encoding="utf-8")
    marker = "## Boundaries\n\noperator-authored boundary\n"
    path.write_text(original.replace("## Boundaries\n", marker), encoding="utf-8")

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="New", goal_body="new body")

    updated = path.read_text(encoding="utf-8")
    assert result["action"] == "updated"
    assert "# Achieve Goal: New" in updated
    assert "new body" in updated
    assert "operator-authored boundary" in updated


def test_binding_sibling_freezes_the_draft(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="Frozen", goal_body="body")
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    binding = path.with_suffix(".binding.json")
    binding.write_text("{}\n", encoding="utf-8")
    original = path.read_bytes()

    result = gal.upsert_goal(tmp_path, date="2026-05-27", slug="g", title="Changed", goal_body="changed")

    assert result["action"] == "refused"
    assert result["reason"] == "frozen-binding"
    assert path.read_bytes() == original


def test_upsert_refuses_to_write_an_invalid_existing_planning_shape(tmp_path: Path) -> None:
    path = gal.goal_path(tmp_path, "2026-05-27", "g")
    path.parent.mkdir(parents=True)
    path.write_text("# Achieve Goal: Old\n\n## Goal\n\nold body\n", encoding="utf-8")
    before = path.read_bytes()

    with pytest.raises(ValueError, match="invalid Goal Draft planning shape"):
        gal.upsert_goal(
            tmp_path,
            date="2026-05-27",
            slug="g",
            title="New",
            goal_body="new body",
        )

    assert path.read_bytes() == before


def test_planning_shape_reports_missing_sections_and_bad_paths() -> None:
    result = gal.check_planning_shape(
        "# Achieve Goal: T\n\n## Goal\nRun `/home/user/worktrees/demo` next.\n"
    )

    assert result["ok"] is False
    assert "Non-Goals" in result["missing_sections"]
    assert result["path_portability"]["ok"] is False


def test_goal_values_reject_unfenced_headings_and_unbalanced_fences() -> None:
    with pytest.raises(ValueError, match="unfenced markdown heading"):
        gal.validate_goal_values("T", "body\n\n## New section")
    with pytest.raises(ValueError, match="code fence unclosed"):
        gal.validate_goal_values("T", "body\n\n```\nunfinished")


def test_goal_path_rejects_malformed_dates(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        gal.goal_path(tmp_path, "2026-5-7", "g")
    assert gal.slugify("../../etc/passwd") == "etc-passwd"
