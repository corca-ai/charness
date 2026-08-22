"""Which required sections are PRESENT but say nothing.

`--pursue-ready` reported a goal as shaped when whole required sections were bare
headings. The check is the thing a session trusts INSTEAD of reading the
artifact, so "pursue-ready" came to mean "has the right headings" rather than "is
shaped" -- which is the failure the readiness check exists to prevent. Reported
from a downstream consumer repo, and a third-or-later sighting: it had been
recorded in successive operator decision queues without being filed, which was
itself part of the report.

## Why "non-empty" is not the test

The obvious fix -- require a non-empty body -- is nearly useless here, because the
scaffold seeds GUIDANCE PROSE into every section it creates. A freshly scaffolded
`## Interview Decisions` already contains three lines explaining what interview
decisions are, so it is non-empty and still says nothing about this goal.

So hollow is defined against the template: a section is hollow when its body is
empty **or** still byte-identical (modulo whitespace) to what the scaffold wrote
there. That is a structural fact, not a judgement about prose quality, and it
answers the question actually asked -- present versus written.

## Why this reports more than it refuses

The report that raised this also named the trap in the fix: a section that is
legitimately empty at shaping time (`## Slice Log` before any slice runs) needs a
way to say so explicitly, or the check trades one false verdict for another.
Most run-filled sections are template-identical at draft time BY DESIGN -- that is
what a fresh scaffold looks like -- so refusing on template-identity alone would
refuse every new draft.

Hollow sections are therefore always REPORTED, and only the shaping-time set is
refused. A reader gets the list either way, which is the half a single
ready/not-ready verdict was hiding.

The explicit escape already exists in this contract and needs no new syntax: the
reference says a goal that genuinely has nothing for a section "keeps the heading
and states ``N/A — <reason>``". That is content, so it is not hollow.
"""

from __future__ import annotations

#: Required sections a goal must have WRITTEN before it can be pursued. These are
#: the Before-phase's own output: if they are still the scaffold's words, nobody
#: shaped this goal, and `/goal` would activate a template.
SHAPING_SECTIONS = (
    "Goal",
    "Non-Goals",
    "Boundaries",
    "User Acceptance",
    "Agent Verification Plan",
    "Slice Plan",
    "Context Sources",
    "Interview Decisions",
    "Plan Critique Findings",
)

#: Required sections that are legitimately hollow at pursue time because the RUN
#: fills them. Reported, never refused -- naming them is what keeps the reported
#: list honest rather than alarming.
RUN_FILLED_SECTIONS = (
    "Slice Log",
    "Off-Goal Findings",
    "Operator Decision Queue",
    "Final Verification",
    "User Verification Instructions",
    "Auto-Retro",
)


def _body(text: str, section: str, section_bounds) -> str | None:
    """One section's body, via the contract's ONE owner of the H2 walk.

    Not a local walk. `goal_artifact_markdown.section_bounds` records that six
    modules had each hand-rolled this same nine-line loop, "each subtly its own:
    masked-vs-raw, `""`-vs-`None` for absent, case-sensitive or not", and that
    adding another copy while shipping a slice about one rule having one owner is
    what made consolidating it a real repair. A first cut of this module added an
    eighth copy anyway; the duplicate-ratchet gate refused it, which is the gate
    doing exactly its job.
    """
    bounds = section_bounds(text, section)
    if bounds is None:
        return None
    start, end = bounds
    return text[start:end]


def _normalized(body: str) -> str:
    """Whitespace-insensitive body text, so reflowing a paragraph is not content."""
    return " ".join(body.split())


def classify(masked_text: str, template_text: str, sections: tuple[str, ...], *, section_bounds) -> dict:
    """Report which of `sections` are hollow, and why each one is.

    `masked_text` is fence-masked by the caller for the same reason every other
    floor here masks: a goal that QUOTES the template inside a fenced block must
    not have the quotation counted as its own content.

    Sections that are ABSENT are not reported -- the missing-heading floor owns
    that, and reporting a missing section as hollow would say the same thing twice
    in two vocabularies.
    """
    empty: list[str] = []
    template_identical: list[str] = []
    for name in sections:
        raw = _body(masked_text, name, section_bounds)
        if raw is None:
            continue
        body = _normalized(raw)
        template_body = _body(template_text, name, section_bounds)
        if not body:
            empty.append(name)
        elif template_body is not None and body == _normalized(template_body):
            template_identical.append(name)
    hollow = sorted(empty + template_identical)
    blocking = [name for name in hollow if name in SHAPING_SECTIONS]
    return {
        "hollow": hollow,
        "empty": empty,
        "still_template_text": template_identical,
        "blocking": blocking,
        "run_filled_hollow": [name for name in hollow if name in RUN_FILLED_SECTIONS],
        "reason": _reason(empty, template_identical, blocking),
    }


def _reason(empty: list[str], template_identical: list[str], blocking: list[str]) -> str:
    """Say WHICH sections are hollow and in which of the two ways.

    The core ask, and the reason this is not a boolean: report which ones are
    hollow rather than a single ready/not-ready verdict. A caller that only
    learns `False` has to re-read the artifact to find out what to fix, which is
    the work the check was supposed to do.
    """
    if not empty and not template_identical:
        return ""
    parts = []
    if empty:
        parts.append("present but EMPTY: " + ", ".join(empty))
    if template_identical:
        parts.append("still the scaffold's own words: " + ", ".join(template_identical))
    detail = "; ".join(parts)
    if blocking:
        return (
            f"{detail}. Shaping sections must be written before `/goal`: "
            + ", ".join(blocking)
            + ". A section with genuinely nothing to say keeps its heading and states "
            "`N/A — <reason>`."
        )
    return f"{detail} (run-filled sections; reported, not refused)"
