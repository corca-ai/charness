"""The handoff artifact's canonical sections and its CONTENT-line budget.

One module owns both because they are the same decision: which lines the
artifact is *required* to have, and therefore which lines the budget must not
charge the author for.

The budget counts CONTENT, not file length. It excludes:

- blank lines (formatting),
- the canonical ``##`` headings the validator itself REQUIRES (charging for a
  line the gate mandates is charging the author for obeying the gate),
- the whole ``## References`` block, whose long link lines are the artifact
  doing its job — single-sourcing durable detail to its owning artifact is the
  behavior this skill asks for, and a raw line count taxed exactly that.

The ``# ...`` title and any non-canonical ``##`` heading DO count: a heading the
author invented is a structure choice, and the shape rule rejects extras anyway.

Both the repo validator (which enforces the ceiling) and the run planner (which
forecasts it) read this. A planner that agreed on the ceiling but counted
different lines would report a status the gate contradicts.
"""
from __future__ import annotations

from typing import Sequence

DEFAULT_MAX_CONTENT_LINES = 58
REQUIRED_SECTIONS = (
    "## Workflow Trigger",
    "## Current State",
    "## Next Session",
    "## Discuss",
    "## References",
)
# The handoff skill's Output Shape lists this section; rejecting it would make
# following the skill a gate failure. It stays optional because the skill says
# the handoff "should usually contain" it, not always -- but an empty one is a
# header pretending to be a baton, so presence implies content.
OPTIONAL_SECTIONS = ("## Continuation Capability",)
CANONICAL_SECTIONS = frozenset(REQUIRED_SECTIONS) | frozenset(OPTIONAL_SECTIONS)
REFERENCES_SECTION = "## References"


def content_lines(lines: Sequence[str]) -> list[str]:
    """The lines the budget charges for: prose the next operator has to read."""
    counted: list[str] = []
    in_references = False
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("## "):
            in_references = stripped == REFERENCES_SECTION
            if stripped in CANONICAL_SECTIONS:
                continue
        if in_references or not stripped:
            continue
        counted.append(raw)
    return counted
