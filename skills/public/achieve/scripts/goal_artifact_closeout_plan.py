"""Typed reader for a goal artifact's ``Closeout Binding Plan``.

The plan is an authoring contract, not closeout proof.  This module owns the
section name, field grammar, fence-aware section selection, and the small
structured report consumed by both the pursue gate and the broad goal-shape
validator.  Keeping the reader here prevents the two proof surfaces from
silently accepting different plans.
"""
from __future__ import annotations

import re
from typing import Any, Callable, NamedTuple

SECTION = "Closeout Binding Plan"
CLOSEOUT_PLAN_SECTION = SECTION
CLOSEOUT_PLAN_FIELDS = (
    "Reviewed inputs:",
    "Frozen target:",
    "Fresh-eye:",
    "Verification lock:",
    "Complete flip:",
)

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_DECORATION = r"[`*_~]*"
_SUBSTANTIVE = re.compile(r"[\s\W_]+", re.UNICODE)


def _mask_fences(text: str) -> str:
    """Mask fenced markdown without treating an unclosed fence as readable."""
    lines = text.splitlines(keepends=True)
    masked: list[str] = []
    marker: str | None = None
    width = 0
    for line in lines:
        stripped = line.lstrip()
        fence = re.match(r"(`{3,}|~{3,})(?![`~])", stripped)
        if fence:
            token = fence.group(1)
            char = token[0]
            if marker is None:
                marker, width = char, len(token)
            elif char == marker and len(token) >= width:
                marker, width = None, 0
            masked.append("\n" if line.endswith("\n") else "")
        elif marker is None:
            masked.append(line)
        else:
            masked.append("\n" if line.endswith("\n") else "")
    return "".join(masked)


def _fences_balanced(text: str) -> bool:
    lines = text.splitlines()
    marker: str | None = None
    width = 0
    for line in lines:
        match = re.match(r"^[ \t]*(`{3,}|~{3,})(?![`~])", line)
        if match is None:
            continue
        token = match.group(1)
        if marker is None:
            marker, width = token[0], len(token)
        elif token[0] == marker and len(token) >= width:
            marker, width = None, 0
    return marker is None


def _has_substance(value: str) -> bool:
    # Punctuation-only placeholders (`—`, `**`, or a decorated empty value) do
    # not satisfy a field.  Keep this structural: a real value may contain any
    # punctuation the goal author needs.
    return bool(_SUBSTANTIVE.sub("", value).strip())


class CloseoutPlan(NamedTuple):
    """One fence-aware closeout-plan observation."""

    present: bool
    duplicate: bool
    missing_fields: tuple[str, ...]
    values: tuple[tuple[str, str], ...]
    fences_balanced: bool

    @property
    def complete(self) -> bool:
        return self.present and not self.duplicate and not self.missing_fields and self.fences_balanced

    @property
    def ok(self) -> bool:
        """Alias used by validators when a plan heading is present."""
        return self.complete

    def as_dict(self) -> dict[str, Any]:
        return {
            "present": self.present,
            "duplicate": self.duplicate,
            "missing_fields": list(self.missing_fields),
            "values": dict(self.values),
            "fences_balanced": self.fences_balanced,
            "complete": self.complete,
            "ok": self.ok,
        }

    def validation_issues(self) -> list[str]:
        """Return the broad-validator issues carried by this typed observation."""
        issues: list[str] = []
        if self.duplicate:
            issues.append("duplicate sections: Closeout Binding Plan")
        if self.missing_fields:
            issues.append("incomplete Closeout Binding Plan: " + ", ".join(self.missing_fields))
        return issues


def parse_closeout_plan(
    text: str,
    *,
    mask_fences: Callable[[str], str] | None = None,
    fences_balanced: Callable[[str], bool] | None = None,
) -> CloseoutPlan:
    """Read one plan from ``text`` and return its typed shape observation.

    Fenced headings are not plans.  An unbalanced fence therefore makes the
    heading/field read unestablished and cannot accidentally turn a quoted
    template into a complete plan.  Callers may inject the repository markdown
    helpers; defaults keep this producer independently importable in the
    exported plugin and in direct unit tests.
    """
    mask = mask_fences or _mask_fences
    balanced_fn = fences_balanced or _fences_balanced
    balanced = bool(balanced_fn(text))
    masked = mask(text)
    headings = [match for match in _H2.finditer(masked) if match.group(1).strip() == SECTION]
    duplicate = len(headings) > 1
    values: dict[str, str] = {}
    missing: list[str] = []
    if len(headings) == 1 and balanced:
        all_headings = list(_H2.finditer(masked))
        heading = headings[0]
        # Match objects from separate ``finditer`` calls are not equal even
        # when they cover the same span; bind the heading by its source offset.
        position = next(i for i, candidate in enumerate(all_headings) if candidate.start() == heading.start())
        end = all_headings[position + 1].start() if position + 1 < len(all_headings) else len(masked)
        body = masked[heading.end() : end]
        for field in CLOSEOUT_PLAN_FIELDS:
            pattern = re.compile(
                rf"^[ \t>*-]*{_DECORATION}{re.escape(field)}{_DECORATION}[ \t]+(.+?)\s*$",
                re.MULTILINE,
            )
            match = pattern.search(body)
            if match is None or not _has_substance(match.group(1)):
                missing.append(field)
            else:
                values[field] = match.group(1).strip()
    elif len(headings) == 1:
        # Preserve the complete missing set when the document cannot establish
        # which body is real; ``fences_balanced`` is the independent refusal.
        missing.extend(CLOSEOUT_PLAN_FIELDS)
    return CloseoutPlan(
        present=bool(headings),
        duplicate=duplicate,
        missing_fields=tuple(missing),
        values=tuple(values.items()),
        fences_balanced=balanced,
    )


def check_closeout_plan(text: str, **kwargs: Any) -> dict[str, Any]:
    """Compatibility/reporting form for callers that consume mappings."""
    return parse_closeout_plan(text, **kwargs).as_dict()


def render_reason(plan: CloseoutPlan) -> str:
    """Render only the plan-owned refusal clauses used by pursue readiness."""
    clauses: list[str] = []
    if not plan.fences_balanced and plan.present:
        clauses.append(
            "unreadable: Closeout Binding Plan is inside an unclosed code fence; close the fence before `/goal`"
        )
    if plan.missing_fields:
        clauses.append(
            "incomplete: Closeout Binding Plan field(s) absent or empty ("
            + ", ".join(plan.missing_fields)
            + ") -- fill the minimum plan fields before `/goal`"
        )
    if plan.duplicate:
        clauses.append(
            "incomplete: Closeout Binding Plan appears more than once -- keep one unambiguous plan before `/goal`"
        )
    return "; ".join(clauses)
