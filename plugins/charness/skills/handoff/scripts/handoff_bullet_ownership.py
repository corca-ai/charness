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
- A hash plus a small ordinal in ordinary prose ("the hash-one priority", written
  with the symbol) and an all-digit six-hex-digit colour still read as issue ids.
- A fenced block owns NOTHING. `- Reproduce with:` followed by a command block
  is charged as unowned, because the owned sections are a flat list of links and
  a bullet that needs a code block belongs in the artifact it should link.
- A list item's second paragraph is not read: a blank line ends the entry, so an
  owner placed below one is not found. Same reason -- that is not the shape.
- An UNCLOSED fence leaves every later line inside it, so both owned sections
  become unscannable and the artifact passes in silence. Nothing reports this;
  the markdown lint gate is the surface that should notice an unclosed fence.
- `validate_nonempty_sections` in the repo validator is still fence-blind, so a
  handoff carrying a fenced `##` heading fails there first, naming a different
  defect than the one the author has.
"""
from __future__ import annotations

import re
from typing import Iterator, Sequence

OWNED_SECTIONS = ("## Current State", "## Next Session")

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
URL_RE = re.compile(r"\bhttps?://\S+")
# The left boundary is the same guard the sibling count rule in
# `validate_handoff_artifact` already carries: without it `issue<id>`, `PR<id>`,
# and `guide.md<anchor>` all read as issue ids.
ISSUE_ID_RE = re.compile(r"(?<![#\w.\-])#\d+\b")
# Equal-length backtick runs, so `` `a` and `b` `` yields two single-token spans
# instead of one span made of the prose between them, and ``` ``git log -n`` ```
# reads as one span rather than two empty ones. An UNBALANCED backtick matches
# nothing, which is the safe direction: a dropped closing backtick used to turn
# the rest of the entry into a "command" and launder the bullet.
CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
# A fence closes only on its OWN marker character, in a run at least as long as
# the one that opened it -- CommonMark. A plain `(```|~~~)` toggle treats a
# `~~~` line inside a backtick fence as a delimiter and inverts the state for
# the rest of the document; `scripts/markdown_doc_scan.py` documents that exact
# bug, and this module reintroduced it once already.
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s*## ")


def _is_command_span(content: str) -> bool:
    """Is this code-span content something to RUN, not a name to go find?

    Arguments are the whole test. Stripping first is load-bearing: CommonMark
    requires padding when the content starts or ends with a backtick, and an
    unstripped check read a padded bare identifier as a command.

    A path is deliberately NOT accepted. It reads like an owner, but two shipped
    surfaces tell the author a bare code-span path is not one, and this repo's
    link gate rejects a backticked repo path in the handoff outright -- so
    accepting it here would bless a form that cannot ship. Paths are links.
    """
    stripped = content.strip()
    return any(char.isspace() for char in stripped)


def has_owner(text: str) -> bool:
    """Does this entry give the reader something to open, run, or look up?"""
    if MARKDOWN_LINK_RE.search(text) or URL_RE.search(text) or ISSUE_ID_RE.search(text):
        return True
    return any(_is_command_span(match.group(2)) for match in CODE_SPAN_RE.finditer(text))


def _walk(lines: Sequence[str]) -> Iterator[tuple[int, str, bool]]:
    """`(index, raw, inside_or_delimiting_a_fence)` with CommonMark fences."""
    open_marker: str | None = None
    for index, raw in enumerate(lines):
        match = FENCE_RE.match(raw)
        if match is not None:
            run = match.group(1)
            if open_marker is None:
                open_marker = run
            elif run[0] == open_marker[0] and len(run) >= len(open_marker):
                open_marker = None
            yield index, raw, True
            continue
        yield index, raw, open_marker is not None


def _section_bounds(lines: Sequence[str], heading: str) -> tuple[int, int] | None:
    """Bounds of a section, ignoring headings that only appear inside fences.

    Fence-blindness here was a whole-section bypass: a fenced example holding a
    `## Next Session` line bound `start` to the EXAMPLE and `end` to the real
    heading, so the real section was never scanned.
    """
    start: int | None = None
    for index, raw, fenced in _walk(lines):
        if fenced:
            continue
        if start is None:
            if raw.strip() == heading:
                start = index + 1
            continue
        if HEADING_RE.match(raw):
            return start, index
    return (start, len(lines)) if start is not None else None


def _entries(section_lines: Sequence[str]) -> list[tuple[int, str]]:
    """`(offset, joined text)` for each list entry in a FLAT list.

    The handoff's owned sections are a flat unordered list of link-plus-one-line
    entries. Every parser feature that supported a richer shape -- attaching a
    fenced block to the bullet above it, merging a nested child into its parent,
    carrying an entry across a blank line into a second paragraph -- produced a
    defect in the round that read it, and each new defect came from those
    branches INTERACTING. Two review rounds in a row found a laundering path
    built out of two individually-reasonable rules.

    So the shape is narrow on purpose: an entry starts at a list marker, absorbs
    following non-blank lines, and ends at a blank line, the next marker, or the
    next heading. Fenced blocks are skipped entirely and own nothing, which is
    also what detaches the `charness-publish-state-claim` ledger block from the
    bullet above it without needing a rule about HTML comments.
    """
    entries: list[tuple[int, str]] = []
    current: list[str] = []
    current_offset: int | None = None

    def flush() -> None:
        nonlocal current_offset, current
        if current_offset is not None and current:
            entries.append((current_offset, " ".join(current)))
        current_offset, current = None, []

    for index, raw, fenced in _walk(section_lines):
        if fenced:
            flush()
            continue
        stripped = raw.strip()
        if not stripped:
            flush()
            continue
        if LIST_ITEM_RE.match(raw):
            if current_offset is not None and raw[:1].isspace():
                # A nested child under an open parent: the parent already
                # carries the owner, and charging the child would demand the
                # same link twice.
                current.append(stripped)
                continue
            flush()
            current_offset, current = index, [stripped]
            continue
        if current_offset is not None:
            current.append(stripped)
    flush()
    return entries


def unowned_entries(lines: Sequence[str]) -> list[tuple[str, int, str]]:
    """`(section, 1-indexed line number, entry text)` for every unowned entry."""
    found: list[tuple[str, int, str]] = []
    for heading in OWNED_SECTIONS:
        bounds = _section_bounds(lines, heading)
        if bounds is None:
            continue
        start, end = bounds
        for offset, text in _entries(lines[start:end]):
            if not has_owner(text):
                found.append((heading, start + offset + 1, text))
    return found
