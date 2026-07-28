#!/usr/bin/env python3
"""Read nose's JSON report shapes, and say when a report establishes no family set.

Split out of `nose_report_lib` (length cap): reading a versioned report is its own
concern, separate from building the query, running the process, and normalizing a
family for display. Two functions own the whole shape question — `extract_report`
pulls the fields out of whichever shape nose emitted, and `report_shape_error` says
whether that shape was understood at all — so a consumer cannot read one without the
other, and there is one home for "which key holds the families".

nose's shapes, pinned:

- `nose query <path> all --format json` emits a top-level object with `families`
  (schema_version 2 on 0.13.0, 3 on 0.13.3, 9 on 0.20.0); the no-`all` dashboard
  emits `top_candidates` instead. The removed `nose scan` emitted `families` with a
  `tool_version`, and 0.4 emitted a bare top-level array.
- The `all` query carries no `ranking` block; it carries `summary`
  (`{"families": N, "shown": M, ...}`), from which ranking is derived for the
  advisory's "showing N of M" line. Observed on nose 0.20.0, 2026-07-28.
"""

from __future__ import annotations

from typing import Any

FAMILY_KEYS = ("families", "top_candidates")


def extract_report(parsed: Any) -> tuple[list[dict[str, Any]], str, dict[str, Any], dict[str, Any]]:
    """Return `(families, tool_version, scope, ranking)` across nose's JSON shapes.

    Reading the wrong family key silently yielded zero families, under-reporting the live
    scan — which is why `report_shape_error` exists alongside this reader: entries dropped
    here (a non-dict family) are invisible in the returned list, so the shape check
    compares this result against the report's own raw entry list.
    """
    families: Any = []
    tool_version = ""
    scope: Any = {}
    ranking: Any = {}
    if isinstance(parsed, dict):
        families = parsed.get("families")
        if not isinstance(families, list):
            families = parsed.get("top_candidates")
        tool_version = str(parsed.get("tool_version") or "")
        scope = parsed.get("scope")
        ranking = parsed.get("ranking")
        if not isinstance(ranking, dict):
            summary = parsed.get("summary")
            if isinstance(summary, dict):
                ranking = {
                    "total_families": summary.get("families"),
                    "shown_families": summary.get("shown"),
                }
    elif isinstance(parsed, list):
        families = parsed
    if not isinstance(families, list):
        families = []
    if not isinstance(scope, dict):
        scope = {}
    if not isinstance(ranking, dict):
        ranking = {}
    return [family for family in families if isinstance(family, dict)], tool_version, scope, ranking


def raw_family_entries(parsed: Any) -> list[Any] | None:
    """The report's own family-entry list before `extract_report` filters it to dicts, or
    ``None`` when the payload declares no such list. `report_shape_error` compares this RAW
    count against the extracted count, so an entry the reader could not read is observable
    from the report itself rather than from a self-declared total."""
    if isinstance(parsed, list):
        return parsed
    if not isinstance(parsed, dict):
        return None
    for key in FAMILY_KEYS:
        entries = parsed.get(key)
        if isinstance(entries, list):
            return entries
    return None


def report_shape_error(parsed: Any, families: list[dict[str, Any]], ranking: dict[str, Any]) -> str | None:
    """Why a parsed nose report does not ESTABLISH a family set, else ``None``.

    `run_nose`'s zero-family branch used to mean two different things: nose scanned the
    scope and found nothing, and the reader did not understand the report it was handed
    (a renamed/future family key, unreadable entries, a non-report payload, or no output
    at all). Both rendered `clean` — a verdict over a scope the reader never established
    (triage sweep S34). A clean scan is only a report whose own family list the reader read
    in full; every other shape degrades the whole scan to `error`, which consumers turn
    into advisory rather than a false block (FD8).

    Two signals, and neither is sufficient alone. The RAW entry count catches entries the
    reader dropped even when the payload declares no total — no nose version is known to
    emit non-dict family entries, so that arm is DEFENSIVE against a future shape rather
    than a reproduced producer behavior. The declared total (`summary.families` on the real
    `all` query, observed 0.20.0) catches the shape that IS producer-grounded: a family key
    the reader could not find while the report itself counts families.
    """
    entries = raw_family_entries(parsed)
    if entries is None:
        if not isinstance(parsed, dict):
            return "nose report is neither a family array nor a report object"
        if not parsed:
            return "nose emitted no report payload; the scan produced nothing to read"
        keys = ", ".join(sorted(str(key) for key in parsed)[:8])
        return (
            f"nose report declares no `families`/`top_candidates` list (keys: {keys}); the reader "
            "cannot establish the family set, so this is a scan error rather than a clean scan"
        )
    unreadable = len(entries) - len(families)
    if unreadable > 0:
        return (
            f"{unreadable} of {len(entries)} nose family entry(ies) are not readable family objects; "
            "the report is in an unrecognized shape, so the family set is unestablished"
        )
    declared = ranking.get("total_families")
    if isinstance(declared, int) and not isinstance(declared, bool) and declared > 0 and not families:
        return (
            f"nose report declares {declared} family(ies) but the reader extracted 0; the family "
            "entries are in an unrecognized shape"
        )
    return None
