"""The shipped achieve contract keeps lesson memory out of default closeout.

The ledger remains available as durable memory and selection state, while
session-emission receipts and retro disposition continuity are not part of the
ordinary goal or release contract.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_DURING = ROOT / "skills/public/achieve/references/lifecycle-during.md"


def _normalized(path: Path) -> str:
    """Make the contract assertion insensitive to Markdown's presentation wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


def test_achieve_does_not_require_session_receipts_for_default_closeout() -> None:
    during = _normalized(LIFECYCLE_DURING)

    assert "The lesson ledger is optional durable memory and selection state" in during
    assert "do not emit session receipts" in during
    assert "require retro disposition continuity" in during
    assert "outside the default and release contracts" in during
    assert "### Lesson-session citation carrier" not in during
