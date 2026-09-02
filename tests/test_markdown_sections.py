"""The shared structured-entry grammar (`scripts/core/markdown_sections.py`).

`parse_pipe_entry` is the ONE reader behind both the critique `## Structured
Findings` floor and the ideation `## Structured Questions` floor. Sharing it is
what stops the two from disagreeing about what an entry IS while both claim to
enforce required fields on it — so its degenerate arms belong to both callers,
not to whichever one happened to exercise them.
"""

from __future__ import annotations

from scripts.core import markdown_sections


def test_parse_pipe_entry_returns_no_fields_for_a_contentless_bullet() -> None:
    # An empty map is how BOTH floors tell "this bullet carried nothing" from
    # "this entry declared an id". Returning a bare `{"id": ""}` here would make a
    # contentless bullet indistinguishable from an entry whose id is empty.
    for raw in ("", "   ", "- |", "* |  |", "|"):
        assert markdown_sections.parse_pipe_entry(raw) == {}, repr(raw)


def test_parse_pipe_entry_keeps_a_leading_chunk_without_a_colon_as_the_id() -> None:
    entry = markdown_sections.parse_pipe_entry("- F1 | action: file-issue | follow-up: deferred #12")

    assert entry["id"] == "F1"
    assert entry["action"] == "file-issue"
    assert entry["follow-up"] == "deferred #12"


def test_parse_pipe_entry_strips_exactly_one_bullet_marker() -> None:
    # `lstrip("- ")` takes a character SET, so it ate every leading `-` and space:
    # an id of `-1` collided with `1` as a bogus duplicate, and `--baseline`
    # silently became `baseline`. Both copies this reader replaced carried that bug.
    assert markdown_sections.parse_pipe_entry("- -1 | action: accept")["id"] == "-1"
    assert markdown_sections.parse_pipe_entry("- --baseline | action: accept")["id"] == "--baseline"


def test_parse_pipe_entry_drops_a_chunk_with_no_colon_rather_than_guessing() -> None:
    entry = markdown_sections.parse_pipe_entry("- F2 | stray chunk | action: accept")

    assert entry == {"id": "F2", "action": "accept"}
