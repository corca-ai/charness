"""Phase-keyed reading brief for achieve runs.

check_goal_artifact.py attaches this to its JSON so a run reads only the
current phase's lifecycle file (lifecycle.md was split by phase) instead of
the full three-phase contract. Declarative data, advisory routing only —
never a blocking floor.
"""
from __future__ import annotations

# floor-addition-restraint: advisory routing brief, non-blocking by design

PHASE_BRIEFS: dict[str, dict[str, object]] = {
    "draft": {
        "phase": "before",
        "lifecycle_file": "references/lifecycle-before.md",
        "lifecycle_section": "## Before",
        "goal_artifact_sections": ["## Location", "## Shape", "## Helper Scripts"],
    },
    "active": {
        "phase": "during",
        "lifecycle_file": "references/lifecycle-during.md",
        "lifecycle_section": "## During",
        "goal_artifact_sections": ["## Helper Scripts"],
        "closeout_handoff": (
            "when this run starts closeout, run describe_goal_closeout_shape.py "
            "and read lifecycle-after.md"
        ),
    },
    "blocked": {
        "phase": "during",
        "lifecycle_file": "references/lifecycle-during.md",
        "lifecycle_section": "## During",
        "goal_artifact_sections": [
            "## Remaining Boundary Matrix (conditional, before blocked)"
        ],
    },
    "superseded": {
        "phase": "after",
        "lifecycle_file": "references/lifecycle-after.md",
        "lifecycle_section": "## After",
        "goal_artifact_sections": [
            "## Superseded Record (conditional, before superseded)",
        ],
    },
    "complete": {
        "phase": "after",
        "lifecycle_file": "references/lifecycle-after.md",
        "lifecycle_section": "## After",
        "goal_artifact_sections": [
            "## Timebox Fields",
            "## Closeout Delegation (optional, orchestrated mode)",
            "## Metrics Honesty",
        ],
    },
}

_NOTE = (
    "Read only the named lifecycle_file (the goal's current-phase file) for the "
    "goal's current status (plus the short `lifecycle.md` `## Honest Proof "
    "Discipline` coda); other phases' depth loads when the phase changes. "
    "goal_artifact_sections are the phase-relevant depth in "
    "references/goal-artifact.md."
)


def phase_brief(status: str | None) -> dict[str, object] | None:
    brief = PHASE_BRIEFS.get(status or "")
    if brief is None:
        return None
    return {**brief, "note": _NOTE}
