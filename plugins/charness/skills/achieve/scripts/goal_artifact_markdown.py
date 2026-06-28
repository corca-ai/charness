"""Markdown parsing helpers shared by achieve goal-artifact gates."""
from __future__ import annotations

import re


def mask_fences(text: str) -> str:
    """Blank fenced code-block regions while preserving offsets and newlines.

    Heading and marker scans run on the masked copy so examples inside fenced
    blocks stay inert. If a fence is unbalanced, fail open and trust the raw text;
    masking to EOF would hide real sections after the unmatched fence.
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


_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)

# A line that *starts* a new block construct, so it is never a soft-wrap
# continuation of the line above: a list item, a heading, a table row, or a
# ``Label:`` field. The field label allows interior spaces (``Issue closeout:``,
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

    The Created-gated coordination/phase-routing floors match their
    ``Routing:``/``Gather:``/``Release:``/``Issue closeout:`` step lines per
    *physical* line, so a correct value whose tail (or routed skill name) wrapped
    onto the next physical line was false-rejected; joining first removes that.
    Inseparable shadow (accepted, not a no-op): a step value whose required token
    sits on an immediately-following continuation line is now also accepted —
    nothing distinguishes a legitimate wrap from prose completion. Acceptable
    because these are presence-only, self-authored, reversible closeout floors and
    the content is substantively present across the wrap; it is not a path for a
    wrong answer to reach an irreversible boundary.
    """
    out: list[str] = []
    for raw in section_body.splitlines():
        if out and raw.strip() and not _BLOCK_STARTER.match(raw):
            out[-1] = f"{out[-1]} {raw.strip()}"
        else:
            out.append(raw)
    return "\n".join(out)


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
