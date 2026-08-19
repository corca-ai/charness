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

    # The budget counts CONTENT WORDS; the skill must say so, because an author who
    # thinks it is a line cap trims formatting, rewraps, and gets nowhere -- which is
    # precisely what the old line-based budget rewarded.
    #
    # The ceiling is READ from the module that owns it rather than written here as a
    # literal. This assertion carried `"78"` and would have kept passing on a SKILL.md
    # that still advertised 78 after the default moved, which is the transcription
    # class the budget module's own docstring is about.
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "handoff_content_budget_for_skill_gate",
        ROOT / "skills" / "public" / "handoff" / "scripts" / "handoff_content_budget.py",
    )
    budget = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(budget)
    assert "CONTENT" in skill_text
    assert "250-550" in skill_text, "the skill must publish an authoring TARGET, not only a ceiling"
    assert str(budget.DEFAULT_MAX_CONTENT_WORDS) in skill_text
    assert "content_word_count" in skill_text
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
    assert "classify each `Current State` and `Next Session` entry" in spill_targets
    assert "copied receipt" in spill_targets
    assert "prerequisite before the next slice it governs" in skill_text
    assert "does not replace the ordered" in skill_text
