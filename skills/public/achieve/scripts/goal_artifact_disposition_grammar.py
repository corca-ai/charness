"""Goal-artifact markdown grammar + disposition-scope primitives.

The parse substrate the deterministic disposition rungs build verdicts on, split
out of ``goal_artifact_disposition.py`` so neither file approaches the single-file
line gate and the "what the rungs parse" concern reads as one cohesive unit
separate from "what the rungs decide". A pure leaf — it mutates no report and
imports no sibling — so importing it standalone never pulls in the rung logic.

Owns:

- the markdown grammar (``_mask_fences`` fenced-region blanking, ``_section_body``
  same-or-higher-level section scoping, ``goal_created_date`` Created-date parse);
- the disposition-scope predicate (``disposition_gate_applies``, grandfather-by-
  ``Created``-date, fail-CLOSED on an undatable goal);
- the Auto-Retro content probes the block-the-blank rung reuses
  (``auto_retro_is_blank``, ``retro_lists_improvements``, ``find_disposition_optout``)
  and the bound-retro path resolver (``_bound_retro_path``).
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Both rungs fire only for goals Created on or after the disposition rule's
# landing date (commit 73d2d34, 2026-05-30, inclusive). A goal shaped before the
# rule existed had no chance to plan its Auto-Retro/review around it, so
# Created-keying grandfathers exactly those in-flight goals; completion-keying
# would punish them. Clone-safe: the date is in-file content, not mtime.
DISPOSITION_RULE_DATE = date(2026, 5, 30)

# The Auto-Retro opt-out: a deliberate "no improvement needs active disposition"
# assertion, recorded visibly (the Engelbart "say why if you depart" valve, not a
# silent skip). A min-length floor mirrors the skip discipline so it cannot be a
# one-word bypass; rung 2 can falsify a false "none".
MIN_OPTOUT_REASON = 30

_DISPOSITION_OPTOUT = re.compile(
    r"^[\s>*-]*Retro dispositions\s*:\s*none\b[ \t]*[—–:-]+[ \t]*(\S.*?)[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)
_LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+\S")

# The goal-artifact template seeds a visible ``Retro dispositions: TODO — …``
# placeholder under ``## Auto-Retro`` so an active run sees the disposition
# obligation from the start. An *untouched* placeholder line must still read as
# blank-equivalent, else seeding it would silently disable rung 1a
# (block-the-blank) for any goal that fills the disposition-review line but never
# replaces the TODO. The line is treated as content only once the ``TODO`` is
# replaced by a real disposition (``Retro dispositions: none — …`` opt-out or an
# ``applied:``/``issue …`` per-improvement record).
_DISPOSITION_PLACEHOLDER = re.compile(
    r"^[\s>*-]*Retro dispositions\s*:\s*(?:TODO|TBD|<[^>]*>|FIXME)\b[^\n]*$",
    re.MULTILINE | re.IGNORECASE,
)


_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_floor_grammar import is_floor_in_scope, parse_created_date  # noqa: E402
from goal_artifact_floor_grammar import section_body as _section_body  # noqa: E402
from goal_artifact_markdown import mask_fences as _mask_fences  # noqa: E402

# ``goal_created_date`` is the shared permissive Created-parse; kept as a named
# re-export so importers/tests that reference it keep working post-extraction.
goal_created_date = parse_created_date


def disposition_gate_applies(text: str) -> bool:
    """Whether the disposition rungs fire for this goal (grandfather-by-
    ``Created``-date). Fail-CLOSED: a missing/malformed ``Created:`` is treated
    as in-scope, so a goal cannot dodge both rungs by corrupting one line."""
    return is_floor_in_scope(goal_created_date(text), DISPOSITION_RULE_DATE)


def auto_retro_is_blank(text: str) -> bool:
    """True when the goal's ``## Auto-Retro`` section is absent, whitespace-only,
    or carries only the untouched ``Retro dispositions: TODO — …`` scaffold
    placeholder (scanned over the Auto-Retro span only, fences masked). This is
    the only content judgment the deterministic rung makes — emptiness, never
    substance. Treating the seeded placeholder as blank-equivalent keeps rung 1a
    (block-the-blank) live: seeding a visible TODO must not silently disable it.
    """
    body = _section_body(_mask_fences(text), "Auto-Retro")
    if body is None or not body.strip():
        return True
    residual = _DISPOSITION_PLACEHOLDER.sub("", body)
    return not residual.strip()


def retro_lists_improvements(retro_text: str) -> bool:
    """True when the retro's ``## Next Improvements`` section carries ≥1 list item.

    Presence/structure only — never classifies the prose (the round-2 word-list
    trap). An absent or renamed section is inert (returns False), so block-the-
    blank cannot fire without a structurally-identifiable improvement to dispose.
    """
    body = _section_body(_mask_fences(retro_text), "Next Improvements")
    if body is None:
        return False
    return any(_LIST_ITEM.match(line) for line in body.splitlines())


def find_disposition_optout(text: str) -> str | None:
    """Return the opt-out reason when a valid ``Retro dispositions: none — <reason>``
    line (≥ ``MIN_OPTOUT_REASON`` chars) sits in the Auto-Retro span, else ``None``.

    Auto-Retro-scoped on purpose: a full-text scan is poisoned — real goal bodies
    describe the marker while specifying it (round-2 B-2), which would falsely
    exempt them.
    """
    body = _section_body(_mask_fences(text), "Auto-Retro")
    if not body:
        return None
    match = _DISPOSITION_OPTOUT.search(body)
    if match is None:
        return None
    reason = match.group(1).strip()
    return reason if len(reason) >= MIN_OPTOUT_REASON else None


def _bound_retro_path(report: dict[str, Any]):
    """The path of the satisfied + bound ``retro_artifact`` evidence file, if any.

    A retro whose F1 binding failed is excluded (it is already an ok=False
    binding failure; block-the-blank must not read an unbound retro's body).
    """
    blocked = {entry["name"] for entry in report.get("binding_failures", [])}
    found = None
    for entry in report["satisfied"]:
        if (
            entry["name"] == "retro_artifact"
            and entry.get("via") == "evidence"
            and entry["name"] not in blocked
        ):
            found = entry["path"]
    return found
