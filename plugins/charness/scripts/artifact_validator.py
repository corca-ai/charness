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


def validate_exact_h2_sections(
    lines: Sequence[str],
    required_sections: Sequence[str],
    *,
    optional_sections: Sequence[str] = (),
) -> None:
    headings = iter_h2_headings(lines)
    allowed = list(required_sections) + list(optional_sections)
    for heading in headings:
        if heading not in allowed:
            raise ValidationError(
                "artifact must use only the canonical sections: "
                + ", ".join(f"`{heading}`" for heading in allowed)
            )
    for required in required_sections:
        if required not in headings:
            raise ValidationError(f"missing required section `{required}`")


def validate_nonempty_sections(lines: Sequence[str], required_sections: Sequence[str]) -> None:
    for index, heading in enumerate(required_sections):
        start = find_index(lines, heading) + 1
        end = len(lines)
        if index + 1 < len(required_sections):
            end = find_index(lines, required_sections[index + 1])
        section_lines = [line.strip() for line in lines[start:end] if line.strip()]
        if not section_lines:
            raise ValidationError(f"`{heading}` must not be empty")


SIBLING_SEARCH_HEADING = "## Sibling Search"
SIBLING_DECISION_FOLLOWUP = "valid follow-up outside the slice"


def is_sibling_decision_bullet(line: str) -> bool:
    """Bullet entries are `- ...` lines that carry a `decision:` field.

    Prose paragraphs that mention the decision phrase are excluded so authors
    can quote the rule in commentary without tripping the validator.
    """
    stripped = line.lstrip()
    return stripped.startswith("- ") and "decision:" in stripped.lower()


def is_trivial_short_circuit(line: str) -> bool:
    """`n/a — trivial fix; no plausible siblings` short-circuit, dash-agnostic."""
    lowered = line.lower()
    return (
        "n/a" in lowered
        and "trivial fix" in lowered
        and "no plausible siblings" in lowered
    )


def is_valid_followup_tail(tail: str) -> bool:
    """`follow-up:` payload must name an identifier or `deferred <anchor>`.

    Bare tokens like `deferred` (without an anchor) silently re-export the
    follow-up to the next session — that is the exact failure the rule blocks.
    """
    parts = tail.split(None, 1)
    if not parts:
        return False
    if parts[0].rstrip(".,;:") == "deferred":
        return len(parts) > 1 and bool(parts[1].strip())
    return True


def line_has_valid_followup(line: str) -> bool:
    lower = line.lower()
    if "follow-up:" not in lower:
        return False
    tail = lower.split("follow-up:", 1)[1].strip()
    return is_valid_followup_tail(tail)


def validate_sibling_followups(
    lines: Sequence[str],
    *,
    boundary_headings: Sequence[str],
    source_reference: str,
) -> None:
    """Fail when a `valid follow-up outside the slice` sibling lacks a follow-up id.

    `## Sibling Search` is a list of `- <axis>: <location> | decision: ... | proof: ...`
    bullets. When `decision: valid follow-up outside the slice` appears on a
    bullet line, the same bullet (or the next continuation line) must carry a
    `follow-up: <issue-url>` or `follow-up: deferred <anchor>` identifier.

    The section is opt-in: artifacts without a `## Sibling Search` heading pass.
    `boundary_headings` are the headings that may follow the section; whichever
    appears first ends it. `source_reference` is the skill reference cited in the
    failure message. Decision matching is case-insensitive so a title-cased
    decision phrase cannot bypass the rule.
    """
    try:
        start = find_index(lines, SIBLING_SEARCH_HEADING) + 1
    except ValidationError:
        return
    end = len(lines)
    for candidate in boundary_headings:
        try:
            index = find_index(lines, candidate)
        except ValidationError:
            continue
        if index > start:
            end = min(end, index)
    section = list(lines[start:end])
    if any(is_trivial_short_circuit(line) for line in section):
        return
    for index, raw in enumerate(section):
        line = raw.rstrip()
        if not is_sibling_decision_bullet(line):
            continue
        if SIBLING_DECISION_FOLLOWUP not in line.lower():
            continue
        if line_has_valid_followup(line):
            continue
        peek = section[index + 1] if index + 1 < len(section) else ""
        if line_has_valid_followup(peek):
            continue
        offender = line.strip().lstrip("- ").strip()
        raise ValidationError(
            "`## Sibling Search` entry classified `valid follow-up outside the slice` must record a "
            "`follow-up: <issue-url>` or `follow-up: deferred <handoff-anchor>` identifier on the same "
            f"bullet (offender: `{offender[:120]}`); see {source_reference}."
        )

