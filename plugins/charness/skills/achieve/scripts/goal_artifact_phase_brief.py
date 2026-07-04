"""Phase-keyed reading brief for achieve runs.

check_goal_artifact.py attaches this to its JSON so a run reads only the
current phase's section of the large references instead of the full docs.
Declarative data, advisory routing only — never a blocking floor.
"""
from __future__ import annotations

# floor-addition-restraint: advisory routing brief, non-blocking by design

PHASE_BRIEFS: dict[str, dict[str, object]] = {
    "draft": {
        "phase": "before",
        "lifecycle_section": "## Before",
        "goal_artifact_sections": ["## Location", "## Shape", "## Helper Scripts"],
    },
    "active": {
        "phase": "during",
        "lifecycle_section": "## During",
        "goal_artifact_sections": ["## Helper Scripts"],
        "closeout_handoff": (
            "when this run starts closeout, run describe_goal_closeout_shape.py "
            "and read lifecycle.md `## After`"
        ),
    },
    "blocked": {
        "phase": "during",
        "lifecycle_section": "## During",
        "goal_artifact_sections": [
            "## Remaining Boundary Matrix (conditional, before blocked)"
        ],
    },
    "complete": {
        "phase": "after",
        "lifecycle_section": "## After",
        "goal_artifact_sections": [
            "## Timebox Fields",
            "## Closeout Delegation (optional, orchestrated mode)",
            "## Metrics Honesty",
        ],
    },
}

_NOTE = (
    "Read only the named lifecycle.md section for the goal's current status "
    "(plus the short `## Honest Proof Discipline` coda); other phases' depth "
    "loads when the phase changes. goal_artifact_sections are the "
    "phase-relevant depth in references/goal-artifact.md."
)


def phase_brief(status: str | None) -> dict[str, object] | None:
    brief = PHASE_BRIEFS.get(status or "")
    if brief is None:
        return None
    return {**brief, "note": _NOTE}
