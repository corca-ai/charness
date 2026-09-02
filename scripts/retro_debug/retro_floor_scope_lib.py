#!/usr/bin/env python3
"""The dated, generic retro floors and their announcement payload.

The lesson ledger remains an optional memory/selection surface. It is not a
retro disposition contract: this module only describes obligations that every
retro validator actually enforces.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

# Every retro must consult the north star and say what it found (user standing
# request, 2026-08-02). Recorded as a floor rather than prose because prose is what it
# already was: `SKILL.md` has always pointed at the design standard, two consecutive
# retros still shipped without a facet mapping, and the operator had to ask twice.
#
# Presence-only, never a content classifier: the floor proves the question was ASKED,
# and the answer's quality is the fresh-eye reviewer's call.
#
# Lands 2026-08-02; enforcement begins the NEXT day so every retro frozen on or before
# the landing day is grandfathered -- the established RESIDUAL_LEDGER_RULE_DATE /
# STRUCTURAL_FOLLOWUP_RULE_DATE precedent.
NEXT_IMPROVEMENTS_HEADING = "## Next Improvements"
# Recurrence-lineage floor for standalone retros: the symmetric extension of the
# achieve rung 1d to a session retro's `## Next Improvements`. Its own enforce-from
# date lands the day after this floor so every existing retro is grandfathered; only
# retros dated on/after it must carry a lineage marker on issue-form dispositions.
RECURRENCE_LINEAGE_RULE_DATE = date(2026, 6, 9)
PERSISTED_FORM_RULE_DATE = date(2026, 6, 25)
NORTH_STAR_RULE_DATE = date(2026, 8, 3)
NORTH_STAR_HEADING = "North Star Alignment"


def date_activated_rules(repo_root: Path, *, output_dir: Path | None = None) -> list[dict[str, object]]:
    """Return generic retro floors that switch on by artifact date.

    ``repo_root`` and ``output_dir`` stay as tolerated call-shape arguments for
    installed consumers, but optional lesson-ledger state is intentionally not
    consulted. A ledger is memory/selection data, not a retro disposition contract.
    """
    return [
        {
            "id": "north-star-alignment",
            "rule_date": NORTH_STAR_RULE_DATE.isoformat(),
            "what": f"a retro dated on/after this needs a `## {NORTH_STAR_HEADING}` section with content",
            "enforced_here": True,
        },
        {
            "id": "recurrence-lineage",
            "rule_date": RECURRENCE_LINEAGE_RULE_DATE.isoformat(),
            "what": (
                f"`{NEXT_IMPROVEMENTS_HEADING}` issue-routed dispositions need a recurrence-lineage "
                "marker (`novel:` / `recurs:`)"
            ),
            "enforced_here": True,
        },
        {
            "id": "persisted-form",
            "rule_date": PERSISTED_FORM_RULE_DATE.isoformat(),
            "what": "`## Persisted` must read `Persisted: yes: <path>` or `Persisted: no: <reason>`",
            "enforced_here": True,
        },
    ]
