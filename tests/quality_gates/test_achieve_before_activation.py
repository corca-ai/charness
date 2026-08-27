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
