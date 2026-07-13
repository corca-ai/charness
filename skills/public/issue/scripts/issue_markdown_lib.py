from __future__ import annotations


def strip_code_fences(text: str) -> list[str]:
    """Return Markdown lines outside fenced code blocks."""
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return lines
