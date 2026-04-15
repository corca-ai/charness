from __future__ import annotations

import re
from collections.abc import Iterable

H2_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def extract_h2_section_lines(text: str, heading: str) -> list[str]:
    lines = strip_frontmatter(text).splitlines()
    wanted = heading.strip().lower()
    start: int | None = None
    for index, line in enumerate(lines):
        match = H2_HEADING_RE.match(line.strip())
        if match and match.group(1).strip().lower() == wanted:
            start = index + 1
            break
    if start is None:
        return []
    end = len(lines)
    for index in range(start, len(lines)):
        if H2_HEADING_RE.match(lines[index].strip()):
            end = index
            break
    return lines[start:end]


def count_fence_blocks(lines: Iterable[str]) -> int:
    count = 0
    in_fence = False
    for raw in lines:
        line = raw.strip()
        if not line.startswith("```"):
            continue
        if in_fence:
            in_fence = False
            continue
        count += 1
        in_fence = True
    return count


def strip_fenced_lines(lines: Iterable[str]) -> list[str]:
    result: list[str] = []
    in_fence = False
    for raw in lines:
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(raw)
    return result
