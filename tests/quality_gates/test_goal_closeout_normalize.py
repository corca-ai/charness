from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[2]
normalizer = load_script_module(
    "normalize_goal_closeout_under_test",
    ROOT / "skills/public/achieve/scripts/normalize_goal_closeout.py",
)


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each fragment belongs to its option block, not only usage text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_normalize_goal_closeout_help_describes_options() -> None:
    script = ROOT / "skills/public/achieve/scripts/normalize_goal_closeout.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    _assert_help_pairs(
        result.stdout,
        {
            "--goal-path": "Path to the goal closeout artifact to normalize.",
            "--json": "Emit normalization results as JSON.",
        },
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
