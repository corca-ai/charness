#!/usr/bin/env python3
"""Presence/enum **form** floor for retro/Auto-Retro dispositions (#329).

The achieve contract declares that every surfaced improvement resolves to
``applied: <committed change>`` / ``issue #N`` / ``none — <reason>`` and that
prose-only ``memory`` is invalid. The pre-existing achieve gate is
presence/binding-only ("a review ran") and a standalone session retro had no
disposition review at all, so an invalid ``Disposition: memory`` could ship and
only a human reading it would catch it.

This module is the **shared single source** of the disposition-form grammar so
neither consumer forks disposition parsing (goal Boundary). It is consumed by:

- the achieve closeout gate (``goal_artifact_disposition.apply_disposition_rungs``
  loads it via parent-walk; scoped to ``## Auto-Retro``), and
- the session-retro validator (``scripts/validate_retro_artifact.py`` imports it
  same-root; scoped to ``## Next Improvements``).

It ships to ``plugins/charness/scripts/`` exactly like ``runtime_bootstrap`` and
``check_prescribed_skill_executed_lib``, so the parent-walk resolves in the
installed export too.

Cardinal rule (verbatim from the achieve guardrail and #329): it judges only the
disposition **form/enum value**, never whether the generalization is good — a
present-but-vague ``applied: tweak`` passes. Mirrors
``skills/public/issue/scripts/validate_proposal_fields.py``'s ``Destination``
enum, not a content classifier.

Masking boundary: like the sibling disposition/closeout gates, only fenced code
blocks are masked. An inline-backtick disposition *example* inside the scoped
section is judged like real content (fence it to exempt it); this keeps the
masking convention identical to the existing gates rather than inventing a new
inline-span parser.
"""
from __future__ import annotations

import re
from datetime import date

# Enforce-from-date. The floor lands 2026-06-07; #330 (a frozen ``complete``
# goal Created 2026-06-07 that carries ``Disposition: memory ->``/``fix (folded)``
# — the motivating dogfood instance), this #329 goal, and the triggering retros
# were all Created/Dated 2026-06-07. Enforcement begins the NEXT day so those
# frozen artifacts are grandfathered (the Goodhart Non-Goal: the original author
# never had this floor). Mirrors ``validate_inventory_consumption.ENFORCED_FROM_DATE``.
# Clone-safe: an in-file constant, not mtime.
DISPOSITION_FORM_RULE_DATE = date(2026, 6, 8)

VALID_FORM_SUMMARY = "`applied: <change>` / `issue #N` / `none — <reason>`"

# Markers whose value carries a disposition. ``Retro dispositions:`` (aggregate,
# achieve per-goal) is tried before the singular ``Disposition:`` so the longer
# label wins at the same position. Both require a trailing colon so prose like
# "the disposition review" (no colon) is never read as a marker.
_MARKER = re.compile(
    r"(?i)\b(retro[ \t]+dispositions?|dispositions?)[ \t]*:[ \t]*(?P<value>[^\n]*)"
)

# Leading markdown bullet/emphasis/quote markers stripped before judging a value,
# mirroring ``validate_proposal_fields._field_value`` tolerance. ``#`` is NOT in
# the class (unlike the label-line idiom): a leading ``#`` here is a meaningful
# issue reference (``#328``), not a heading marker, and must survive.
_MARKDOWN_LEAD = re.compile(r"^[ \t\-\*>]+")

# Untouched scaffold placeholders are NOT a form violation — block-the-blank
# (disposition rung 1a) owns the unfilled-Auto-Retro case. Skip them here.
_PLACEHOLDER = re.compile(r"^(?:TODO|TBD|FIXME)\b|^<[^>\n]*>", re.IGNORECASE)

# The three valid forms, anchored to the leading token (enum-style).
_APPLIED = re.compile(r"^applied\b", re.IGNORECASE)
_ISSUE_LEAD = re.compile(r"^(?:issues?\b|#\d)", re.IGNORECASE)
_ISSUE_NUM = re.compile(r"#\d+")
# ``none`` then a dash/colon separator then a non-empty reason (``none — <reason>``).
# A plain hyphen must carry surrounding whitespace so a compound word like
# ``none-actionable`` is NOT read as ``none`` + ``-`` separator + reason; an
# em/en-dash or colon (not used inside compound words) needs no leading space.
_NONE = re.compile(r"^none\b[ \t]*(?:[—–:]|[ \t]-)[ \t]*\S", re.IGNORECASE)

# Recurrence-lineage marker for ``issue``-routed dispositions: one of
# ``recurs``/``recurrence``/``lineage``/``novel`` then a colon then non-empty
# content. Presence/enum only (like the form floor and ``Destination`` enum) —
# it proves the author committed to a falsifiable claim *type*, never whether the
# claim is true. ``novel:`` requires the colon, so prose like "a novel approach"
# (no colon) does not satisfy it.
RECURRENCE_LINEAGE_SUMMARY = (
    "a recurrence-lineage marker (`recurs:`/`recurrence:`/`lineage:`/`novel:`) with non-empty content"
)
_RECURRENCE_LINEAGE = re.compile(r"(?i)\b(?:recurs|recurrence|lineage|novel)\b[ \t]*:[ \t]*\S")


def _clean(value: str) -> str:
    """Strip leading markdown markers and surrounding emphasis from a value."""
    cleaned = _MARKDOWN_LEAD.sub("", value.strip())
    return cleaned.strip().strip("*").strip()


def evaluate_disposition_form(value: str) -> dict:
    """Judge one disposition value's form (never its substance).

    Returns ``{"ok", "kind", "value", "reason"}`` where ``kind`` is one of
    ``applied`` / ``issue`` / ``none`` (valid), ``placeholder`` (unfilled
    scaffold; ok, not judged), or ``invalid`` (the rejected prose-only/``memory``
    class). ``ok`` is True for the valid forms and placeholders.
    """
    cleaned = _clean(value)
    if not cleaned:
        return {"ok": False, "kind": "invalid", "value": value.strip(), "reason": "empty disposition value"}
    if _PLACEHOLDER.match(cleaned):
        return {"ok": True, "kind": "placeholder", "value": cleaned, "reason": "unfilled scaffold placeholder; not judged"}
    if _APPLIED.match(cleaned):
        return {"ok": True, "kind": "applied", "value": cleaned, "reason": ""}
    if _ISSUE_LEAD.match(cleaned) and _ISSUE_NUM.search(cleaned):
        return {"ok": True, "kind": "issue", "value": cleaned, "reason": ""}
    if _NONE.match(cleaned):
        return {"ok": True, "kind": "none", "value": cleaned, "reason": ""}
    return {
        "ok": False,
        "kind": "invalid",
        "value": cleaned,
        "reason": f"not one of {VALID_FORM_SUMMARY} (bare `memory`/prose-only is rejected)",
    }


def has_recurrence_lineage(value: str) -> bool:
    """Presence/enum-only: does this disposition value carry a recurrence-lineage
    marker (``recurs``/``recurrence``/``lineage``/``novel`` + colon + non-empty)?

    Never judges the marker's *correctness* — a false ``novel:`` passes this floor
    and is the fresh-eye disposition review's (rung 2) job to falsify. Mirrors the
    form floor's presence/enum discipline; it must never become a content
    classifier (the achieve guardrail). Consumed only by the achieve recurrence-
    lineage rung; the session-retro validator does not call it, so retro behavior
    is unchanged.
    """
    return bool(_RECURRENCE_LINEAGE.search(value))


def _mask_fences(text: str) -> str:
    """Blank fenced code-block regions to spaces (length/newlines preserved).

    A self-contained mirror of the sibling gates' ``_mask_fences`` so this module
    keeps no cross-module import; a fenced disposition *example* must not be read
    as a real disposition line.
    """
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    if in_fence:
        return text
    return "".join(masked)


def scan_dispositions(section_text: str) -> list[dict]:
    """Find every disposition-marker line in ``section_text`` and judge its form.

    ``section_text`` is the already-section-scoped body (the caller owns section
    selection). Fences are masked here so a fenced example line is inert. Returns
    ``[{"marker", "value", "verdict"}]`` in source order.
    """
    masked = _mask_fences(section_text)
    results: list[dict] = []
    for match in _MARKER.finditer(masked):
        value = match.group("value").strip()
        results.append(
            {"marker": match.group(1).strip(), "value": value, "verdict": evaluate_disposition_form(value)}
        )
    return results


def invalid_dispositions(section_text: str) -> list[dict]:
    """Return only the scanned entries whose form verdict is not ``ok``."""
    return [entry for entry in scan_dispositions(section_text) if not entry["verdict"]["ok"]]


def is_form_enforced(observed: date | None) -> bool:
    """Whether the form floor fires for an artifact dated ``observed``.

    Fail-CLOSED: an undatable artifact (``None``) is treated as in-scope, so a
    file cannot dodge the floor by dropping/corrupting its date line. Mirrors
    ``disposition_gate_applies``.
    """
    if observed is None:
        return True
    return observed >= DISPOSITION_FORM_RULE_DATE
