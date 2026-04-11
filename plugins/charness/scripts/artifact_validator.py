#!/usr/bin/env python3

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from pathlib import Path

H2_RE = re.compile(r"^##\s+.+$")


class ValidationError(Exception):
    pass


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        raise ValidationError(f"missing artifact `{path}`")
    return path.read_text(encoding="utf-8").splitlines()


def validate_max_lines(lines: Sequence[str], *, max_lines: int, artifact_label: str) -> None:
    if len(lines) > max_lines:
        raise ValidationError(
            f"{artifact_label} should stay concise; archive or move durable detail before it grows past {max_lines} lines"
        )


def validate_title(
    lines: Sequence[str],
    *,
    title_predicate: Callable[[str], bool],
    error_message: str,
) -> None:
    if not lines or not title_predicate(lines[0].strip()):
        raise ValidationError(error_message)


def validate_date_line(lines: Sequence[str]) -> None:
    if len(lines) < 2 or not lines[1].startswith("Date: "):
        raise ValidationError("artifact must record `Date: YYYY-MM-DD` on line 2")


def find_index(lines: Sequence[str], heading: str) -> int:
    for index, line in enumerate(lines):
        if line.strip() == heading:
            return index
    raise ValidationError(f"missing required section `{heading}`")


def validate_section_order(lines: Sequence[str], required_sections: Sequence[str]) -> None:
    indices = [find_index(lines, heading) for heading in required_sections]
    if indices != sorted(indices):
        raise ValidationError("required sections must stay in canonical order")


def iter_h2_headings(lines: Sequence[str]) -> list[str]:
    return [line.strip() for line in lines if H2_RE.match(line.strip())]


def validate_exact_h2_sections(lines: Sequence[str], required_sections: Sequence[str]) -> None:
    headings = iter_h2_headings(lines)
    if headings != list(required_sections):
        raise ValidationError(
            "artifact must use only the canonical sections: "
            + ", ".join(f"`{heading}`" for heading in required_sections)
        )


def validate_nonempty_sections(lines: Sequence[str], required_sections: Sequence[str]) -> None:
    for index, heading in enumerate(required_sections):
        start = find_index(lines, heading) + 1
        end = len(lines)
        if index + 1 < len(required_sections):
            end = find_index(lines, required_sections[index + 1])
        section_lines = [line.strip() for line in lines[start:end] if line.strip()]
        if not section_lines:
            raise ValidationError(f"`{heading}` must not be empty")

