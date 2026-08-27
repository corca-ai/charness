"""Validate the small, typed vocabulary used by lesson score events.

The ledger owns durable lesson history and this module owns score-event shape:
one encounter has one outcome and one human anchor. Selection uses the resulting
counts; it does not require a session receipt, retro disposition, or evaluator
continuity record.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

# The four values, and the disposition each one routes to without a human
# re-deriving which. Every one is a fact about the AUTHOR'S OWN BEHAVIOUR, not a
# judgement about the lesson's wording -- that is the whole reason the split
# works. Whether better wording would have caught you is a counterfactual and
# unknowable from the inside; whether the lesson was in front of you when you
# decided is a fact you remember.
SCORE_OUTCOMES: dict[str, str] = {
    "changed-an-action": "graduate",
    "read-but-not-applied": "rewrite-in-place",
    "not-consulted": "strengthen-binding",
    "pushed-a-wrong-action": "rewrite-in-place",
}
# The question each outcome answers, kept beside the value so a solicitation and
# a refusal message cannot drift apart.
OUTCOME_QUESTIONS: dict[str, str] = {
    "changed-an-action": "did it change a specific action you took?",
    "read-but-not-applied": "was it in view AT the decision and still did not land?",
    "not-consulted": "did you never revisit it at the moment the class came up?",
    "pushed-a-wrong-action": (
        "did it move the work toward something wrong, or cost a read that returned nothing?"
    ),
}
WORKING_OUTCOME = "changed-an-action"

IDENTITY_KEYS = {"event_id", "source_retro", "lesson_id"}
# Two shapes, one list. Legacy events keep their exact committed bytes: the
# ledger is append-only and its committed prefix is compared against
# `git show HEAD:<path>`, so translating them would rewrite history -- and they
# were recorded when `changed-an-action` was not expressible, so reinterpreting
# them would manufacture evidence that was never given. They are marked
# `legacy-scalar` BY SHAPE rather than by a stored field, which is the only
# marking that costs no committed byte.
LEGACY_REQUIRED_KEYS = IDENTITY_KEYS | {"score"}
LEGACY_KEYS = LEGACY_REQUIRED_KEYS | {"anchor"}
# With no magnitude, EVERY outcome requires an anchor. One fewer rule, one more
# obligation: magnitude was doing "how strong was the effect" and "how confident
# am I" badly, and neither is needed -- strength is carried by the anchor, and
# aggregation is a count of encounters per outcome.
OUTCOME_KEYS = IDENTITY_KEYS | {"outcome", "anchor"}

RETRO_DIR = "charness-artifacts/retro"
# Shape-only, per the module docstring. A closed marker set rather than a prose
# parser, with an obvious negative case: an anchor that names only what happened
# and never what would have happened otherwise.
_COUNTERFACTUAL_MARKERS = ("otherwise", "would have", "instead of", "without it", "rather than")
_MARKER_RE = re.compile("|".join(re.escape(marker) for marker in _COUNTERFACTUAL_MARKERS))
COUNTERFACTUAL_RULE = (
    f"`{WORKING_OUTCOME}` anchors must name BOTH the action taken and where the work would "
    f"have gone otherwise; say so with one of {sorted(_COUNTERFACTUAL_MARKERS)}"
)
OUTCOME_INSTRUCTION = (
    "a score event records an encounter, so it takes `outcome` (one of "
    f"{sorted(SCORE_OUTCOMES)}) and an `anchor`, and cites the retro that RECORDS the "
    "encounter rather than the lesson's origin retro"
)


def is_legacy_scalar(event: Any) -> bool:
    """A pre-vocabulary event, identified by the field only it carries."""
    return isinstance(event, dict) and "score" in event


def outcome_of(event: Any) -> str | None:
    """The event's outcome, or None when it is a legacy scalar."""
    if not isinstance(event, dict):
        return None
    value = event.get("outcome")
    return value if isinstance(value, str) else None


def valence(event: Any) -> int:
    """+1 when the lesson did its job at this encounter, -1 when it did not.

    MAGNITUDE IS RETIRED FROM BOTH VOCABULARIES, not just the new one. A legacy
    event contributes the SIGN of its scalar, never its size. That is not
    translating it into the new vocabulary -- it keeps its `score` field, is
    reported as `legacy-scalar`, and routes to no disposition -- it is refusing to
    let a `+3` authored under "how strong was the effect" outweigh three later
    encounters that failed.

    The reason is that magnitude was never valid evidence in EITHER vocabulary.
    It was doing "how strong was the effect" and "how confident am I" at once and
    neither is recoverable from one digit, which is why the new vocabulary drops
    it rather than reinterpreting it. Direction survives because the author did
    assert a direction; size does not, because nothing ever calibrated it.

    An earlier draft justified this instead by claiming "every legacy event in
    this repo's ledger is positive". A bounded reviewer measured the ledger: four
    of the twelve are `-2`. That sentence was true in the 2026-08-14 spec and was
    transcribed forward without re-reading the file -- the
    `premise-not-checked-against-source` class, recorded here rather than quietly
    deleted because this module is where that class is supposed to be caught.
    """
    if is_legacy_scalar(event):
        score = event.get("score")
        return (score > 0) - (score < 0) if type(score) is int else 0
    return 1 if outcome_of(event) == WORKING_OUTCOME else -1


def anchor_shape_error(outcome: str, anchor: Any) -> str | None:
    """The refusal for an anchor that cannot carry its outcome's claim."""
    if not isinstance(anchor, str) or not anchor.strip():
        return "anchor must be a non-empty non-whitespace string"
    if outcome == WORKING_OUTCOME and not _MARKER_RE.search(anchor.lower()):
        return COUNTERFACTUAL_RULE
    return None


def canonical_retro_citation(value: Any) -> bool:
    """Return whether *value* is a canonical repo-relative retro path.

    This is deliberately a shape check. The ledger needs a stable citation for
    selection history but does not infer a retro's session ownership or require a
    second continuity record.
    """
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        return False
    path = PurePosixPath(value)
    # Keep the path check local and deterministic: it prevents traversal,
    # nested/ambiguous paths, and using the generated summary as a source.
    if path.is_absolute() or ".." in path.parts or str(path) != value:
        return False
    if len(path.parts) != 3 or path.parts[:2] != ("charness-artifacts", "retro"):
        return False
    return path.suffix == ".md" and path.name != "recent-lessons.md"


def score_event_error(event: dict[str, Any]) -> str | None:
    """The single refusal for one score event, or None when it validates."""
    keys = set(event)
    if is_legacy_scalar(event):
        if not LEGACY_REQUIRED_KEYS <= keys <= LEGACY_KEYS:
            return (
                f"a legacy-scalar score event takes keys {sorted(LEGACY_REQUIRED_KEYS)} and "
                f"allows only `anchor` beyond them; {OUTCOME_INSTRUCTION}"
            )
        score = event.get("score")
        if type(score) is not int or not -3 <= score <= 3:
            return "legacy-scalar score must be an integer in -3..3"
        if "anchor" in event and not (isinstance(event["anchor"], str) and event["anchor"].strip()):
            return "anchor must be non-empty non-whitespace when present"
        return None
    if keys != OUTCOME_KEYS:
        return f"unexpected or missing fields; {OUTCOME_INSTRUCTION}"
    outcome = event.get("outcome")
    if outcome not in SCORE_OUTCOMES:
        return f"`outcome` must be one of {sorted(SCORE_OUTCOMES)}"
    return anchor_shape_error(outcome, event.get("anchor"))


def legacy_prefix_error(events: list[Any]) -> str | None:
    """Legacy-scalar events may only be a PREFIX of the score list.

    The migration is one-way and this is what makes it so. `record_lesson_score`
    refuses to write a legacy event, and this refuses to accept one appended
    after any outcome event -- so the first outcome event closes the old shape
    permanently, without a schema flag anyone can flip back.
    """
    seen_outcome = False
    for position, event in enumerate(events, start=1):
        if is_legacy_scalar(event):
            if seen_outcome:
                return (
                    f"score event {position} uses the retired legacy-scalar shape after the "
                    f"vocabulary was adopted; {OUTCOME_INSTRUCTION}"
                )
        else:
            seen_outcome = True
    return None


def outcome_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    """Encounters per outcome, plus the frozen legacy cohort under its own key.

    A COUNT rather than an author-guessed magnitude, and `legacy-scalar` is a
    reported bucket rather than a silent absence: `changed-an-action: 0` over
    twelve legacy events means something different from `changed-an-action: 0`
    over nothing at all.
    """
    counts = {outcome: 0 for outcome in sorted(SCORE_OUTCOMES)}
    counts["legacy-scalar"] = 0
    for event in events:
        key = "legacy-scalar" if is_legacy_scalar(event) else outcome_of(event)
        if key in counts:
            counts[key] += 1
    return counts
