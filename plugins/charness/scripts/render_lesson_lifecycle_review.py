#!/usr/bin/env python3
"""Render read-only lesson-lifecycle evidence for the surface the spec put in charge.

WHY THIS EXISTS (#626). `2026-08-12-lesson-ledger-and-contract-register.md:106-111`
splits the roles by what each surface can see: `retro` scores and cites because it
sees one session, and `quality` reads the candidate list and PROPOSES because "can
this be a validator instead of prose" is its own question and contract changes
already route through it. That assignment sat unwired in two stages. First the
skill said nothing: `skills/public/quality/SKILL.md` did not mention lessons at
all, so the surface named as owner had no idea it owned anything -- repaired when
this report was written. Then the report briefed a judgment with no way to ACT on
it: `record_lesson_lifecycle.py`, `record_contract_graduation_proposal.py`, and
`apply_contract_transition.py` all existed and all validated, with test-only
callers, so `state == "archived"` was never written and the preview's
resurrection slot could never be filled. `_lifecycle_commands` closes the second
stage; the reasoning for emitting rather than executing is stated there.

THE FAILURE MODE THIS IS DESIGNED AGAINST, stated in #626's own ordering comment.
A high-recurrence lesson is in one of three states, and RECURRENCE COUNT CANNOT
TELL THEM APART:

  - should have been a gate, stayed prose        -> graduate
  - wrong form: origin-incident vocabulary       -> rewrite in place
  - form is fine, it was simply not consulted    -> strengthen the binding

Proposing on recurrence selects the LOUDEST lesson rather than the one whose PROSE
is the problem. TWO things discriminate, and the ledger now carries both. The
OUTCOME says which of the three states an encounter was in, because it records a
fact about the author's own behaviour rather than a judgement about the lesson --
that is `by_disposition`, and it is a lookup rather than an inference. The ANCHOR
says what happened, and every outcome requires one. Recurrence says something is
wrong; these say what. So this report leads with anchors, groups by disposition,
and reports recurrence as context explicitly labelled as the loud signal rather
than the ranking key.

WHAT THIS DELIBERATELY DOES NOT DO.

- It does not classify a lesson into one of the three dispositions FROM ITS
  CONTENT. That is a content judgment, and the ledger contract's `Deliberately
  Not Doing` keeps content classification out of these surfaces on purpose: a
  classifier rots exactly like the prose it would replace. `by_disposition`
  is not that classifier -- it reports the routing an AUTHOR already chose by
  naming an outcome, and a lesson with no outcome evidence appears nowhere in
  it.
- It does not run an automatic archive. The ledger contract's early text calls
  archive "automatic", and its Eighth Slice -- the one that actually built schema
  v4/v5 -- supersedes that: "the current positive-only score cohort still cannot
  justify a numeric archive, promotion, or retirement threshold", and every
  lifecycle event carries a reviewed `decision_ref` and rationale. Wiring a
  threshold here would invent the calibration that slice deferred.
- It does not propose, approve, or apply anything. It emits no verdict, and a
  green run is not authorization for a lifecycle event or a graduation proposal.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
# Reused, never reimplemented: `_value` is the same shrinkage statistic the
# selection preview ranks its value bucket with. A second copy here would let
# quality's "high value" and the preview's "high value" drift apart silently,
# which is the one disagreement this report must not introduce.
_preview = import_repo_module(__file__, "scripts.lesson_selection_preview_lib")
_index = import_repo_module(__file__, "scripts.recent_lessons_lib")
# The vocabulary, not a second copy of it: the dispositions this report briefs
# are the ones the outcomes route to, and two spellings would let quality read a
# disposition the ledger cannot produce.
_outcome = import_repo_module(__file__, "scripts.lesson_score_outcome_lib")
# The state machine and the command renderer, both reused: the moves offered
# must be the moves the ledger accepts, and the command spelling must be the one
# THIS layout can run (a consuming repo has no `scripts/` of its own).
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
_records = import_repo_module(__file__, "scripts.lesson_evaluation_records_lib")

LIFECYCLE_SCRIPT = "record_lesson_lifecycle.py"
GRADUATION_SCRIPT = "record_contract_graduation_proposal.py"

# The judgment quality owes, named rather than computed. Recorded here so the
# report briefs the decision instead of leaving a reader to rediscover the
# taxonomy from an issue comment.
DISPOSITIONS = {
    "graduate": (
        "should have been a gate and stayed prose -- propose it with "
        "`record_contract_graduation_proposal.py`, which requires two distinct evidence "
        "sessions, and a displacement once the unit budget is full"
    ),
    "rewrite-in-place": (
        "wrong form -- phrased in the vocabulary of its origin incident, so it fires only on "
        "near-duplicates of that incident. Revise the wording at its source retro; the ledger "
        "keeps the id and the accumulated scores"
    ),
    "strengthen-binding": (
        "form is fine, it was simply not consulted -- bind it to a step a planner emits, "
        "rather than leaving it in a list to be remembered"
    ),
}

NON_CLAIMS = [
    "This report proposes nothing, approves nothing, and applies nothing.",
    "Recurrence is context, not a disposition: it identifies the loudest lesson, not the one "
    "whose prose is the problem.",
    "No archive, promotion, or retirement threshold exists. The ledger contract's Eighth Slice "
    "defers threshold calibration, and every lifecycle event still requires a reviewed "
    "decision_ref and rationale.",
    "A lesson with no anchored score has no lifecycle evidence here, only exposure counts.",
]


def _anchors_by_lesson(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Every score event's anchor, kept with its outcome and citing retro.

    The anchor without its outcome is unreadable -- "the fresh-eye round caught
    two overclaims" is a different finding under `changed-an-action` than under
    `pushed-a-wrong-action` -- so they travel together. This is also where the
    retired scalar did its worst work: `+3` and `-3` on identical anchor text
    rendered as the same row at different sizes.
    """
    anchors: dict[str, list[dict[str, Any]]] = {}
    for event in payload.get("score_events") or []:
        if not isinstance(event, dict):
            continue
        lesson_id = event.get("lesson_id")
        if not isinstance(lesson_id, str):
            continue
        legacy = _outcome.is_legacy_scalar(event)
        anchors.setdefault(lesson_id, []).append(
            {
            # The OUTCOME, not a number: a `-3` and a `-1` were the same
            # finding rendered at different confidence, while
            # `read-but-not-applied` and `not-consulted` are different
            # findings that a scalar rendered identically.
                "outcome": "legacy-scalar" if legacy else _outcome.outcome_of(event),
                "disposition": _outcome.SCORE_OUTCOMES.get(_outcome.outcome_of(event)),
            # Kept only for the frozen legacy cohort, so a reader can still
            # see what was recorded under the retired vocabulary without the
            # renderer pretending it means what an outcome means.
                **({"legacy_score": event.get("score")} if legacy else {}),
                "source_retro": event.get("source_retro"),
                "session_id": event.get("session_id"),
            # Absent rather than empty: legacy events permitted an unanchored
            # score at magnitude <= 1, and rendering `""` would read as a
            # blank anchor someone forgot to fill in. Every OUTCOME event has
            # one by construction.
                **({"anchor": event["anchor"]} if event.get("anchor") else {}),
            }
        )
    return anchors


def _recurrence_by_lesson(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        candidate["recurrence_class"]: {
            "independent_source_count": candidate.get("independent_source_count"),
            "source_count": candidate.get("source_count"),
            "latest_source_path": candidate.get("latest_source_path"),
        }
        for candidate in index.get("candidates") or []
        if isinstance(candidate.get("recurrence_class"), str) and candidate["recurrence_class"]
    }


def _lifecycle_commands(repo_root: Path, lesson_id: str, state: str, sequence: int) -> list[str]:
    """The runnable lifecycle moves for ONE lesson, in its CURRENT state.

    THE PRODUCTION CALLER (#626). `record_lesson_lifecycle.py`,
    `record_contract_graduation_proposal.py`, and `apply_contract_transition.py`
    all shipped, all validated, and were reachable only from tests -- so nothing
    ever wrote `state == "archived"`, the preview's archive bucket selected over
    an empty set, and the resurrection slot was structurally unfillable for the
    entire life of the ledger. A mechanism whose only caller is its own test is
    not wired; it is a fixture.

    Emitted rather than EXECUTED, and that is not a hedge. The ledger contract's
    Eighth Slice defers threshold calibration, and every lifecycle event carries a
    reviewed `decision_ref` and rationale, so a report that ran the archive itself
    would invent the calibration that slice deferred. What was missing was never
    automation -- it was the operator ever being handed the command with its
    arguments filled in, which is the same gap `#627` names on the scoring side
    and the retro run plan already closed with its score command template.

    Only the moves the state machine will actually accept are offered:
    `LIFECYCLE_TRANSITIONS` allows archive from `active` and resurrect from
    `archived`, so offering both would route an operator to a guaranteed refusal.
    """
    actions = [
        action for (action, required), _ in _ledger.LIFECYCLE_TRANSITIONS.items() if required == state
    ]
    return [
        _records.repo_or_installed_command(
            repo_root,
            LIFECYCLE_SCRIPT,
            "--repo-root",
            ".",
        # SEQUENCED, because `_replay_lifecycle` refuses a duplicate
        # `event_id`. An earlier version emitted `f"{action}-{lesson_id}"`,
        # which is constant per lesson, so archive -> resurrect -> archive
        # died on `duplicate lifecycle event_id` at the third move: this
        # function honored the state-machine filter and dropped the identity
        # one, producing exactly the guaranteed refusal the paragraph above
        # says it exists to avoid. A bounded reviewer traced it; the round
        # trip is now exercised in the SC7 test rather than asserted.
            "--event-id",
            f"{action}-{lesson_id}-{sequence}",
            "--lesson-id",
            lesson_id,
            "--action",
            action,
            "--decision-ref",
            "<repo-relative Markdown path of the review that authorized this>",
            "--rationale",
            "<why this lesson moves, in one sentence>",
        )
        for action in sorted(actions)
    ]


def _graduation_command(
    repo_root: Path, lesson_id: str, events: list[dict[str, Any]], source_retro: str
) -> str | None:
    """The graduation-proposal move, when the lesson has the evidence for it.

    SC7 names THREE slots -- archive, resurrection, graduation -- and an earlier
    version of this slice wired the first two and left
    `record_contract_graduation_proposal.py` exactly what the module docstring
    calls a fixture: a mechanism whose only caller is its own test. A bounded
    reviewer caught the under-delivery against the criterion's own wording, and
    #626 does name graduation-proposal alongside archive and resurrection.

    Returned only when at least two DISTINCT sessions carry an encounter, because
    that is the writer's own evidence floor -- graduation is a multi-session
    claim, which is exactly why the ledger contract assigns it to `quality` and
    not to `retro`. Emitting it for a one-session lesson would route an operator
    to a guaranteed refusal, the defect `_lifecycle_commands` was just repaired
    for. `None` here means "not yet proposable", not "not a candidate".
    """
    # `changed-an-action` sessions only. `events` includes legacy scalars, and
    # this module is explicit that the legacy cohort routes NOWHERE because
    # inferring a disposition from it would manufacture evidence nobody gave --
    # yet `graduate` is precisely the disposition `changed-an-action` routes to.
    # Counting legacy or failing encounters as graduation evidence would hand
    # quality a promote move for lessons absent from `by_disposition`, including
    # ones whose only recorded encounters are failures. Round 2 measured three
    # such lessons in the live ledger under the looser rule.
    sessions = sorted(
        {
            event["session_id"]
            for event in events
            if event.get("session_id") and event.get("outcome") == _outcome.WORKING_OUTCOME
        }
    )
    if len(sessions) < 2:
        return None
    evidence: list[str] = []
    for session_id in sessions:
        evidence.extend(["--evidence-session-id", session_id])
    return _records.repo_or_installed_command(
        repo_root,
        GRADUATION_SCRIPT,
        "--repo-root",
        ".",
        "--proposal-id",
        f"graduate-{lesson_id}",
        "--lesson-id",
        lesson_id,
        # KNOWN, not a placeholder: the register requires this to equal the
        # lesson's seeded `source_retro`, which the payload already holds, so
        # leaving it blank invited a refusal the renderer could prevent.
        "--source-retro",
        source_retro,
        *evidence,
        "--target-path",
        "<one of the contract register's unit paths>",
        "--target-heading",
        "<the heading this becomes>",
        "--rationale",
        "<why this belongs in the always-loaded contract rather than the ledger>",
        "--displacement-unit-id",
        "<the unit it displaces or retires; required once the unit budget is full>",
    )


def review_sort_key(item: dict[str, Any]) -> tuple[int, int, int, str]:
    """The reviewed-lesson ordering, named so a test can bind it directly."""
    return (
        -item["anchored_score_count"],
        # ASCENDING, and TIER-LOCAL. Within one anchored-count tier the
        # failing lessons now sort above the working ones, which the retired
        # key could not express at all. Across tiers `-anchored_score_count`
        # still dominates, so three `changed-an-action` anchors DO still
        # outrank one `pushed-a-wrong-action` -- deliberate, because more
        # anchored evidence is more to judge on, and it is why
        # `by_disposition` rather than this list is the "which failed"
        # surface. Round 1 flagged a comment claiming sign-blindness was
        # retired while the key was unchanged; round 2 flagged its
        # replacement for claiming a cross-tier fix this key does not make.
        item["score_total"],
        -item["score_count"],
        item["lesson_id"],
    )


def _by_disposition(reviewed: list[dict[str, Any]]) -> dict[str, list[str]]:
    """`disposition -> the lessons with at least one encounter routing to it`.

    Every disposition key is present even when empty, so `rewrite-in-place: []`
    reads as "nothing to rewrite" rather than as a key the renderer forgot. The
    legacy cohort routes NOWHERE by design: those events were recorded when
    `changed-an-action` was not expressible, so inferring a disposition from them
    would manufacture evidence that was never given.
    """
    grouped: dict[str, list[str]] = {value: [] for value in sorted(set(_outcome.SCORE_OUTCOMES.values()))}
    for item in reviewed:
        for disposition in sorted(
            {event["disposition"] for event in item["score_events"] if event.get("disposition")}
        ):
            grouped[disposition].append(item["lesson_id"])
    return grouped


def _evidence_state(anchored: int, scored: int) -> str:
    if anchored:
        return "anchored"
    if scored:
        return "unanchored-scores-only"
    return "no-score-evidence"


def build_lifecycle_review(repo_root: Path) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    output_dir = repo_root / "charness-artifacts/retro"
    summary_path = output_dir / "recent-lessons.md"
    # Re-prefixed, because the reused helpers raise through the SELECTION PREVIEW's
    # `_fail`, so an unrepaired refusal here would name a command the operator did
    # not run. That matters most in the one failure this report is documented as
    # unable to enter: a seeded lesson whose cited retro was renamed or whose
    # `recurrence-class:` tag was edited away -- the freeze hazard
    # `seed_lesson_transitions.py` describes -- where the surface named in the
    # message is the operator's only lead.
    try:
        payload = _preview._load_validated_ledger(repo_root, output_dir, summary_path)
        index = _index.build_lesson_selection_index(
            repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
        )
        rows = _preview._candidate_rows(index, payload["lessons"])
    except ValueError as exc:
        raise ValueError(f"lesson lifecycle review cannot render: {exc}") from exc
    # The next free lifecycle sequence, so an emitted `--event-id` is unique
    # against everything the ledger already holds.
    lifecycle_sequence = len(payload.get("lifecycle_events") or []) + 1
    anchors = _anchors_by_lesson(payload)
    recurrence = _recurrence_by_lesson(index)
    reviewed = []
    for row in rows:
        events = anchors.get(row["lesson_id"], [])
        anchored = [event for event in events if "anchor" in event]
        reviewed.append(
            {
                "lesson_id": row["lesson_id"],
                "lesson": row["lesson"],
                "state": row["state"],
                "score_total": row["score_total"],
                "score_count": row["score_count"],
                "value": round(_preview._value(row), 4),
            # The discriminator, first among the evidence fields.
                "evidence": _evidence_state(len(anchored), len(events)),
                "anchored_score_count": len(anchored),
                "score_events": events,
            # Context, and labelled as context by the key name it sits under.
                "recurrence_context": recurrence.get(row["lesson_id"], {}),
            # The move, runnable. Without this the report briefed a judgment
            # whose only execution path lived in a test file.
                "lifecycle_command_templates": _lifecycle_commands(
                    repo_root, row["lesson_id"], row["state"], lifecycle_sequence
                ),
            # Absent rather than null when the two-session floor is unmet, so
            # a present key means "proposable now" instead of "someone forgot
            # to fill this in".
                **(
                    {"graduation_command_template": graduation}
                    if (
                        graduation := _graduation_command(
                            repo_root,
                            row["lesson_id"],
                            events,
                            payload["lessons"][row["lesson_id"]]["source_retro"],
                        )
                    )
                    else {}
                ),
            }
        )
    # Anchored lessons first, then by exposure, then slug. NOT by recurrence: a
    # report ordered by recurrence proposes on recurrence no matter what its prose
    # says, because the top of the list is what gets read. And no longer
    # WHOLLY sign-blind: the retired key went straight from anchored count to
    # exposure count, so nothing about direction entered the ordering at any
    # level. `by_disposition` below is what a reader consults for "which lessons
    # failed"; this ordering leads with failures WITHIN each anchored tier.
    reviewed.sort(key=review_sort_key)
    without_anchors = [item["lesson_id"] for item in reviewed if item["evidence"] != "anchored"]
    return {
        "kind": "charness.lesson-lifecycle-review",
        "schema_version": 1,
        "lesson_count": len(reviewed),
        "active_count": sum(item["state"] == "active" for item in reviewed),
        "archived_count": sum(item["state"] == "archived" for item in reviewed),
        "anchored_lesson_count": len(reviewed) - len(without_anchors),
        # The denominator, stated. `anchored=3` means nothing without it, and the
        # repo has already recorded one green verdict rendered over a loop that had
        # never closed.
        "lessons_without_anchored_evidence": without_anchors,
        "dispositions": dict(DISPOSITIONS),
        # THE ANSWER TO THE QUESTION QUALITY ACTUALLY ASKS, as a grouping with no
        # ordering heuristic in it: "which lessons have a `read-but-not-applied`
        # encounter" is a lookup, not an inference from a rank. A lesson appears
        # under every disposition it has evidence for, because a lesson can be
        # both working for one author and mis-worded for another, and collapsing
        # that to one winner is the judgement this report refuses to make.
        "by_disposition": _by_disposition(reviewed),
        "non_claims": list(NON_CLAIMS),
        "lessons": reviewed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    review = build_lifecycle_review(args.repo_root.resolve())
    # The prose renderer carried nothing the review does not: `dispositions` and
    # `non_claims` are payload keys, and its only editorial line ("recurrence cannot
    # tell these apart") restated the `dispositions` mapping it printed.
    emit_yaml(review)
    # Zero over any ledger this could validate, INCLUDING one with nothing to
    # propose: a nonzero exit there would make an unproposed graduation look like a
    # failure and turn a briefing surface into a gate the contract did not
    # authorize. It is not "always zero" -- the entrypoint below still exits 1 when
    # the ledger cannot be read or replayed, which is a refusal to render rather
    # than a finding about a lesson. The distinction is the declared contract in
    # the catalog trust_model, so keep the two in step.
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
