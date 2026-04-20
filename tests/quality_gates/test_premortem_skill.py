from __future__ import annotations

from .support import ROOT


def test_premortem_skill_surfaces_counterweight_and_deliberately_not_doing() -> None:
    skill_text = (ROOT / "skills" / "public" / "premortem" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    angle_text = (
        ROOT / "skills" / "public" / "premortem" / "references" / "angle-selection.md"
    ).read_text(encoding="utf-8")
    capability_text = (
        ROOT / "skills" / "public" / "premortem" / "references" / "subagent-capability-check.md"
    ).read_text(encoding="utf-8")
    counterweight_text = (
        ROOT / "skills" / "public" / "premortem" / "references" / "counterweight-triage.md"
    ).read_text(encoding="utf-8")
    handoff_loop = (
        ROOT / "skills" / "public" / "handoff" / "references" / "premortem-loop.md"
    ).read_text(encoding="utf-8")
    spec_loop = (
        ROOT / "skills" / "public" / "spec" / "references" / "premortem-loop.md"
    ).read_text(encoding="utf-8")

    assert "counterweight" in skill_text
    assert "Deliberately Not Doing" in skill_text
    assert "use subagents as the canonical path" in skill_text
    assert "at least two angle subagents plus one separate counterweight subagent" in skill_text
    assert "default to three angle subagents" in skill_text
    assert "if the host cannot provide subagents, stop" in skill_text
    assert "do not collapse into a same-agent local pass or degraded variant" in skill_text
    assert "blast-radius" in angle_text
    assert "future maintainer" in angle_text
    assert "minimum: two contrasting angle subagents plus one separate counterweight" in angle_text
    assert "canonical premortem path is unavailable" in angle_text
    assert "Do not present a local pass as the canonical premortem" in capability_text
    assert "the next action is to surface the host-side contract gap" in capability_text
    assert "Do not replace the misunderstanding premortem with a" in handoff_loop
    assert "Do not replace the fresh-eye premortem with a same-agent" in spec_loop
    assert "Act Before Ship" in counterweight_text
    assert "Over-Worry" in counterweight_text


def test_spec_and_narrative_preserve_rejected_alternatives() -> None:
    spec_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    rejected = (
        ROOT / "skills" / "public" / "spec" / "references" / "rejected-alternatives.md"
    ).read_text(encoding="utf-8")
    narrative_text = (ROOT / "skills" / "public" / "narrative" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "standalone `premortem` skill" in spec_text
    assert "Deliberately Not Doing" in spec_text
    assert "rejected alternatives" in rejected
    assert "Deliberately Not Doing" in narrative_text
