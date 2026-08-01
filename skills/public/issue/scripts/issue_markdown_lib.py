from __future__ import annotations

#: Both CommonMark fence markers. `~~~` was missing, so a quoted example inside a
#: tilde fence was read as real content by every caller — the closeout body's
#: `Critique:` scanner and the resolution critique's own `Fresh-eye satisfaction:`
#: reader alike. The repo's authoring-side readers already handle both, so this
#: was a parity gap on the side that runs at the irreversible boundary.
_FENCE_MARKERS = ("```", "~~~")


def strip_code_fences(text: str) -> list[str]:
    """Return Markdown lines outside fenced code blocks.

    A fence is closed only by its OWN marker: a `~~~` line inside a ``` block is
    content, not a close. Tracking which marker opened the block keeps a document
    that quotes one fence style inside the other from inverting the whole scan.
    """
    lines: list[str] = []
    open_marker: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if open_marker is None:
            marker = next((m for m in _FENCE_MARKERS if stripped.startswith(m)), None)
            if marker is not None:
                open_marker = marker
                continue
        elif stripped.startswith(open_marker):
            open_marker = None
            continue
        if open_marker is None:
            lines.append(line)
    return lines
