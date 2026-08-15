"""What a lesson score MEANS, and which retro it belongs to.

WHY THIS IS ITS OWN MODULE (#627, #631). `lesson_ledger_lib` used ONE citation
rule for two different acts: seeding a transition needs evidence that the class
EXISTS -- a `recurrence-class:` tag is exactly right -- and scoring needs evidence
that an ENCOUNTER happened, for which the anchor is exactly right. (Line numbers
are deliberately not cited: the two rules have moved twice, and the numbers an
earlier draft carried were transcribed from a 2026-08-14 spec and pointed at
unrelated code by the time anyone read them.)
One rule served the first and structurally excluded half the second, so:

- a lesson that WORKED could not be credited at all. Its source set is rebuilt
  from recurrence tags, and `(source_retro, lesson_id)` is unique, so scoring a
  lesson a second time required tagging a new retro with its recurrence class --
  i.e. declaring the class recurred in order to say it did not. Three lessons
  that measurably changed an action in the 2026-08-14 session went unrecorded.
- a session drawing lessons from two ORIGIN retros always violated
  `foreign-score-source` (#631), because the reconciler asks which scores a
  retro's disposition speaks for and the old citation made that underivable.

So the two acts get two rules. Seeding still cites the origin retro. Scoring
cites the retro that RECORDS THE ENCOUNTER -- this session's own retro -- which
is what `lesson_evaluation_records_lib` already filled into its score command
template (`<repo-relative path of the retro being written>`) while
`record_lesson_score.py` refused that very value.

THE THREE ASYMMETRIES ARE LOAD-BEARING, not tidiness. The symmetric design is
the obvious one and is wrong in three specific ways; each is enforced below and
each has its own negative case in the tests:

1. A commit hash is PERMITTED evidence, never REQUIRED. A lesson usually fails
   at a judgement, not at an edit -- the 2026-08-14 negative rests on three
   anchors, two of which touched no file. A hash requirement collects only the
   failures that edited something.
2. `changed-an-action` carries a STRICTER anchor bar than the other three: it
   must name where the work would have gone otherwise. Making positives
   recordable removes a structural bias that was suppressing them and installs a
   self-serving one in its place; the asymmetric bar is what pays for that. The
   same session that produced this vocabulary had four self-assessments proven
   false by readers.
3. `not-consulted` is recordable ONLY when the session actually committed the
   class the lesson names. Without that guard it is the default -- every lesson
   a session had no occasion to use is trivially "not consulted", and a
   ten-lesson presentation would emit ten `strengthen-binding` signals per
   session for lessons that were merely irrelevant.

WHAT IS DELIBERATELY NOT ENFORCED HERE. The anchor bar is a SHAPE check, not a
semantic one: an author who wants to defeat it can. It exists to make the
omission visible at the moment of writing, which is the only moment the author
still remembers the counterfactual -- not to prove the counterfactual is true.
That is the same containment the release-narrative lint uses, and the ledger
contract's `Deliberately Not Doing` keeps content classification off these
surfaces on purpose.
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
# The outcome whose LITERAL READING IS ALMOST ALWAYS TRUE, and therefore the one
# outcome carrying a precondition (`binding_violations` proves it). Kept as a set
# of one on purpose: the temptation is to widen it to `read-but-not-applied`,
# which also implies the class recurred, and the canonical spec's third asymmetry
# refuses that widening by name -- "this is the ONE outcome needing a
# precondition". A precondition on an outcome that is not trivially true buys no
# refusal and costs the author a recurrence tag they may not owe.
RECURRENCE_ASSERTING_OUTCOMES = frozenset({"not-consulted"})

IDENTITY_KEYS = {"event_id", "source_retro", "lesson_id", "session_id"}
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
    """A repo-relative Markdown path under the retro directory.

    Existence is NOT checked here, and that is deliberate FOR THREE OF THE FOUR
    OUTCOMES. The documented order is `append scores first, write the DISPOSITION
    second` (`skills/public/retro/references/lesson-evaluation.md`), so the retro
    recording the encounter is typically still unwritten when the score lands.
    Existence and session ownership are therefore proven by the reconciler that
    runs after persistence.

    `not-consulted` is the exception, and this docstring said otherwise until
    round 2 caught it: because that outcome ASSERTS the class recurred, its
    evidence is a `recurrence-class:` bullet that must already exist, so
    `record_lesson_score` refuses it at write time rather than leaving a
    committed encounter permanently red on an append-only ledger.
    """
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        return False
    path = PurePosixPath(value)
    # The SAME shape rule `lesson_evaluation_continuity_lib.canonical_retro_path`
    # enforces, restated rather than imported: that module reaches this one
    # through `lesson_ledger_lib`, so importing it back would close a cycle. The
    # three clauses are what a bounded reviewer showed the loose version admitted
    # -- `charness-artifacts/retro/../../../tmp/x.md` (escapes the tree),
    # `recent-lessons.md` (explicitly not a retro, so no disposition can ever
    # claim it), and any non-canonical spelling of a real path. All three are
    # permanent once committed, because the ledger refuses to rewrite a score
    # event, so a shape this lax turns one typo into an unclearable gate.
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


def scores_owned_by(events: list[dict[str, Any]], *, session_id: str, path: str) -> list[dict[str, Any]]:
    """The scores a retro's disposition at `path` speaks for.

    TWO OWNERSHIP RULES, because there are two citation contracts (#631):

    - an OUTCOME event names the retro that records the encounter, so it is owned
      by the retro it cites; and
    - a LEGACY event names the lesson's ORIGIN retro, which says nothing about
      who declares it, so it is owned by whichever retro CLAIMS ITS SESSION.
      `duplicate-session-reference` already refuses a session claimed by more
      than one retro, so that owner is unique.

    Reading legacy events under the outcome rule is what made #631 unclearable:
    a session scoring two lessons with two different origins had
    `len(session_scores) == 2` and `len(matching) <= 1` for EVERY retro that
    could declare it, so no disposition could ever be written truthfully.
    """
    return [
        event
        for event in events
        if event.get("session_id") == session_id
        and (is_legacy_scalar(event) or event.get("source_retro") == path)
    ]


def foreign_scores(events: list[dict[str, Any]], *, session_id: str, path: str) -> list[dict[str, Any]]:
    """Outcome events in this session that cite some OTHER retro.

    Legacy events are exempt because their citation was never a claim about who
    declares them. This keeps the check that has a real failure behind it -- a
    session's encounters attributed to a retro that does not claim the session --
    while retiring the false positive.
    """
    return [
        event
        for event in events
        if event.get("session_id") == session_id
        and not is_legacy_scalar(event)
        and event.get("source_retro") != path
    ]


def binding_violations(
    events: list[dict[str, Any]], *, session_id: str, path: str, recurrence_sources: dict[str, set[str]]
) -> list[tuple[str, str]]:
    """`(id, detail)` for encounters whose post-persistence binding does not hold.

    This is the half `canonical_retro_citation` deliberately does not check,
    running where the retro exists: the `not-consulted` precondition. An author
    may only record "I never revisited it" about a session that ACTUALLY
    COMMITTED the class -- which is exactly a `recurrence-class: <lesson_id>`
    bullet in the retro doing the recording. Without it, `not-consulted` is
    trivially true of every lesson a session had no occasion to use.
    """
    rows: list[tuple[str, str]] = []
    # ONE ENCOUNTER PER LESSON PER SESSION, enforced for both vocabularies.
    # The ledger's uniqueness key is `(source_retro, lesson_id)` with NO session
    # component, and a legacy citation is valid against ANY retro carrying the
    # class tag -- so a recurring class with several tagged origins could take two
    # legacy events for one lesson in one session, and after `foreign_scores`
    # stopped reading legacy citations nothing compared them to the declaring
    # retro any more. A bounded reviewer found that the #631 narrowing opened it.
    # Checked here rather than in the ledger because "which session claims this"
    # is a reconciler fact.
    seen: dict[str, str] = {}
    for event in scores_owned_by(events, session_id=session_id, path=path):
        lesson_id = event.get("lesson_id")
        if lesson_id in seen:
            rows.append(
                (
                    "duplicate-encounter",
                    f"session `{session_id}` records more than one encounter for `{lesson_id}` "
                    f"(`{seen[lesson_id]}` and `{event.get('event_id')}`); score what actually bit, "
                    "one cited event each",
                )
            )
        elif isinstance(lesson_id, str):
            seen[lesson_id] = str(event.get("event_id"))
    for event in events:
        if event.get("session_id") != session_id or event.get("source_retro") != path:
            continue
        outcome = outcome_of(event)
        if outcome not in RECURRENCE_ASSERTING_OUTCOMES:
            continue
        lesson_id = event.get("lesson_id")
        if path not in recurrence_sources.get(lesson_id, set()):
            rows.append(
                (
                    "unrecurred-encounter",
                    f"`{event.get('event_id')}` records `{outcome}` for `{lesson_id}`, which asserts "
                    f"the class recurred, but `{path}` carries no `recurrence-class: {lesson_id}` bullet",
                )
            )
    return rows
