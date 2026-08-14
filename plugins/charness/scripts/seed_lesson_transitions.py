#!/usr/bin/env python3
"""Append lesson-ledger seed transitions for tagged retro classes not yet seeded.

WHY THIS EXISTS (#625). `init_lesson_ledger.py` creates a valid EMPTY ledger and
deliberately seeds nothing. Every other lifecycle entry point reads seeded
lessons: `record_lesson_session.py` refuses over an empty preview,
`record_lesson_score.py` refuses an unseeded `lesson_id`, and
`render_lesson_selection_preview.py` reports `0 eligible`. So between "the ledger
file exists" and "the lifecycle runs" there was exactly one missing step, and no
command performed it -- the verifier who found this had to HAND-EDIT the
append-only ledger, which is the one thing a repo must never be asked to do
(`_committed_state` diffs the committed prefix against `git show HEAD:<path>`).

Without this, `init_lesson_ledger.py` converts a loud `FileNotFoundError` into a
silent permanent `0 eligible lessons`, which is the worse honesty position.

WHY APPENDING AND SEEDING ARE ONE COMMAND. The ledger has no separate "add a new
lesson later" operation: a transition IS how a class enters, whether the ledger is
one minute or one year old. A one-shot bootstrap seeder would have closed the cold
start and left the identical hole open for every lesson authored afterwards. This
repo demonstrates that directly -- it had 16 seeded classes and 15 tagged classes
with no path in, all authored after the ledger landed.

WHAT IT REFUSES TO DECIDE. It never invents a `recurrence-class`, never writes a
retro, and never edits a tag. A class becomes seedable only when an author tags a
retro bullet; this command is the mechanical half after that judgment, not a
substitute for it.

THE FREEZE RISK, STATED IN THE RECEIPT. `_replay_transitions` re-derives
`available_sources` LIVE from `charness-artifacts/retro/*.md` on every validation,
and transitions are append-only with archive as the only withdrawal. So a
committed transition breaks UNREPAIRABLY if its cited retro is later renamed or
its tag edited away. This command therefore lands its result in the worktree and
says so: the human inspects before the commit that freezes it. That is also why
there is no `--auto-commit` and why `--dry-run` exists.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")
_index = import_repo_module(__file__, "scripts.recent_lessons_lib")
_records = import_repo_module(__file__, "scripts.lesson_evaluation_records_lib")

# Same prefix the 16 hand-authored transitions already use, so a reader cannot
# tell a bootstrap seed from a later append -- correctly, because the ledger draws
# no distinction between them either.
TRANSITION_ID_PREFIX = "seed-"

FREEZE_NOTE = (
    "Seeded transitions are in the worktree, not committed. Validation rebuilds each "
    "citation from `charness-artifacts/retro/*.md` on every run, and transitions are "
    "append-only, so once committed a transition breaks unrepairably if its cited retro "
    "is renamed or its `recurrence-class:` tag is removed. Inspect the cited retros before "
    "committing."
)


def _fail(message: str) -> None:
    raise ValueError(f"seed lesson transitions: {message}")


def _candidate_seeds(repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, str]:
    """Every tagged class mapped to the ONE retro a transition should cite.

    `latest_source_path`, with the trade stated honestly. It is the source the
    digest renders the lesson's wording and section from, so at the moment of
    seeding the ledger cites the artifact whose text a reader is actually shown.

    That alignment EXPIRES. The digest recomputes `latest_source_path` live on
    every build while the ledger's citation is frozen forever, so the next time the
    class recurs the digest quotes a retro the ledger does not name. This repo
    already shows it: transition 1 cites the 08-11 retro while
    `guard-adjacent-to-action` has since recurred in the 08-13 one.

    The alternative was the OLDEST source, which the validator accepts equally
    (`_replay_transitions` takes any member of the source set) and which binds the
    permanent record to a historical artifact less likely to be edited later. It
    was not chosen, because a citation a reader cannot connect to the text they
    were shown is harder to audit than one that ages. Recorded rather than
    re-litigated: transitions are append-only, so this choice is not revisable for
    already-seeded classes.
    """
    index = _index.build_lesson_selection_index(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )
    return {
        candidate["recurrence_class"]: str(candidate["latest_source_path"])
        for candidate in index["candidates"]
        if isinstance(candidate.get("recurrence_class"), str) and candidate["recurrence_class"]
    }


def plan_seeds(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
    payload: dict[str, Any],
    lesson_ids: list[str] | None,
) -> list[dict[str, Any]]:
    """The transitions that WOULD be appended, in deterministic slug order.

    Pure: it reads state and returns records. `--dry-run` and the write path call
    this same function, so the plan a human inspects is the plan that gets written
    rather than a second rendering that can drift from it.
    """
    available = _candidate_seeds(repo_root, output_dir, summary_path)
    seeded = set(payload.get("lessons") or {})
    existing_ids = {
        transition.get("transition_id")
        for transition in payload.get("transitions") or []
        if isinstance(transition, dict)
    }
    if lesson_ids is None:
        targets = sorted(set(available) - seeded)
    else:
        targets = []
        for lesson_id in lesson_ids:
            if lesson_id not in available:
                _fail(
                    f"`{lesson_id}` is not a tagged retro class; {_ledger.RECURRENCE_TAG_INSTRUCTION}. "
                    "Tag a retro bullet first -- this command never invents a class."
                )
            if lesson_id in seeded:
                _fail(f"`{lesson_id}` is already seeded; a lesson_id enters the ledger exactly once")
            if lesson_id not in targets:
                targets.append(lesson_id)
        targets.sort()
    plan: list[dict[str, Any]] = []
    sequence = len(payload.get("transitions") or [])
    for lesson_id in targets:
        transition_id = f"{TRANSITION_ID_PREFIX}{lesson_id}"
        # transition_ids are globally unique FOREVER, and archive does not free one.
        # Caught here rather than left to the validator so the refusal names the
        # collision instead of reporting a generic duplicate after a partial plan.
        if transition_id in existing_ids:
            _fail(
                f"transition_id `{transition_id}` is already used by a different lesson; "
                "transition ids are unique forever and archiving does not release one"
            )
        existing_ids.add(transition_id)
        sequence += 1
        plan.append(
            {
                "sequence": sequence,
                "transition_id": transition_id,
                "lesson_id": lesson_id,
                "source_retro": available[lesson_id],
            }
        )
    return plan


def seed_transitions(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
    lesson_ids: list[str] | None,
    dry_run: bool,
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    path = _ledger.lesson_ledger_path(output_dir)
    if not path.is_file():
        # Resolved, not spelled: a consuming repo has no `scripts/` of its own, and
        # naming one here would answer "the ledger is missing" with a command the
        # reader cannot run -- the #624 class, at the one moment the reader is
        # certainly bootstrapping.
        raise FileNotFoundError(
            f"missing lesson ledger `{path.relative_to(repo_root)}`; create it with "
            f"`{_records.repo_or_installed_command(repo_root, 'init_lesson_ledger.py', '--repo-root', '.')}`"
            " first"
        )
    with _writer.ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        # Validate the CURRENT ledger before planning against it: planning over a
        # ledger that is already invalid would append onto a state no later run can
        # replay, and the refusal would then name this command's transition rather
        # than the pre-existing damage.
        replayed = _ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=payload,
        )
        plan = plan_seeds(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            payload=payload,
            lesson_ids=lesson_ids,
        )
        active = sum(lesson["state"] == "active" for lesson in replayed.values())
        # Pre-checked so an over-budget request names the arithmetic. The validator
        # refuses this too; it just cannot say how many the caller asked for.
        if active + len(plan) > _ledger.ACTIVE_LESSON_BUDGET:
            _fail(
                f"seeding {len(plan)} would put {active + len(plan)} lessons active, past the fixed "
                f"budget of {_ledger.ACTIVE_LESSON_BUDGET}; archive lessons with "
                "`record_lesson_lifecycle.py` or seed a subset with `--lesson-id`"
            )
        receipt = {
            "seeded": [dict(transition) for transition in plan],
            "seeded_count": len(plan),
            "already_seeded_count": len(replayed),
            "active_lesson_count": active + len(plan),
            "dry_run": dry_run,
            "path": str(path.relative_to(repo_root)),
        }
        if dry_run or not plan:
            # No write, and `dry_run` stays as asked: an empty plan under a real run
            # is "nothing to seed", not a dry run, and conflating them would let a
            # receipt claim a rehearsal that never happened.
            return receipt
        candidate = copy.deepcopy(payload)
        candidate["transitions"].extend(plan)
        candidate["lessons"] = _replayable_lessons(plan, replayed)
        # The whole candidate goes through the real replay before it can reach disk,
        # so every refusal leaves the ledger bytes unchanged.
        _ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=candidate,
        )
        _writer.replace_payload(path, candidate)
    return receipt


def _replayable_lessons(
    plan: list[dict[str, Any]], replayed: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """The materialized view the appended transitions imply, before revalidation.

    A seeded lesson starts at zero scores in `active` state; `_replay_transitions`
    builds exactly this shape. Constructed here rather than trusted, so the
    validator's `lessons != replayed` check still has something independent to
    disagree with -- handing it the replay output directly would make that check
    tautological.
    """
    lessons = copy.deepcopy(replayed)
    for transition in plan:
        lessons[transition["lesson_id"]] = {
            "source_retro": transition["source_retro"],
            "transition_id": transition["transition_id"],
            "score_total": 0,
            "score_count": 0,
            "state": "active",
            "last_lifecycle_event_id": None,
        }
    return lessons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--lesson-id",
        action="append",
        dest="lesson_ids",
        help="Seed only this tagged recurrence class; repeatable. Default seeds every unseeded class.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the transitions that would be appended without writing the ledger.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the structured receipt instead of prose.")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    receipt = seed_transitions(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
        lesson_ids=args.lesson_ids,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps({**receipt, "freeze_note": FREEZE_NOTE}, ensure_ascii=False, sort_keys=True))
        return 0
    if not receipt["seeded"]:
        print(
            f"No unseeded tagged classes: {receipt['already_seeded_count']} lessons already in "
            f"`{receipt['path']}`. {_ledger.RECURRENCE_TAG_INSTRUCTION}."
        )
        return 0
    verb = "Would seed" if receipt["dry_run"] else "Seeded"
    print(f"{verb} {receipt['seeded_count']} transition(s) into `{receipt['path']}`:")
    for transition in receipt["seeded"]:
        print(f"  {transition['lesson_id']} <- {transition['source_retro']}")
    print(f"{receipt['active_lesson_count']} of {_ledger.ACTIVE_LESSON_BUDGET} lessons active.")
    # Printed on BOTH paths. The dry run is the inspection moment this command's
    # whole mitigation rests on, so gating the warning on the write meant it
    # arrived only after the bytes it was warning about had landed.
    print(FREEZE_NOTE)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
