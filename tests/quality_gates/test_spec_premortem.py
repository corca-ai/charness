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


def test_spec_skill_distinguishes_public_executable_contract_from_implementation_guard() -> None:
    skill_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    reference_text = (
        ROOT / "skills" / "public" / "spec" / "references" / "public-executable-contracts.md"
    ).read_text(encoding="utf-8")

    assert "public executable contract" in skill_text
    assert "maintenance lint / implementation guard" in skill_text
    assert "future roadmap" in skill_text
    assert "`references/public-executable-contracts.md`" in skill_text
    assert "reader-facing current claims" in reference_text
    assert "implementation-file pinning" in reference_text
