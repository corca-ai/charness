"""Changed-ref range spelling for critique packets."""

from __future__ import annotations

from pathlib import Path

from scripts.review.reviewed_input_range import pin_changed_ref


def test_three_dot_range_resolves_empty_endpoints_to_head(tmp_path: Path) -> None:
    calls: list[tuple[str, ...]] = []

    def git_bytes_optional(_root: Path, *args: str) -> bytes | None:
        calls.append(args)
        return b"abc123\n"

    pinned = pin_changed_ref(tmp_path, "...", git_bytes_optional)
    assert pinned == "abc123...abc123"
    assert any("HEAD" in arg for args in calls for arg in args)
