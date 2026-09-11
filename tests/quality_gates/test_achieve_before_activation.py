from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACHIEVE = ROOT / "skills" / "public" / "achieve"


def _text(relative: str) -> str:
    return (ACHIEVE / relative).read_text(encoding="utf-8")


def test_achieve_describes_planning_binding_and_pickup() -> None:
    skill = _text("SKILL.md")
    draft = _text("references/goal-artifact.md")
    pickup = _text("references/lifecycle-during.md")

    assert "planning record" in skill
    assert "Goal Binding" in skill
    assert "`/goal #N`" in skill
    assert "goal_run_pickup.py" in skill
    assert "interview-cap-reached" in skill
    assert "ordinary operator answer" in skill
    assert "one planning writer" in draft
    assert "immutable Goal Binding" in pickup


def test_achieve_no_longer_advertises_local_goal_lifecycle() -> None:
    joined = "\n".join(
        _text(relative)
        for relative in (
            "SKILL.md",
            "references/goal-artifact.md",
            "references/lifecycle.md",
            "references/lifecycle-before.md",
            "references/lifecycle-during.md",
        )
    )

    for removed in (
        "/goal @",
        "append_slice_log.py",
        "Status: active",
        "Status: complete",
        "Slice Log",
        "Auto-Retro",
        "Operator Decision Queue",
        "metric window",
    ):
        assert removed not in joined


def test_achieve_routes_direction_uncertainty_before_commitment() -> None:
    skill = " ".join(_text("SKILL.md").split())
    coordination = " ".join(_text("references/coordination.md").split())

    assert "## Learning Before Commitment" in skill
    assert "choose the next move: learn first when unresolved uncertainty could change the" in skill
    assert "otherwise continue with that step" in skill
    assert "before the next cheap reversible step" in skill
    assert "Name direction-invalidating uncertainty as an assumption" in skill
    assert "route it to `ideation`" in skill
    assert "Achieve owns this handoff and sequences the result" in skill
    assert "Enter `spec` only after that concept uncertainty is observed" in skill
    assert "Spec-local mechanism uncertainty remains a `Probe Question`" in skill
    assert "Evidence is claim-relative" in skill
    assert "local deterministic evidence remains enough for local" in skill
    assert "Do not create a separate probe when the next cheap reversible step" in skill
    assert "record the uncertainty and expected observation" in skill
    assert "whether reality contact is needed" in coordination
    assert "cheapest sufficiently real probe" in coordination
    assert "mechanism uncertainty as a `Probe Question`" in coordination


def test_shared_sequence_diagnoses_before_structural_response() -> None:
    sequence = " ".join(
        (ROOT / "skills" / "shared" / "references" / "generative-sequence.md")
        .read_text(encoding="utf-8")
        .split()
    )

    assert "observe first, separate the observation from its interpretation" in sequence
    assert "diagnose whether the gap is one of ownership, derivation, boundary, or proof" in sequence
    assert "structural response" in sequence
