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
