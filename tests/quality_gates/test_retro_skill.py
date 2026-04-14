from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_retro_skill_triggers_on_present_but_undeclared_invariants() -> None:
    skill_text = (ROOT / "skills" / "public" / "retro" / "SKILL.md").read_text(encoding="utf-8")
    reference_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "trigger-and-persistence.md"
    ).read_text(encoding="utf-8")

    assert "fresh-eye reader misread an invariant" in skill_text
    assert "present invariant as absent" in reference_text
