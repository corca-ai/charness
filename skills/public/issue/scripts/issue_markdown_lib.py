from __future__ import annotations

#: Both CommonMark fence characters. The opener length is retained because a
#: four-backtick fence is not closed by a three-backtick example inside it.
_FENCE_CHARS = ("`", "~")


def _closing_fence(line: str, opener: str) -> bool:
    """A closer must use the same marker, be at least as long, and have no tail."""
    leading = len(line) - len(line.lstrip(" "))
    if leading > 3:
        return False
    body = line[leading:]
    if not body or any(char != opener[0] for char in body):
        return False
    return len(body) >= len(opener)


def _opening_fence(line: str) -> str | None:
    leading = len(line) - len(line.lstrip(" "))
    if leading > 3:
        return None
    stripped = line[leading:]
    for char in _FENCE_CHARS:
        if not stripped.startswith(char * 3):
            continue
        length = 0
        while length < len(stripped) and stripped[length] == char:
            length += 1
        return char * length
    return None


def strip_code_fences(text: str) -> list[str]:
    """Return Markdown lines outside fenced code blocks.

    A fence is closed only by its OWN marker: a `~~~` line inside a ``` block is
    content, not a close. Tracking which marker opened the block keeps a document
    that quotes one fence style inside the other from inverting the whole scan.
    """
    lines: list[str] = []
    open_marker: str | None = None
    for line in text.splitlines():
        if open_marker is None:
            marker = _opening_fence(line)
            if marker is not None:
                open_marker = marker
                continue
        elif _closing_fence(line, open_marker):
            open_marker = None
            continue
        if open_marker is None:
            lines.append(line)
    return lines
