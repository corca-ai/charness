"""The handoff artifact's canonical sections and its CONTENT-WORD budget.

One module owns both because they are the same decision: which lines the
artifact is *required* to have, and therefore which lines the budget must not
charge the author for.

The budget counts CONTENT WORDS, not lines. It excludes:

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
different words would report a status the gate contradicts.

WHY WORDS AND NOT LINES (2026-08-19). The budget charged per NEWLINE until this
change, so the same prose cost whatever the author's wrap width happened to be.
Measured on this repo's own handoff, one unchanged text: 80 counted units at 90
columns, 77 at 100, 67 at 120, 44 at 200, 24 unwrapped -- a 3.3x swing on a
choice no rule requires, because `.markdownlint-cli2.jsonc` sets `MD013: false`
and nothing enforces a width at all. Two consequences, both live: the cheapest
way to pass was to REWRAP WIDER, which makes a handoff less readable while the
gate goes green; and the refusal message asserted that "trimming formatting will
not help", which was false for exactly that move. Across the 156 revisions since
the ceiling was raised to 78, the line bar admitted between 222 and 1240 words
-- a 5.6x spread in the thing the docstring said it was measuring.

This is the SECOND pass at the same defect. The 58-line re-base already found
that "the raw count was measuring formatting" and fixed it by excluding blank
lines, headings and `## References` -- then kept charging per newline, which is
also formatting. The repair carried the class it repaired; a word count is
wrap-invariant and does not.

BLIND CLASS -- what this measure CANNOT see. A word is a whitespace-separated
token, so `[label](path)` costs ONE -- there is no space inside it -- and a bare
URL costs one too, while either can occupy most of a visual line. (An earlier
draft of this paragraph said two; `"[label](path)".split()` returns one element,
and a bounded reviewer caught the arithmetic in the sentence that justifies the
`## References` exclusion.) A handoff padded with inline links therefore grows on
screen without growing against the ceiling. That is deliberate and consistent with the
`## References` exclusion (single-sourcing to an owning artifact is the behavior
this skill asks for), but it means this budget is a READING-LOAD proxy, not a
screen-space one. It also cannot see repetition, hedging, or a bullet that says
nothing -- no automatic measure can, which is why SKILL.md keeps a target well
under the ceiling and why the ceiling is a failure guard rather than a budget to
spend.
"""
from __future__ import annotations

from typing import Sequence

# 900, REPLACING the 78-CONTENT-LINE ceiling on 2026-08-19 -- replacing, not
# translating. There is no faithful translation and this is a new decision: the
# line bar admitted 222-1240 words across the 156 revisions of its era, so no word
# number reproduces it. 900 was chosen against that history rather than against the
# current file -- it admits 153 of those 156 revisions unchanged, and leaves the
# handoff at the time of the change (839 words) about 7% of headroom, matching the
# 0-13% the line ceiling typically left. Deliberately NOT the tightest number that
# fits today's artifact: 850 would have left 11 words, which is a bar fitted to its
# own test set.
DEFAULT_MAX_CONTENT_WORDS = 900
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
    """SELECTS which lines hold chargeable content; it no longer decides the cost.

    Kept as its own function because the selection rule (which lines are the
    author's prose rather than the gate's own scaffolding) is a separate decision
    from the unit charged: `content_words` is defined in terms of it, and a caller
    that wants to SHOW an author which lines were charged needs the list.

    Honest state: no production caller uses the list today -- only `content_words`
    and the tests do. An earlier version of this docstring claimed the planner and
    the preflight needed it, which was an unearned claim on a proof surface; a
    bounded reviewer refused it. It stays because the selection rule has to live
    somewhere separable from the charge, not because something is calling it.
    """
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


def content_words(lines: Sequence[str]) -> int:
    """The measure the budget charges: whitespace-separated tokens of counted content.

    Wrap-invariant by construction -- joining or splitting a physical line cannot
    change this number. That is the whole point of the unit; see the module
    docstring for what it still cannot see.
    """
    return sum(len(line.split()) for line in content_lines(lines))
