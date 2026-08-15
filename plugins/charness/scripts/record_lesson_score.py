#!/usr/bin/env python3
"""Append one cited lesson score without bypassing the ledger validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
lesson_ledger_path = _ledger.lesson_ledger_path
replay_validated_ledger_payload = _ledger.replay_validated_ledger_payload
candidate_sources = _ledger.candidate_sources
# The ONE writer, and the reason the legacy-scalar shape can never come back:
# `legacy_prefix_error` refuses a scalar appended after any outcome event, and
# this refuses to author one at all. Neither alone is enough -- the validator
# cannot stop a hand edit that predates the first outcome event, and a writer
# rule alone would not survive someone editing the JSON directly.
_outcome = import_repo_module(__file__, "scripts.lesson_score_outcome_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")
ledger_lock = _writer.ledger_lock
replace_payload = _writer.replace_payload


def _fail(message: str) -> None:
    raise ValueError(f"record lesson score: {message}")


def _nonblank(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        _fail(f"{name} must be a non-empty non-whitespace string")
    return stripped


def append_score(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
    event_id: str,
    session_id: str,
    lesson_id: str,
    source_retro: str,
    outcome: str,
    anchor: str,
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    event_id = _nonblank(event_id, "event_id")
    lesson_id = _nonblank(lesson_id, "lesson_id")
    session_id = _nonblank(session_id, "session_id")
    source_retro = _nonblank(source_retro, "source_retro")
    anchor = _nonblank(anchor, "anchor")
    if outcome not in _outcome.SCORE_OUTCOMES:
        # The refusal carries the QUESTIONS, not just the legal values: an author
        # picking between `read-but-not-applied` and `not-consulted` from the
        # slugs alone is guessing, and guessing is what collapses the split the
        # vocabulary exists to make.
        legal = "; ".join(
            f"`{value}` -- {_outcome.OUTCOME_QUESTIONS[value]}"
            for value in sorted(_outcome.SCORE_OUTCOMES)
        )
        _fail(f"outcome must be one of: {legal}")
    # Refused HERE rather than at replay, because this is where the author still
    # remembers the counterfactual. A refusal at gate time arrives after the
    # session that could have answered it is over.
    anchor_error = _outcome.anchor_shape_error(outcome, anchor)
    if anchor_error is not None:
        _fail(anchor_error)
    if not _outcome.canonical_retro_citation(source_retro):
        _fail(
            f"source_retro must be a repo-relative `{_outcome.RETRO_DIR}/<name>.md` path naming the "
            "retro that RECORDS this encounter -- this session's own retro, not the lesson's origin"
        )
    path = lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    with ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        replayed = replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=payload,
        )
        if lesson_id not in replayed:
            _fail(f"lesson_id `{lesson_id}` is unseeded")
        # REFUSED HERE, not only at the gate, because the ledger is append-only:
        # `replay_validated_ledger_payload` refuses to rewrite a committed score
        # event, so a `not-consulted` encounter that fails the reconciler's
        # precondition after commit is a permanently red gate whose only escape is
        # to add the recurrence tag afterwards -- i.e. to assert the recurrence in
        # order to clear the check that verifies it, which is verbatim the defect
        # this vocabulary exists to remove. A bounded reviewer found that trap; the
        # inputs were already on this call path, so refusing costs nothing.
        # SAME REASON, second check. Round 2 found that `duplicate-encounter` --
        # added in round 1 to close the legacy double-count hole -- shipped the
        # very class its neighbour below was written to remove: a post-persistence
        # refusal with no write-time counterpart, on an append-only ledger. The
        # reachable case is a legacy event and an outcome event for one lesson in
        # one session; their `source_retro` values differ, so `(source, lesson)`
        # uniqueness accepts both, and the gate then goes permanently red.
        if any(
            event.get("session_id") == session_id and event.get("lesson_id") == lesson_id
            for event in payload["score_events"]
        ):
            _fail(
                f"session `{session_id}` already records an encounter for `{lesson_id}`; score what "
                "actually bit, one cited event each. A second encounter for the same lesson in the "
                "same session cannot be reconciled against any retro's declared count"
            )
        if outcome in _outcome.RECURRENCE_ASSERTING_OUTCOMES:
            sources = _ledger.candidate_sources(repo_root, output_dir, summary_path)
            if source_retro not in sources.get(lesson_id, set()):
                _fail(
                    f"`{outcome}` asserts that this session COMMITTED the class `{lesson_id}`, so "
                    f"`{source_retro}` must already carry a `recurrence-class: {lesson_id}` bullet "
                    "under one of its Context / Waste / Next Improvements sections. Write that "
                    "bullet first, then record the encounter -- without the precondition this "
                    "outcome is trivially true of every lesson the session had no occasion to use"
                )
        candidate = copy.deepcopy(payload)
        event: dict[str, Any] = {
            "event_id": event_id,
            "session_id": session_id,
            "source_retro": source_retro,
            "lesson_id": lesson_id,
            "outcome": outcome,
            "anchor": anchor,
        }
        candidate["score_events"].append(event)
        candidate["lessons"] = replayed
        lesson = candidate["lessons"][lesson_id]
        lesson["score_total"] += _outcome.valence(event)
        lesson["score_count"] += 1
        lesson["outcome_counts"][outcome] += 1
        replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=candidate,
        )
        replace_payload(path, candidate)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--lesson-id", required=True)
    parser.add_argument(
        "--source-retro",
        required=True,
        help="repo-relative path of the retro RECORDING this encounter (this session's own retro)",
    )
    parser.add_argument(
        "--outcome",
        required=True,
        choices=sorted(_outcome.SCORE_OUTCOMES),
        help="; ".join(
            f"{value}: {question}" for value, question in sorted(_outcome.OUTCOME_QUESTIONS.items())
        ),
    )
    # Required, not optional: with magnitude gone there is no unanchored tier
    # left to fall back to. One fewer rule, one more obligation.
    parser.add_argument("--anchor", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    event = append_score(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
        event_id=args.event_id,
        session_id=args.session_id,
        lesson_id=args.lesson_id,
        source_retro=args.source_retro,
        outcome=args.outcome,
        anchor=args.anchor,
    )
    # Receipt only; `append_score` already persisted the event in the JSON ledger.
    emit_yaml(event)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
