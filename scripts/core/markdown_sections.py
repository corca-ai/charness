"""The lines of one markdown section, from its heading to the next one.

Every artifact validator reads declared values out of a named `## Section`, and
each had grown its own copy of the same six-line walk: find the heading line,
collect following lines, stop at the next `## `. Five lexical clone families across
`validate_critique_artifacts.py`, `validate_ideation_artifact.py` and
`critique_enforcement_scope.py` (which carried three copies by itself) were all
this one shape.

The copies were not identical, and that is the argument for one home rather than
against it: some matched the heading with `strip() == heading`, one lowercased it,
one accepted the heading with a trailing colon, one accepted any `#` depth. A
reader auditing "which sections does this floor see" had to check each copy, and a
heading form fixed in one place stayed broken in the others — which is exactly how
C3's heading form went 46 artifacts unmatched while the line form was fixed twice.

Deliberately NOT owned here: what a caller does with the lines. Field maps,
bullet filters, first-non-empty-value reads and n-line joins are per-floor
decisions, and folding them in would couple four unrelated grammars to make the
extraction look bigger.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

#: Section boundary. `## ` only — a deeper `### ` heading is CONTENT of the
#: section above it, which is how the corpus writes subsections, and treating it
#: as a boundary would silently truncate every section that has one.
_BOUNDARY_PREFIX = "## "


def _heading_matches(line: str, headings: tuple[str, ...], *, case_insensitive: bool) -> bool:
    candidate = line.strip()
    if case_insensitive:
        candidate = candidate.lower()
    # A trailing colon is how part of the corpus writes these headings, and it is
    # never part of the heading's identity.
    return candidate in headings or candidate.rstrip(":") in headings


def lines_until_next_section(lines: Iterable[str]) -> list[str]:
    """``lines`` truncated at the first ``## `` boundary.

    The primitive for callers that locate the heading themselves because their
    heading grammar is their own — the blocked-signal floor accepts any ``#`` depth
    with an optional trailing colon from a set of spellings, and the fresh-eye line
    reader keys off a bare mid-line mention. Those two do not share a matcher with
    `section_lines`, but they do share the boundary rule, which is the half that
    kept getting re-derived.
    """
    collected: list[str] = []
    for raw in lines:
        if raw.strip().startswith(_BOUNDARY_PREFIX):
            break
        collected.append(raw)
    return collected


_FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


def _outside_fences(lines: list[str]) -> list[str]:
    """``lines`` with fenced-block content blanked, line positions preserved.

    Fenced text is SHOWN, not asserted. This repo has now read it as the author's
    claim on four separate gates, and the artifacts most likely to quote a canonical
    `## Section` block are critiques OF these validators. A quoted example heading
    was matched as the real one, so a floor read the example's fields — the wrong
    binding, or a refusal citing a packet the artifact never claimed.

    Blanking rather than dropping keeps every line index valid for callers that
    locate a heading themselves and then slice.
    """
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    for raw in lines:
        match = _FENCE_RE.match(raw)
        if match and not in_fence:
            in_fence, fence_marker = True, match.group(1)[0]
            out.append("")
            continue
        if match and in_fence and match.group(1)[0] == fence_marker:
            in_fence, fence_marker = False, ""
            out.append("")
            continue
        out.append("" if in_fence else raw)
    return out


def section_lines(
    text: str | list[str],
    heading: str | Iterable[str],
    *,
    case_insensitive: bool = False,
) -> list[str]:
    """The raw lines under ``heading``, excluding it, up to the next ``## `` or EOF.

    Headings and boundaries inside a fenced block are ignored: see `_outside_fences`.

    Returns ``[]`` for an absent heading AND for a present-but-empty section. Those
    two are not distinguishable here on purpose: no caller in this repo needs the
    difference, and a caller that ever does should read the heading's presence
    itself rather than have this function invent a sentinel.

    ``heading`` may be one heading or a set of accepted spellings. Lines are
    returned RAW (not stripped) so a caller whose grammar depends on indentation —
    a nested bullet, a fenced block inside the section — still sees it, except for
    fenced content, which is blanked.
    """
    lines = _outside_fences(text.splitlines() if isinstance(text, str) else list(text))
    headings = (heading,) if isinstance(heading, str) else tuple(heading)
    if case_insensitive:
        headings = tuple(value.strip().lower() for value in headings)
    else:
        headings = tuple(value.strip() for value in headings)
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if _heading_matches(line, headings, case_insensitive=case_insensitive)
        ),
        None,
    )
    if start is None:
        return []
    return lines_until_next_section(lines[start + 1 :])


def section_bullets(text: str | list[str], heading: str | Iterable[str]) -> list[str]:
    """The ``- `` bullet lines of a section, raw. The shape three structured-entry
    floors (critique findings, ideation questions) each re-derived."""
    return [line for line in section_lines(text, heading) if line.strip().startswith("- ")]


def section_field_map(text: str | list[str], heading: str | Iterable[str]) -> dict[str, str]:
    """``- Key: value`` bullets of a section as a lowercased-key map.

    Bold markers are stripped from keys and backticks from values because the
    corpus writes both (`- **Verdict**: \\`owned-correctly\\``), and a floor that
    read the decorated spelling as a different field silently found nothing.
    """
    fields: dict[str, str] = {}
    for raw in section_lines(text, heading):
        stripped = raw.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, _, value = stripped.lstrip("- ").partition(":")
        fields[key.replace("*", "").strip().lower()] = value.strip().strip("`")
    return fields


def parse_pipe_entry(raw: str) -> dict[str, str]:
    """One ``- <id> | key: value | key: value`` bullet as a lowercased-key map.

    The structured-entry grammar the critique `## Structured Findings` and ideation
    `## Structured Questions` floors both enforce, byte-identical in each. Sharing
    it means the two cannot disagree about what an entry IS while both claiming to
    enforce required fields on it.

    A leading chunk with no colon is the entry ``id``; without one, no ``id`` key is
    produced at all, which is how both callers tell "this entry has no id" from "its
    id is empty". Chunks with no colon after the head are dropped rather than
    guessed at. Returns ``{}`` for a bullet with no content.
    """
    # ONE leading bullet marker, via regex. `lstrip("- ")` takes a character SET,
    # so it ate every leading `-` and space: an id of `-1` collided with `1` as a
    # bogus duplicate, and `--baseline` silently became `baseline`. Both copies this
    # replaced carried that bug.
    body = re.sub(r"^[-*][ \t]+", "", raw.strip()).strip()
    parts = [chunk.strip() for chunk in body.split("|") if chunk.strip()]
    if not parts:
        return {}
    fields: dict[str, str] = {}
    if ":" in parts[0]:
        rest = parts
    else:
        fields["id"] = parts[0]
        rest = parts[1:]
    for chunk in rest:
        if ":" not in chunk:
            continue
        key, _, value = chunk.partition(":")
        fields[key.strip().lower()] = value.strip()
    return fields


def leading_nonempty(lines: Iterable[str], limit: int) -> list[str]:
    """The first ``limit`` non-empty lines, stripped and lowercased.

    The read two fresh-eye status paths share: a declared status can wrap over a
    few lines, and both wanted a bounded join rather than the whole section.
    """
    collected: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        collected.append(stripped.lower())
        if len(collected) >= limit:
            break
    return collected
