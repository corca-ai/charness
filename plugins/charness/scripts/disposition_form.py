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

VALID_FORM_SUMMARY = (
    "`applied: <change>` / `issue #N` / `none — <reason>` / "
    "`accepted-risk: <reason>` / `out-of-scope: <reason>`"
)

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

# The #339 additive arms: `accepted-risk: <reason>` / `out-of-scope: <reason>`.
# Same separator discipline as `_NONE` (colon/em–en-dash, or a whitespace-bearing
# plain hyphen) so a compound word is never split, then a non-empty reason. The
# `\b` after the literal token rejects a glued compound (`accepted-risky`,
# `out-of-scoped`). These extend the shared disposition grammar (never fork it);
# `evaluate_destination_form` explicitly excludes them so the #337 structural-
# follow-up destination vocabulary is byte-for-byte behavior-preserved.
_ACCEPTED_RISK = re.compile(r"^accepted-risk\b[ \t]*(?:[—–:]|[ \t]-)[ \t]*\S", re.IGNORECASE)
_OUT_OF_SCOPE = re.compile(r"^out-of-scope\b[ \t]*(?:[—–:]|[ \t]-)[ \t]*\S", re.IGNORECASE)

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

# Structural-follow-up **destination** floor (#337). When a waste-retro names a
# *transferable* waste item (a `## Sibling Search` trigger), each item's
# disposition must resolve to one explicit structural-follow-up destination, so
# "recorded in recent-lessons" can no longer be mistaken for a structural fix.
# Its own enforce-from date lands the day after the floor (mirrors rung 1c/1d):
# every artifact dated on/before the landing day is grandfathered. Clone-safe:
# an in-file constant, not mtime.
STRUCTURAL_FOLLOWUP_RULE_DATE = date(2026, 6, 9)

# Residual/disposition LEDGER floor (#339). A `## Residual Ledger` row that names a
# residual risk / non-claim / proof gap must resolve to one concrete disposition,
# so a prose-only `defer` / `recorded in retro` / `future work` no longer satisfies
# closeout. Lands 2026-06-09; enforcement begins the NEXT day so every artifact
# Created on/before the landing day is grandfathered (the established
# `DISPOSITION_FORM_RULE_DATE` / `STRUCTURAL_FOLLOWUP_RULE_DATE` precedent — the
# broad gate stays green). The two new disposition arms above are additive/
# permissive (accepting more forms can never break an existing artifact), so only
# this presence/form FLOOR carries an enforce-from date. Clone-safe: in-file
# content, not mtime.
RESIDUAL_LEDGER_RULE_DATE = date(2026, 6, 10)

# The four destination forms, a superset of the disposition forms above plus
# `repo-local guard: <path>` (a consuming-repo guard). Presence/enum only — the
# fresh-eye disposition review (rung 2) judges whether the chosen destination is
# substantively right, exactly as it falsifies a `novel:` claim.
DESTINATION_FORM_SUMMARY = (
    "`applied: <gate/hook/validator/test/contract change>` / "
    "`issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`"
)
# `repo-local guard: <path>` then a colon/dash separator then a non-empty path.
# Mirrors `_NONE`'s separator handling so a compound word is not split.
_REPO_LOCAL_GUARD = re.compile(
    r"^repo-local[ \t]+guard\b[ \t]*(?:[—–:]|[ \t]-)[ \t]*\S", re.IGNORECASE
)
# The destination-line marker. `follow[ \t-]?ups?` matches `follow-up`/`followup`/
# `follow up`/`follow-ups`; the trailing colon is required so prose like "a
# structural follow-up was filed" (no colon) is never read as a marker.
_DESTINATION_MARKER = re.compile(
    r"(?i)\bstructural[ \t]+follow[ \t-]?ups?[ \t]*:[ \t]*(?P<value>[^\n]*)"
)
# A `## Sibling Search` section names transferable waste when it carries a real
# decision bullet (`- … | decision: …`); the `n/a — trivial fix; no plausible
# siblings` short-circuit has no `decision:` and is correctly excluded.
_SIBLING_HEADING = re.compile(r"(?im)^(#{2,6})[ \t]+Sibling[ \t]+Search\b[^\n]*$")
_DECISION_BULLET = re.compile(r"(?im)^[ \t]*(?:[-*+]|\d+[.)])[ \t].*\bdecision[ \t]*:")


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
    if _ACCEPTED_RISK.match(cleaned):
        return {"ok": True, "kind": "accepted-risk", "value": cleaned, "reason": ""}
    if _OUT_OF_SCOPE.match(cleaned):
        return {"ok": True, "kind": "out-of-scope", "value": cleaned, "reason": ""}
    return {
        "ok": False,
        "kind": "invalid",
        "value": cleaned,
        "reason": f"not one of {VALID_FORM_SUMMARY} (bare `memory`/prose-only is rejected)",
    }


def evaluate_destination_form(value: str) -> dict:
    """Judge one structural-follow-up **destination** value's form (#337).

    The four valid forms are the three disposition forms (``applied:`` /
    ``issue #N`` / ``none — <reason>``) plus ``repo-local guard: <path>``. Like
    ``evaluate_disposition_form`` it is presence/enum only — a present-but-vague
    ``applied: tweak`` passes; the substance is the disposition review's call.
    Returns the same ``{"ok", "kind", "value", "reason"}`` shape; ``kind`` adds
    ``repo-local-guard`` to the form vocabulary.
    """
    cleaned = _clean(value)
    if not cleaned:
        return {"ok": False, "kind": "invalid", "value": value.strip(), "reason": "empty destination value"}
    if _PLACEHOLDER.match(cleaned):
        return {"ok": True, "kind": "placeholder", "value": cleaned, "reason": "unfilled scaffold placeholder; not judged"}
    if _REPO_LOCAL_GUARD.match(cleaned):
        return {"ok": True, "kind": "repo-local-guard", "value": cleaned, "reason": ""}
    base = evaluate_disposition_form(value)
    # The #339 `accepted-risk:`/`out-of-scope:` arms are residual-ledger forms, NOT
    # structural-follow-up destinations; excluding them keeps `evaluate_destination_form`
    # byte-for-byte behavior-preserved for every input (the #337 Non-Goal).
    if base["ok"] and base["kind"] not in ("accepted-risk", "out-of-scope"):
        return base
    return {
        "ok": False,
        "kind": "invalid",
        "value": cleaned,
        "reason": f"not one of {DESTINATION_FORM_SUMMARY} (a bare memory/prose-only destination is rejected)",
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


def names_transferable_waste(retro_text: str) -> bool:
    """True when the cited retro names a *transferable* waste item — a
    ``## Sibling Search`` section carrying ≥1 real decision bullet (#337).

    Structure/presence only: the section is the waste-sibling-scan marker the
    retro contract adds *only* when a transferable waste pattern is named, so its
    presence-with-a-decision-bullet is the trigger. The ``n/a — trivial fix; no
    plausible siblings`` short-circuit carries no ``decision:`` and is excluded,
    so narrowly-local waste does not over-fire the destination floor. Fences are
    masked so a fenced example section is inert.
    """
    masked = _mask_fences(retro_text)
    head = _SIBLING_HEADING.search(masked)
    if head is None:
        return False
    level = len(head.group(1))
    body_start = masked.find("\n", head.end())
    if body_start == -1:
        return False
    nxt = re.compile(rf"(?m)^#{{1,{level}}}[ \t]+\S").search(masked, body_start + 1)
    body = masked[body_start + 1 : nxt.start() if nxt else len(masked)]
    return bool(_DECISION_BULLET.search(body))


def scan_destinations(section_text: str) -> list[dict]:
    """Find every ``Structural follow-up:`` destination line and judge its form.

    ``section_text`` is the already-section-scoped body (the caller owns section
    selection, mirroring ``scan_dispositions``). Returns
    ``[{"marker", "value", "verdict"}]`` in source order; fences are masked.
    """
    masked = _mask_fences(section_text)
    results: list[dict] = []
    for match in _DESTINATION_MARKER.finditer(masked):
        value = match.group("value").strip()
        results.append(
            {"marker": "Structural follow-up", "value": value, "verdict": evaluate_destination_form(value)}
        )
    return results


def evaluate_structural_followup(section_text: str) -> dict:
    """Verdict for the structural-follow-up destination floor over an Auto-Retro
    body. Presence/form-enum only (never a content classifier — the #337
    guardrail). Returns ``{"problem": None|"invalid"|"missing", "reason"?, ...}``:

    - ``"invalid"`` — at least one ``Structural follow-up:`` line uses a form that
      is not one of the four destinations.
    - ``"missing"`` — no valid ``Structural follow-up:`` destination line is
      present (the caller fires this only when transferable waste is named).
    - ``None`` — at least one valid destination line and no invalid form.
    """
    destinations = scan_destinations(section_text)
    invalid = [d for d in destinations if not d["verdict"]["ok"]]
    valid = [d for d in destinations if d["verdict"]["ok"] and d["verdict"]["kind"] != "placeholder"]
    if invalid:
        return {
            "problem": "invalid",
            "invalid": [{"value": d["value"]} for d in invalid],
            "reason": (
                "one or more `Structural follow-up:` destination lines use an invalid form; each must be "
                f"{DESTINATION_FORM_SUMMARY}"
            ),
        }
    if not valid:
        return {
            "problem": "missing",
            "reason": (
                "the cited retro names a transferable waste item (a `## Sibling Search` trigger) but "
                "`## Auto-Retro` records no `Structural follow-up:` destination; classify each transferable "
                f"waste item's structural follow-up as {DESTINATION_FORM_SUMMARY} so a bare "
                "'recorded in recent-lessons' cannot be mistaken for a structural disposition"
            ),
        }
    return {"problem": None}


# ---------------------------------------------------------------------------
# Residual/disposition LEDGER floor (#339).
#
# Generalizes the #337 destination floor to a full residual ledger: every
# closeout residual risk / non-claim / proof gap listed in a `## Residual Ledger`
# table must resolve to one concrete disposition. The valid residual forms are
# `applied:` / `issue #N` / `accepted-risk:` / `out-of-scope:` — a bare `none`
# is NOT a residual disposition (a named residual resolves affirmatively, never
# to "nothing"), and a prose-only `defer` / `recorded in retro` / `future work`
# is rejected. Presence/form-enum only (the fixed #337/#329/#253 doctrine): a
# vague-but-valid `accepted-risk: <reason>` passes; the reviewer/human judges
# whether the residual was honestly dispositioned and whether any residual was
# omitted. The floor never REQUIRES a ledger — an absent or empty ledger does not
# fire (no over-fire on a no-residual closeout).
# ---------------------------------------------------------------------------

RESIDUAL_DISPOSITION_FORM_SUMMARY = (
    "`applied: <artifact/change>` / `issue #N` / "
    "`accepted-risk: <reason>` / `out-of-scope: <reason>`"
)

# A markdown table data row (`| … | … |`). The separator row (`| --- | :-: |`)
# carries only dashes/colons/pipes/space and is filtered out before judging.
_LEDGER_TABLE_ROW = re.compile(r"^[ \t]*\|(.+)\|[ \t]*$")
_LEDGER_SEPARATOR = re.compile(r"^[ \t]*\|[\s:|-]+\|[ \t]*$")
_RESIDUAL_LEDGER_HEADING = re.compile(r"(?im)^(#{2,6})[ \t]+Residual[ \t]+Ledgers?\b[^\n]*$")


def evaluate_residual_disposition_form(value: str) -> dict:
    """Judge one residual-ledger row disposition's form (never its substance).

    Valid forms are ``applied`` / ``issue`` / ``accepted-risk`` / ``out-of-scope``
    (and ``placeholder``, an unfilled scaffold cell). A bare ``none — <reason>``
    is intentionally INVALID here: a named residual resolves to a concrete
    disposition, not to "nothing". Layers on ``evaluate_disposition_form`` (the
    single shared grammar) rather than re-deriving the form checks. Presence/enum
    only — a vague-but-valid ``accepted-risk: x`` passes.
    """
    base = evaluate_disposition_form(value)
    if base["kind"] in ("applied", "issue", "accepted-risk", "out-of-scope", "placeholder"):
        return base
    return {
        "ok": False,
        "kind": "invalid",
        "value": base["value"],
        "reason": (
            f"not one of {RESIDUAL_DISPOSITION_FORM_SUMMARY} (a prose-only "
            "`defer`/`recorded in retro`/`future work`, or a bare `none`, residual is rejected)"
        ),
    }


def _split_table_row(line: str) -> list[str]:
    """Split a `| a | b | c |` markdown table row into stripped cell values."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _residual_ledger_body(text: str) -> str | None:
    """The body of the ``## Residual Ledger`` section (heading line excluded),
    fences masked; ``None`` when the section is absent. Mirrors the heading scan
    in ``names_transferable_waste`` so a fenced example section stays inert."""
    masked = _mask_fences(text)
    head = _RESIDUAL_LEDGER_HEADING.search(masked)
    if head is None:
        return None
    level = len(head.group(1))
    body_start = masked.find("\n", head.end())
    if body_start == -1:
        return ""
    nxt = re.compile(rf"(?m)^#{{1,{level}}}[ \t]+\S").search(masked, body_start + 1)
    return masked[body_start + 1 : nxt.start() if nxt else len(masked)]


def _judge_ledger_table(table: list[str], results: list[dict]) -> None:
    """Judge one contiguous markdown table's residual rows, appending to ``results``.

    A table is judged only when its header row names a ``Disposition`` column, found
    by header NAME (any position). A leading non-disposition table in the same
    section is passed over without masking a following residual table — closing the
    multi-table under-fire bypass (a prose-only row in a second table cannot slip
    through behind a first non-disposition table).
    """
    rows = [line for line in table if not _LEDGER_SEPARATOR.match(line)]
    if not rows:
        return
    header = _split_table_row(rows[0])
    disp_idx = next(
        (i for i, name in enumerate(header) if re.search(r"disposition", name, re.IGNORECASE)),
        None,
    )
    if disp_idx is None:
        return
    for row in rows[1:]:
        cells = _split_table_row(row)
        if disp_idx < len(cells):
            value = cells[disp_idx]
            results.append(
                {"row": row.strip(), "value": value, "verdict": evaluate_residual_disposition_form(value)}
            )


def scan_residual_ledger(section_text: str) -> list[dict]:
    """Judge each ``## Residual Ledger`` DATA row's disposition cell form.

    Tables are grouped by contiguity (a non-table line breaks a group) and each is
    judged independently by its own header, so a leading non-disposition table
    cannot blind a following residual table. Returns ``[{"row", "value",
    "verdict"}]`` in source order; ``[]`` when no table names a ``Disposition``
    column (no over-fire on an empty or malformed ledger). Fences are masked so a
    fenced example table is inert.
    """
    masked = _mask_fences(section_text)
    results: list[dict] = []
    table: list[str] = []
    for line in masked.splitlines():
        if _LEDGER_TABLE_ROW.match(line):
            table.append(line)
            continue
        _judge_ledger_table(table, results)
        table = []
    _judge_ledger_table(table, results)
    return results


def evaluate_residual_ledger(section_text: str) -> dict:
    """Verdict for the residual-ledger floor over a ``## Residual Ledger`` body.

    Presence/form-enum only (never a content classifier). Returns
    ``{"problem": None|"invalid", "invalid"?, "reason"?}``. There is no
    ``"missing"`` state: an absent or empty ledger never fires — a no-residual
    closeout is not forced to add a row (no over-fire). It fires only when a
    present row leaves the residual as a prose-only / bare-``none`` disposition.
    """
    rows = scan_residual_ledger(section_text)
    invalid = [r for r in rows if not r["verdict"]["ok"]]
    if invalid:
        return {
            "problem": "invalid",
            "invalid": [{"value": r["value"], "row": r["row"]} for r in invalid],
            "reason": (
                "one or more `## Residual Ledger` rows leave the residual/non-claim/proof-gap as a "
                f"prose-only or bare-`none` disposition; each must be {RESIDUAL_DISPOSITION_FORM_SUMMARY}"
            ),
        }
    return {"problem": None}


def is_residual_ledger_enforced(observed: date | None) -> bool:
    """Whether the residual-ledger floor fires for an artifact dated ``observed``.

    Fail-CLOSED: an undatable artifact (``None``) is in-scope, mirroring
    ``is_form_enforced`` / ``disposition_gate_applies`` so a file cannot dodge the
    floor by dropping its date line."""
    if observed is None:
        return True
    return observed >= RESIDUAL_LEDGER_RULE_DATE


def residual_ledger_report(text: str, created: date | None) -> dict:
    """Full residual-ledger floor verdict over a goal body (achieve rung 1f).

    Bundles the grandfather-by-date gate, the ``## Residual Ledger`` section scope,
    and the per-row form judgment so the (at-cap) achieve wiring stays a few lines.
    Returns ``{"scope": {...}, "problem": None|"invalid", "invalid"?, "reason"?}``.
    """
    enforced = is_residual_ledger_enforced(created)
    scope = {
        "enforced": enforced,
        "created": created.isoformat() if created else None,
        "rule_date": RESIDUAL_LEDGER_RULE_DATE.isoformat(),
    }
    if not enforced:
        return {"scope": scope, "problem": None}
    body = _residual_ledger_body(text)
    if body is None:
        return {"scope": scope, "problem": None}
    return {"scope": scope, **evaluate_residual_ledger(body)}
