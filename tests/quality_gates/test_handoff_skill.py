from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_handoff_skill_names_diary_antipattern_and_size_gate() -> None:
    skill_text = (ROOT / "skills" / "public" / "handoff" / "SKILL.md").read_text(encoding="utf-8")
    spill_targets = (
        ROOT / "skills" / "public" / "handoff" / "references" / "spill-targets.md"
    ).read_text(encoding="utf-8")

    assert "roughly" in skill_text and "200 lines" in skill_text
    assert "## This Session" in skill_text and "(<date>)" in skill_text
    assert "spill-targets.md" in skill_text
    assert "git log" in spill_targets
    assert "release notes" in spill_targets
