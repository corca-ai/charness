"""Markdown parsing helpers shared by achieve goal-artifact gates."""
from __future__ import annotations

import re


def mask_fences(text: str) -> str:
    """Blank fenced code-block regions while preserving offsets and newlines.

    Heading and marker scans run on the masked copy so examples inside fenced
    blocks stay inert. If a fence is unbalanced, fail open and trust the raw text;
    masking to EOF would hide real sections after the unmatched fence.

    That fail-open leaves fenced examples visible, which is how a template's
    `Created:` / `Activation:` / `- Decision:` line got read as the author's own.
    The tempting repair -- mask every balanced region and return only the unclosed
    tail raw -- is WRONG, and was measured wrong: fences are paired left to right,
    so ONE stray marker early in the file re-pairs every later fence and masks the
    real sections between them, turning a malformed-markdown goal into a false
    "missing sections" refusal. With odd parity nothing in the text says which
    marker is the stray one.

    So this function keeps failing open, and the answer to "which reading is real"
    moves to the callers that render verdicts: `fences_balanced` lets them refuse
    (or fail closed) on an unbalanced document instead of silently picking one of
    two irreconcilable readings.
    """
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    if in_fence:
        return text
    return "".join(masked)


def fences_balanced(text: str) -> bool:
    """False when a fence marker is left unclosed, so `mask_fences` failed open.

    A caller that reads a field out of the masked body is reading the RAW body in
    that case, fenced examples included. This is the fact that lets it say so
    rather than render a verdict over a reading it could not establish.
    """
    return sum(1 for line in text.splitlines() if line.lstrip().startswith(("```", "~~~"))) % 2 == 0


_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)

# A line that *starts* a new block construct, so it is never a soft-wrap
# continuation of the line above: a list item, a heading, a table row, or a
# ``Label:`` field. The field label allows interior spaces (for example,
# ``Host log probe:``) but is length-bounded and must be followed by whitespace,
# which biases toward NOT joining an ambiguous ``word word:`` tail — a missed
# join only reverts to the old per-physical-line behavior, whereas an over-join
# would leak an adjacent field's value into this one.
_BLOCK_STARTER = re.compile(
    r"^[ \t]*(?:[-*+] |#{1,6} |\||[A-Za-z][A-Za-z ./-]{0,40}:\s)",
)


def join_soft_wraps(section_body: str) -> str:
    """Reflow markdown soft-wraps so a logically-single line is one physical line.

    A non-blank line that does not itself begin a new block construct (list item,
    heading, table row, or ``Label:`` field — see ``_BLOCK_STARTER``) is treated
    as a soft-wrap continuation of the preceding line and joined with a space;
    markdown renders the two that way. A blank line or a block-starter line
    protects the line above it (a later continuation attaches to the blank line
    instead), so a step line followed by a blank line or another field is never
    merged.

    Structured artifact fields may be wrapped across physical lines, so a value
    whose tail sits on the next line is kept together. This is a presentation
    normalization only; the owning floor still decides whether the resulting
    field is valid.
    """
    return "\n".join(text for _, text in logical_lines(section_body))


def logical_lines(section_body: str) -> list[tuple[int, str]]:
    """``(1-based physical line where it starts, joined text)`` per logical line.

    The reflow rule is ``join_soft_wraps``'; this is the same walk keeping the
    origin of each logical line, so a floor can both READ a soft-wrapped value and
    SAY where it is. Reporting the joined text with no location leaves the author
    hunting for a line that, by construction, is not the one they see.
    """
    out: list[tuple[int, str]] = []
    for index, raw in enumerate(section_body.splitlines(), start=1):
        if out and raw.strip() and not _BLOCK_STARTER.match(raw):
            out[-1] = (out[-1][0], f"{out[-1][1]} {raw.strip()}")
        else:
            out.append((index, raw))
    return out


def section_bounds(masked: str, section: str, *, casefold: bool = False) -> tuple[int, int] | None:
    """Offsets of one ``## <section>`` body inside a fence-masked artifact.

    ``(body_start, body_end)``: the offset just past the heading line, and the
    offset of the next ``##`` heading (or end of text). Offsets rather than the
    slice itself, because the two things callers do with a section need the same
    two numbers — READ the body, or INSERT at its end (``start`` is exactly the
    insertion point after the heading line).

    ONE owner. Several goal-artifact helpers had hand-rolled this same walk, each
    subtly its own: masked-vs-raw, ``""``-vs-``None`` for absent, case-sensitive or
    not. Keeping the walk here prevents those readers from drifting apart.
    """
    matches = section_bounds_all(masked, section, casefold=casefold)
    return matches[0] if matches else None


def section_bounds_all(masked: str, section: str, *, casefold: bool = False) -> list[tuple[int, int]]:
    """Offsets for every ``## <section>`` body in a fence-masked artifact.

    A first-match reader is safe for append-only helpers, but not for a verdict:
    a duplicate heading can put written content before an empty/template copy (or
    the reverse) and make the answer depend on order. The all-occurrences reader
    keeps that decision at the shared markdown boundary so consumers that render
    a verdict can inspect every matching body.
    """
    headings = list(_H2.finditer(masked))
    matches: list[tuple[int, int]] = []
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        if (name.lower() != section.lower()) if casefold else (name != section):
            continue
        body_start = masked.find("\n", match.start())
        start = match.end() if body_start == -1 else body_start + 1
        end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        matches.append((start, end))
    return matches


def required_heading_report(
    masked: str,
    required_sections: tuple[str, ...],
    portability_sections: tuple[str, ...],
) -> tuple[list[str], list[str], list[str]]:
    """Return missing-required, missing-portability, and duplicate H2 names."""
    headings = [match.group(1).strip() for match in _H2.finditer(masked)]
    present = set(headings)
    missing = [section for section in required_sections if section not in present]
    duplicate_sections = [
        section for section in required_sections + portability_sections
        if headings.count(section) > 1
    ]
    portability_missing = [
        section for section in portability_sections if section not in present
    ]
    return missing, portability_missing, duplicate_sections


def slice_plan_data_row_count(text: str) -> int:
    """Count data rows in the first markdown table inside ``## Slice Plan``."""
    masked = mask_fences(text)
    headings = list(_H2.finditer(masked))
    section_text: str | None = None
    for index, match in enumerate(headings):
        if match.group(1).strip() != "Slice Plan":
            continue
        body_start = masked.find("\n", match.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        section_text = masked[body_start + 1 if body_start != -1 else match.start():body_end]
        break
    if section_text is None:
        return 0
    seen_header = False
    seen_separator = False
    data_rows = 0
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if seen_header:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        is_separator = bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)
        if not seen_header:
            seen_header = True
            continue
        if not seen_separator and is_separator:
            seen_separator = True
            continue
        if is_separator:
            continue
        data_rows += 1
    return data_rows
