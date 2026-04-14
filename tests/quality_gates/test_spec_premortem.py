from __future__ import annotations

from .support import ROOT


def test_spec_skill_surfaces_premortem_and_fresh_eye_review() -> None:
    skill_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    reference_text = (
        ROOT / "skills" / "public" / "spec" / "references" / "premortem-loop.md"
    ).read_text(encoding="utf-8")

    assert "premortem" in skill_text.lower()
    assert "fresh-eye" in skill_text
    assert "subagent" in skill_text or "subagents" in skill_text
    assert "`references/premortem-loop.md`" in skill_text
    assert "fresh five-minute implementer" in reference_text
    assert "wrong next action" in reference_text
