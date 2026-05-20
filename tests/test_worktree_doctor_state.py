from __future__ import annotations

from scripts.worktree_doctor_state import tail


def test_tail_keeps_short_text_and_truncates_from_end() -> None:
    assert tail("abc", max_chars=5) == "abc"
    assert tail("abcdef", max_chars=3) == "def"
