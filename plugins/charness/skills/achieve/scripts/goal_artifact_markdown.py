"""Markdown parsing helpers shared by achieve goal-artifact gates."""
from __future__ import annotations


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
