from __future__ import annotations

from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]
normalizer = load_script_module(
    "normalize_goal_closeout_under_test",
    ROOT / "skills/public/achieve/scripts/normalize_goal_closeout.py",
)


def test_normalize_common_closeout_form_errors() -> None:
    text = (
        "# Achieve Goal: Demo\n\n"
        "Status: active\n\n"
        "## Operator Decision Queue\n\n"
        "Record decisions, confirmations, credential actions, manual proof steps.\n\n"
        "- Decision: operator-only decision or confirmation needed\n\n"
        "## Coordination Cues\n\n"
        "- Routing: quality \u2014 used the quality planner.\n\n"
        "## Final Verification\n\n"
        "Retro: `charness-artifacts/retro/2026-07-09-demo.md`\n"
        "Host log probe: `charness-artifacts/probe/2026-07-09-demo.json`\n"
        "Disposition review: `charness-artifacts/retro/2026-07-09-demo-disposition.md`\n\n"
        "## Auto-Retro\n\n"
        "Retro dispositions: `charness-artifacts/retro/2026-07-09-demo-disposition.md` PASS -- done\n"
    )

    updated, fixes = normalizer.normalize(text, complete=True)

    assert "Status: complete" in updated
    assert "Retro: charness-artifacts/retro/2026-07-09-demo.md" in updated
    assert "- Routing: find-skills -> quality \u2014 used the quality planner." in updated
    assert "none \u2014 no operator-only decision remains" in updated
    assert "Retro dispositions: applied:" in updated
    assert len(fixes) == 5


def test_normalize_is_noop_when_forms_are_clean() -> None:
    text = (
        "Status: complete\n\n"
        "## Operator Decision Queue\n\n"
        "none \u2014 no operator-only decision remains for this completed local goal.\n\n"
        "## Auto-Retro\n\n"
        "Retro dispositions: applied: shipped the follow-up.\n"
    )

    updated, fixes = normalizer.normalize(text)

    assert updated == text
    assert fixes == []
