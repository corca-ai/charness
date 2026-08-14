#!/usr/bin/env python3
"""Render read-only lesson-lifecycle evidence for the surface the spec put in charge.

WHY THIS EXISTS (#626). `2026-08-12-lesson-ledger-and-contract-register.md:106-111`
splits the roles by what each surface can see: `retro` scores and cites because it
sees one session, and `quality` reads the candidate list and PROPOSES because "can
this be a validator instead of prose" is its own question and contract changes
already route through it. That assignment was never wired. The mechanics landed --
`record_lesson_lifecycle.py`, `record_contract_graduation_proposal.py`,
`apply_contract_transition.py` all exist and all validate -- with test-only
callers, and `skills/public/quality/SKILL.md` did not mention lessons at all, so
the surface named as owner had no idea it owned anything.

THE FAILURE MODE THIS IS DESIGNED AGAINST, stated in #626's own ordering comment.
A high-recurrence lesson is in one of three states, and RECURRENCE COUNT CANNOT
TELL THEM APART:

  - should have been a gate, stayed prose        -> graduate
  - wrong form: origin-incident vocabulary       -> rewrite in place
  - form is fine, it was simply not consulted    -> strengthen the binding

Proposing on recurrence selects the LOUDEST lesson rather than the one whose PROSE
is the problem. The discriminator is the ANCHOR -- the ledger contract requires one
at score magnitude >= 2 precisely because it names "a concrete moment in the
session where the lesson changed or failed to change an action". Recurrence says
something is wrong; the anchor says what. So this report leads with anchors, orders
by anchored evidence, and reports recurrence as context explicitly labelled as the
loud signal rather than the ranking key.

WHAT THIS DELIBERATELY DOES NOT DO.

- It does not classify a lesson into one of the three dispositions. That is a
  content judgment, and the ledger contract's `Deliberately Not Doing` keeps
  content classification out of these surfaces on purpose: a classifier rots
  exactly like the prose it would replace.
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

ROOT = repo_root_from_script(__file__)
# Reused, never reimplemented: `_value` is the same shrinkage statistic the
# selection preview ranks its value bucket with. A second copy here would let
# quality's "high value" and the preview's "high value" drift apart silently,
# which is the one disagreement this report must not introduce.
_preview = import_repo_module(__file__, "scripts.lesson_selection_preview_lib")
_index = import_repo_module(__file__, "scripts.recent_lessons_lib")

# The judgment quality owes, named rather than computed. Recorded here so the
# report briefs the decision instead of leaving a reader to rediscover the
# taxonomy from an issue comment.
DISPOSITIONS = {
    "graduate": (
        "should have been a gate and stayed prose -- propose it with "
        "`record_contract_graduation_proposal.py`, which requires two distinct evidence "
        "sessions and a named displacement"
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
    """Every score event's anchor, kept with its score and citing retro.

    The anchor without its score is unreadable -- `+3 "the fresh-eye round caught
    two overclaims"` and `-3 "the fresh-eye round caught two overclaims"` would
    render identically -- so the three travel together.
    """
    anchors: dict[str, list[dict[str, Any]]] = {}
    for event in payload.get("score_events") or []:
        if not isinstance(event, dict):
            continue
        lesson_id = event.get("lesson_id")
        if not isinstance(lesson_id, str):
            continue
        anchors.setdefault(lesson_id, []).append(
            {
                "score": event.get("score"),
                "source_retro": event.get("source_retro"),
                "session_id": event.get("session_id"),
                # Absent rather than empty: the contract permits an unanchored score
                # at magnitude <= 1, and rendering `""` would read as a blank anchor
                # someone forgot to fill in.
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
            }
        )
    # Anchored lessons first, then by exposure, then slug. NOT by recurrence: a
    # report ordered by recurrence proposes on recurrence no matter what its prose
    # says, because the top of the list is what gets read.
    reviewed.sort(
        key=lambda item: (
            -item["anchored_score_count"],
            -item["score_count"],
            item["lesson_id"],
        )
    )
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
        "non_claims": list(NON_CLAIMS),
        "lessons": reviewed,
    }


def _render_human(review: dict[str, Any]) -> str:
    lines = [
        f"Lesson lifecycle review: {review['lesson_count']} lessons "
        f"({review['active_count']} active, {review['archived_count']} archived); "
        f"{review['anchored_lesson_count']} with anchored evidence.",
        "",
    ]
    for item in review["lessons"]:
        lines.append(
            f"- {item['lesson_id']} [{item['state']}] evidence={item['evidence']} "
            f"score={item['score_total']}/{item['score_count']} value={item['value']} "
            f"independent_sources={item['recurrence_context'].get('independent_source_count')}"
        )
        for event in item["score_events"]:
            if "anchor" in event:
                lines.append(f"    {event['score']:+d} anchor: {event['anchor']}")
    lines.extend(
        [
            "",
            f"No anchored evidence ({len(review['lessons_without_anchored_evidence'])}): "
            + (", ".join(review["lessons_without_anchored_evidence"]) or "none"),
            "",
            "Dispositions to judge (recurrence cannot tell these apart):",
        ]
    )
    lines.extend(f"- {name}: {why}" for name, why in review["dispositions"].items())
    lines.append("")
    lines.extend(f"Not claimed: {claim}" for claim in review["non_claims"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="Emit the structured review instead of prose.")
    args = parser.parse_args()
    review = build_lifecycle_review(args.repo_root.resolve())
    if args.json:
        print(json.dumps(review, ensure_ascii=False, sort_keys=True))
    else:
        print(_render_human(review))
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
