from __future__ import annotations


def extract_section(text: str, heading: str) -> str:
    """Return one level-two Markdown section body without its heading."""
    lines = text.splitlines()
    target = heading.strip().lower()
    start = next(
        (index + 1 for index, line in enumerate(lines) if line.strip().lower() == target),
        None,
    )
    if start is None:
        return ""
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return "\n".join(lines[start:end])
