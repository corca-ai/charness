"""Line-splice helpers for prompt mutant removal and rewrite operators."""

from __future__ import annotations


def remove_unit_by_lines(text: str, start_line: int, end_line: int) -> str:
    lines = text.splitlines(keepends=True)
    return "".join(lines[: start_line - 1] + lines[end_line:])


def applied_replacement_text(text: str, end_line: int, replacement_text: str) -> str:
    lines = text.splitlines(keepends=True)
    if replacement_text and len(lines) > end_line and not replacement_text.endswith(("\n", "\r")):
        return replacement_text + "\n"
    return replacement_text


def rewrite_unit_by_lines(text: str, start_line: int, end_line: int, replacement_text: str) -> str:
    lines = text.splitlines(keepends=True)
    suffix = "".join(lines[end_line:])
    return "".join(lines[: start_line - 1]) + applied_replacement_text(text, end_line, replacement_text) + suffix


def rewrite_matching_public_unit(
    public_text: str, unit: dict, public_units: list[dict], replacement_text: str | None
) -> str | None:
    matches = [
        candidate
        for candidate in public_units
        if candidate["heading_path"] == unit["heading_path"] and candidate["content_sha256"] == unit["content_sha256"]
    ]
    if len(matches) != 1:
        return None
    match = matches[0]
    if replacement_text is None:
        return remove_unit_by_lines(public_text, match["start_line"], match["end_line"])
    return rewrite_unit_by_lines(public_text, match["start_line"], match["end_line"], replacement_text)
