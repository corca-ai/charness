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
    "Final Verification",
    "User Verification Instructions",
    "Auto-Retro",
)


def _bodies(text: str, section: str, section_bounds) -> list[str]:
    """Every matching section body, via the contract's ONE owner of the H2 walk.

    Not a local walk. `goal_artifact_markdown.section_bounds` records that six
    modules had each hand-rolled this same nine-line loop, "each subtly its own:
    masked-vs-raw, `""`-vs-`None` for absent, case-sensitive or not", and that
    adding another copy while shipping a slice about one rule having one owner is
    what made consolidating it a real repair. A first cut of this module added an
    eighth copy anyway; the duplicate-ratchet gate refused it, which is the gate
    doing exactly its job.
    """
    return [text[start:end] for start, end in section_bounds(text, section)]


def _normalized(body: str) -> str:
    """Whitespace-insensitive body text, so reflowing a paragraph is not content."""
    return " ".join(body.split())


def classify(masked_text: str, raw_text: str, template_text: str,
             sections: tuple[str, ...], *, section_bounds) -> dict:
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
        masked_bodies = _bodies(masked_text, name, section_bounds)
        if not masked_bodies:
            continue
        # EMPTINESS is decided on the RAW body, template-identity on the masked
        # one. `mask_fences` blanks fenced regions, so a section written entirely
        # as fenced command blocks -- the most natural shape for a verification
        # plan -- normalized to "" and was refused as "present but EMPTY", a
        # statement the code had not established. Identity still reads the masked
        # body, because a goal that QUOTES the template must not have the
        # quotation counted as its own content.
        unmasked_bodies = _bodies(raw_text, name, section_bounds)
        if any(not _normalized(body) for body in unmasked_bodies):
            empty.append(name)
            continue
        template_bodies = _bodies(template_text, name, section_bounds)
        template_body = _normalized(template_bodies[0]) if template_bodies else ""
        if template_body and any(
            _normalized(body) == template_body for body in masked_bodies
        ):
            template_identical.append(name)
    hollow = sorted(empty + template_identical)
    run_filled = [name for name in hollow if name in RUN_FILLED_SECTIONS]
    # FAIL CLOSED on anything in neither tuple. The two lists are hand-maintained
    # against the section set this module does not own; an unclassified section
    # must cost a false stop rather than a silent pass when the template grows.
    # Defaulting an unclassified section to "must be written" makes drift cost a
    # false stop instead of a silent pass.
    blocking = [name for name in hollow if name not in RUN_FILLED_SECTIONS]
    return {
        "evaluated": True,
        "hollow": hollow,
        "empty": empty,
        "still_template_text": template_identical,
        "blocking": blocking,
        "run_filled_hollow": run_filled,
        "unclassified_blocking": [name for name in blocking if name not in SHAPING_SECTIONS],
        "reason": _reason(empty, template_identical, blocking, run_filled),
    }


def _reason(empty: list[str], template_identical: list[str], blocking: list[str],
            run_filled: list[str]) -> str:
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
            f"{detail}. These must be written before `/goal`: "
            + ", ".join(blocking)
            + ". A section with genuinely nothing to say keeps its heading and states "
            "`N/A — <reason>`."
        )
    # Only reachable when EVERY hollow section is run-filled, so the parenthetical
    # is now a fact rather than a label applied to whatever did not block.
    return f"{detail} ({', '.join(run_filled)}: filled by the run; reported, not refused)"
