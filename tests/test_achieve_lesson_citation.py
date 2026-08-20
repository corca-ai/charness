"""The shipped achieve contract must produce the citation its retro reader consumes.

This is deliberately a source-contract test. The lesson bundle is already written by
``open_lesson_session.py``; this test prevents the work workflow from silently dropping
the producer's ``session_id``/``bundle_path`` handoff again.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_DURING = ROOT / "skills/public/achieve/references/lifecycle-during.md"


def _normalized(path: Path) -> str:
    """Make the contract assertion insensitive to Markdown's presentation wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


def test_achieve_records_the_frozen_lesson_bundle_for_retro_recovery() -> None:
    during = _normalized(LIFECYCLE_DURING)

    assert "### Lesson-session citation carrier" in during
    assert "run that exact command before the affected work" in during
    assert "`session_id` and frozen `bundle_path`" in during
    assert "active goal artifact's `## Context Sources`" in during
    assert "retro reads that exact bundle after context loss" in during
    assert "never a newest-file guess or mutable lesson source" in during
    assert "not a copy of the bundle contents" in during
