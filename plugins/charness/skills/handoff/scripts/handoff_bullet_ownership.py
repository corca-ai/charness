"""Every state/next-action entry must carry an OWNER the reader can open or run.

The size budget in ``handoff_content_budget`` measures how MUCH the artifact
says. This module measures whether what it says has an address. They are
different defects and the budget cannot reach this one: an author who trims to
fit the ceiling produces shorter unowned prose, not owned prose.

The failure this guards is measured, not hypothetical. The handoff claimed the
recent-lessons digest's "4 trap slots dropped the two sharpest lessons"; the
lessons in question came from a retro's `Next Improvements` and route to the
CHECKLIST slots. A paraphrase of another artifact's contents, written without a
pointer to it, was wrong at the moment it was written and stayed wrong because
nobody owned it. Had the bullet carried the link, the next reader would have
opened the digest and seen the section names.

So the rule is ownership, not brevity: an entry may point at an artifact (a
link), or at a fact the reader can regenerate (a command), or at a stable
external identifier (an issue id). An entry that does none of these is asking
the reader to trust a claim with no way to check it, and the correct fix is
usually to spill the detail to the artifact that owns it and link that.

Scope is deliberately narrow. `## Current State` and `## Next Session` are the
sections whose bullets ROT — they assert what is true now and what to do next,
and both go stale between sessions. `## Discuss` is exempt because an open
question legitimately has no owner yet; that is what makes it open.
`## Workflow Trigger` and `## Continuation Capability` are out of scope here.

Known non-claims:

- Only list entries are checked. A bare paragraph under these sections is not
  reached, because the artifact shape is bulleted by convention and widening the
  rule to prose would fire on the section's own framing sentence.
- An entry passes on ONE owner even when it makes several claims, so a bullet
  that links one artifact and paraphrases a second still passes. This is a
  floor, not a completeness proof.
- A code span is read as a command when it contains whitespace, which is what
  separates something you can run from an identifier you must go find. A
  multi-word code span that is not a command passes; no executable allow-list is
  used, because that list would be wrong in the first consuming repo that builds
  with something this one does not.
"""
from __future__ import annotations

import re
from typing import Sequence

OWNED_SECTIONS = ("## Current State", "## Next Session")

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
URL_RE = re.compile(r"\bhttps?://\S+")
ISSUE_ID_RE = re.compile(r"#\d+\b")
# Ordered items too: this repo's `## Next Session` is a numbered queue, and a
# rule that only saw `-` would have exempted the section it most needed to read.
TOP_LEVEL_ITEM_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")


def has_owner(text: str) -> bool:
    """Does this entry give the reader something to open or run?

    The command test is whitespace INSIDE a code span: `git log --oneline` is
    runnable, `inventory_boundary_bypass_lib` is a name the reader has to go
    locate. Spans are taken by SPLITTING on backticks, never matched with a
    regex like `` `[^`]*\\s[^`]*` ``. That form is wrong in a way that passes
    review: given two adjacent single-token spans, its leftmost match starts at
    the CLOSING backtick of the first and ends at the OPENING backtick of the
    second, so the whitespace it found was the prose between them. Measured
    effect was a live handoff bullet holding two bare identifiers and no
    pointer, which this gate read as carrying a command.
    """
    if MARKDOWN_LINK_RE.search(text) or URL_RE.search(text) or ISSUE_ID_RE.search(text):
        return True
    spans = [span.strip() for span in text.split("`")[1::2]]
    return any(span and any(char.isspace() for char in span) for span in spans)


def _entries(section_lines: Sequence[str]) -> list[tuple[int, str, bool]]:
    """`(offset, joined text, owns a fenced block)` for each list entry.

    An indented list marker continues its parent rather than starting a new
    entry: a sub-bullet elaborating an owned parent has an owner already, and
    charging it separately would push authors to repeat the same link.

    A fenced block attaches to the most recently STARTED entry, across blank
    lines: `- Reproduce with:` then a blank then a bash block is idiomatic
    markdown, and reading only inline spans would reject the replacement this
    rule recommends. Attaching across the blank is deliberately generous --
    a fence late in a section can launder an unowned entry above it, which is
    the cheaper error. Refusing a correctly-authored command block would push
    authors away from carrying commands at all, and this rule is a floor.
    """
    entries: list[list] = []
    current: list[str] = []
    current_offset: int | None = None
    in_fence = False

    def flush() -> None:
        if current_offset is not None and current:
            entries.append([current_offset, " ".join(current), False])

    for offset, raw in enumerate(section_lines):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            if in_fence:
                flush()
                current_offset, current = None, []
                if entries:
                    entries[-1][2] = True
            continue
        if in_fence:
            continue
        stripped = raw.strip()
        if not stripped:
            flush()
            current_offset, current = None, []
            continue
        if TOP_LEVEL_ITEM_RE.match(raw):
            flush()
            current_offset, current = offset, [stripped]
            continue
        if current_offset is not None:
            current.append(stripped)
    flush()
    return [(offset, text, owns_fence) for offset, text, owns_fence in entries]


def _section_bounds(lines: Sequence[str], heading: str) -> tuple[int, int] | None:
    start: int | None = None
    for index, raw in enumerate(lines):
        stripped = raw.strip()
        if start is None:
            if stripped == heading:
                start = index + 1
            continue
        if stripped.startswith("## "):
            return start, index
    return (start, len(lines)) if start is not None else None


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
