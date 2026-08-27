"""The shipped achieve contract keeps lesson memory small and optional."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_DURING = ROOT / "skills/public/achieve/references/lifecycle-during.md"


def _normalized(path: Path) -> str:
    """Make the contract assertion insensitive to Markdown's presentation wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


def test_achieve_keeps_one_optional_lesson_memory_surface() -> None:
    during = _normalized(LIFECYCLE_DURING)

    assert "The lesson ledger is optional durable memory and selection state" in during
    assert "pickup path reads recent-lessons.md once per goal start or resume" in during
    assert "never rebuilds the ledger/index" in during
