"""Validation for the quality artifact's semantic surface-contract packet."""

from __future__ import annotations

import re
from collections.abc import Sequence

from runtime_bootstrap import import_repo_module

_markdown_sections = import_repo_module(__file__, "scripts.core.markdown_sections")


SECTION = "## Surface Contract Review"
FIELDS = (
    ("semantic coverage", "- semantic coverage:"),
    ("surface", "- surface:"),
    ("owner", "- owner:"),
    ("projections", "- projections:"),
    ("state scope", "- state scope:"),
    ("transitions", "- transitions:"),
    ("proof boundary", "- proof boundary:"),
    ("unexamined axes", "- unexamined axes:"),
)
COVERAGE_STATUSES = ("observed", "partial", "not-in-scope")
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD)\b|<[^>]+>", re.IGNORECASE)
EMPTY_AXES_RE = re.compile(r"^(?:none|n/?a|not assessed|not applicable)\.?$", re.IGNORECASE)


class SurfaceContractError(ValueError):
    """Raised when a quality artifact hides or omits semantic coverage state."""


def _section_body(lines: Sequence[str]) -> list[str]:
    count = sum(line.strip() == SECTION for line in lines)
    if not count:
        raise SurfaceContractError(f"missing required section `{SECTION}`")
    if count > 1:
        raise SurfaceContractError(f"surface contract repeats section `{SECTION}`")
    start = next(index for index, line in enumerate(lines) if line.strip() == SECTION)
    return [
        line.strip()
        for line in _markdown_sections.lines_until_next_section(lines[start + 1 :])
        if line.strip()
    ]


def validate_surface_contract_section(lines: Sequence[str]) -> None:
    values: dict[str, str] = {}
    for line in _section_body(lines):
        for field, prefix in FIELDS:
            if line.startswith(prefix):
                if field in values:
                    raise SurfaceContractError(f"surface contract repeats `{field}`")
                value = line[len(prefix) :].strip()
                if not value or PLACEHOLDER_RE.search(value):
                    raise SurfaceContractError(f"surface contract `{field}` must be explicit")
                values[field] = value
                break
    missing = [field for field, _ in FIELDS if field not in values]
    if missing:
        raise SurfaceContractError("surface contract missing fields: " + ", ".join(missing))

    coverage = values["semantic coverage"].replace("`", "").lower()
    status = coverage.split("—", 1)[0].strip()
    if status not in COVERAGE_STATUSES:
        allowed = ", ".join(f"`{item}`" for item in COVERAGE_STATUSES)
        raise SurfaceContractError(f"semantic coverage must start with one of {allowed}")
    if status != "observed" and EMPTY_AXES_RE.fullmatch(values["unexamined axes"]):
        raise SurfaceContractError(
            f"`unexamined axes` must name the unproven axes when coverage is `{status}`"
        )
