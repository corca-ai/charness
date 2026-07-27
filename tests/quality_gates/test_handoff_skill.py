from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_handoff_skill_names_diary_antipattern_and_size_gate() -> None:
    skill_text = (ROOT / "skills" / "public" / "handoff" / "SKILL.md").read_text(encoding="utf-8")
    spill_targets = (
        ROOT / "skills" / "public" / "handoff" / "references" / "spill-targets.md"
    ).read_text(encoding="utf-8")
    state_selection = (
        ROOT / "skills" / "public" / "handoff" / "references" / "state-selection.md"
    ).read_text(encoding="utf-8")

    # The budget counts CONTENT lines; the skill must say so, because an author
    # who thinks it is a raw line cap trims formatting and reference links and
    # gets nowhere.
    assert "CONTENT" in skill_text and "25-50" in skill_text and "58" in skill_text
    assert "content_line_count" in skill_text
    assert "## This Session" in skill_text and "(<date>)" in skill_text
    assert "spill-targets.md" in skill_text
    assert "changes the next action" in skill_text
    assert "always-loaded host instruction surfaces" in skill_text
    assert "host already injects them automatically" in skill_text
    # #240 reciprocal pickup contract: SessionStart/handoff routing sends a
    # mention-only pickup here, and handoff must invoke (not just re-read) the named workflow.
    # Normalize whitespace so the pins survive line-wrapping of the contract.
    normalized = " ".join(skill_text.split())
    assert "routed here by the SessionStart hook" in normalized
    assert "recurring routing miss" in normalized
    assert "host already injects" in state_selection
    # document-seams.md deleted in reference-compaction Slice 7 (DUP: its
    # host-injected-surface Non-Goal is covered by SKILL.md's "always-loaded host
    # instruction surfaces" / "host already injects them automatically" and
    # state-selection.md's "host already injects").
    assert "git log" in spill_targets
    assert "release notes" in spill_targets
    assert "quality/latest.md" in spill_targets
