"""The shipped Achieve pickup keeps lesson memory small and optional."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACHIEVE = ROOT / "skills/public/achieve/SKILL.md"


def _normalized(path: Path) -> str:
    """Make the contract assertion insensitive to Markdown's presentation wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


def test_achieve_keeps_one_optional_lesson_memory_surface() -> None:
    achieve = _normalized(ACHIEVE)

    assert "one bounded advisory projection" in achieve
    assert "ledger selection preview" in achieve
    assert "consumer adapter declares a digest" in achieve
    assert "Missing lesson context never blocks pickup" in achieve
    assert "neither rebuilds the ledger nor records session continuity" in achieve
