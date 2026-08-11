"""Every state/next-action entry must carry an OWNER the reader can open or run.

The size budget in ``handoff_content_budget`` measures how MUCH the artifact
says. This module measures whether what it says has an address. They are
different defects and the budget cannot reach this one: an author who trims to
fit the ceiling produces shorter unowned prose, not owned prose.

The shape this exists to force is a section that reads

    ## Current State
    - [what changed](../path/to/owner.md)
    - [the next constraint](../path/to/other.md)

rather than paragraphs asserting what those artifacts contain. Prose describing
another artifact's contents without pointing at it is wrong the moment the other
artifact moves, and nothing is watching. A pointer makes the claim checkable in
one click; a command makes a fact regenerate instead of decay.

Scope is deliberately narrow. `## Current State` and `## Next Session` assert
what is true now and what to do next, and both go stale between sessions.
`## Discuss` is exempt because an open question legitimately has no owner yet;
that is what makes it open.

Known non-claims -- this is a FLOOR, not a completeness proof:

- `## Workflow Trigger` and `## Continuation Capability` are NOT read. A wrong
  paraphrase there passes, and one has already shipped (a handoff misnamed the
  recent-lessons digest's slot sections from the Workflow Trigger). Do not cite
  that incident as this rule's catch; it is out of scope by construction.
- An entry passes on ONE owner even when it makes several claims, so a bullet
  that links one artifact and paraphrases a second still passes.
- The link is not followed. A pointer to an artifact that contradicts the entry
  passes exactly like a correct one.
- Only list entries are checked; a bare paragraph under a covered heading is not
  reached, because widening to prose would fire on a section's framing sentence.
- `#\\d+` is GitHub-shaped. A repo whose tracker uses `PROJ-123` effectively has
  two owner forms, not three, until an adapter names its id shape.
"""
from __future__ import annotations

import re
from typing import Iterator, Sequence

OWNED_SECTIONS = ("## Current State", "## Next Session")

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
URL_RE = re.compile(r"\bhttps?://\S+")
# The left boundary is the same guard the sibling count rule in
# `validate_handoff_artifact` already carries: without it `issue<id>`,
# `PR<id>`, and `guide.md<anchor>` all read as issue ids. Residual, accepted
# and NOT fixed here: a hash plus a small ordinal in ordinary prose ("the hash-1
# priority") and an all-digit six-hex-digit colour still match. Separating those
# needs a content classifier, which this repo keeps out of gates on purpose.
ISSUE_ID_RE = re.compile(r"(?<![#\w.\-])#\d+\b")
# Equal-length backtick runs, so `` `a` and `b` `` yields two single-token spans
# instead of one span made of the prose between them, and ``` ``git log -n`` ```
# (the form an author must use when the command itself contains a backtick)
# reads as one span rather than two empty ones. An UNBALANCED backtick matches
# nothing at all, which is the safe direction: a dropped closing backtick used
# to turn the rest of the entry into a "command" and launder the bullet.
CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
# Whether an indented marker STARTS an entry is relative, not absolute. With a
# parent entry open it is a sub-bullet elaborating an already-owned claim, and
# charging it separately would push authors to repeat the same link on every
# child. With no entry open there is no parent to inherit from, so it must be
# checked -- the anchored form dropped those lines entirely, which is worse than
# a false pass because nothing was reported at all.
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
# A fence closes only on its OWN marker character, in a run at least as long as
# the one that opened it -- CommonMark. A plain `(```|~~~)` toggle treats a
# `~~~` line inside a backtick fence as a delimiter and inverts the state for
# the rest of the document; `scripts/markdown_doc_scan.py` documents that exact
# bug, and this module reintroduced it once already.
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s*## ")


def has_owner(text: str) -> bool:
    """Does this entry give the reader something to open, run, or look up?"""
    if MARKDOWN_LINK_RE.search(text) or URL_RE.search(text) or ISSUE_ID_RE.search(text):
        return True
    # Whitespace inside a span is the command test: `git log --oneline` is
    # runnable, `inventory_boundary_bypass_lib` is a name to go find.
    return any(" " in match.group(2) or "\t" in match.group(2) for match in CODE_SPAN_RE.finditer(text))


def _walk(lines: Sequence[str]) -> Iterator[tuple[int, str, bool, bool]]:
    """`(index, raw, is_fence_delimiter, inside_fence)` with CommonMark fences."""
    open_marker: str | None = None
    for index, raw in enumerate(lines):
        match = FENCE_RE.match(raw)
        if match is not None:
            run = match.group(1)
            if open_marker is None:
                open_marker = run
                yield index, raw, True, True
                continue
            if run[0] == open_marker[0] and len(run) >= len(open_marker):
                open_marker = None
                yield index, raw, True, False
                continue
        yield index, raw, False, open_marker is not None


def _section_bounds(lines: Sequence[str], heading: str) -> tuple[int, int] | None:
    """Bounds of a section, ignoring headings that only appear inside fences.

    Fence-blindness here was a whole-section bypass: a fenced example holding a
    `## Next Session` line bound `start` to the EXAMPLE and `end` to the real
    heading, so the real section was never scanned and the reported line numbers
    pointed into a code block.
    """
    start: int | None = None
    for index, raw, is_delimiter, inside in _walk(lines):
        if is_delimiter or inside:
            continue
        stripped = raw.strip()
        if start is None:
            if stripped == heading:
                start = index + 1
            continue
        if HEADING_RE.match(raw):
            return start, index
    return (start, len(lines)) if start is not None else None


def _entries(section_lines: Sequence[str]) -> list[tuple[int, str, bool]]:
    """`(offset, joined text, owns a fenced block)` for each list entry.

    A blank line does not end an entry on its own: a list item may hold several
    paragraphs, and the owner is often in the second one. The entry ends when a
    new list item, a heading, or an UNINDENTED non-blank line arrives. That last
    case is what detaches the `charness-publish-state-claim` marker comment (and
    the ledger fence below it) from the bullet above -- attaching a fence across
    arbitrary intervening content permanently exempted the last bullet of the
    live artifact's `## Current State`.
    """
    entries: list[list] = []
    current: list[str] = []
    current_offset: int | None = None
    pending_blank = False

    def flush() -> None:
        if current_offset is not None and current:
            entries.append([current_offset, " ".join(current), False])

    for index, raw, is_delimiter, inside in _walk(section_lines):
        if is_delimiter:
            # Attach only to an entry that is still open, or one separated from
            # the fence by blank lines alone.
            if current_offset is not None:
                flush()
                entries[-1][2] = True
                current_offset, current, pending_blank = None, [], False
            continue
        if inside:
            continue
        stripped = raw.strip()
        if not stripped:
            pending_blank = True
            continue
        indented = raw[:1].isspace()
        if LIST_ITEM_RE.match(raw) and (not indented or current_offset is None):
            flush()
            current_offset, current, pending_blank = index, [stripped], False
            continue
        if current_offset is None:
            continue
        if pending_blank and not indented:
            # A new unindented paragraph, not a continuation of the list item.
            flush()
            current_offset, current, pending_blank = None, [], False
            continue
        current.append(stripped)
        pending_blank = False
    flush()
    return [(offset, text, owns_fence) for offset, text, owns_fence in entries]


def unowned_entries(lines: Sequence[str]) -> list[tuple[str, int, str]]:
    """`(section, 1-indexed line number, entry text)` for every unowned entry."""
    found: list[tuple[str, int, str]] = []
    for heading in OWNED_SECTIONS:
        bounds = _section_bounds(lines, heading)
        if bounds is None:
            continue
        start, end = bounds
        for offset, text, owns_fence in _entries(lines[start:end]):
            if not owns_fence and not has_owner(text):
                found.append((heading, start + offset + 1, text))
    return found
