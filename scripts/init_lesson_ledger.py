#!/usr/bin/env python3
"""Create the opt-in empty lesson ledger so the lesson lifecycle is reachable.

Every lesson-lifecycle entry point — `validate_lesson_ledger`, `declare_session`,
`record_lesson_score`, `record_lesson_lifecycle`, `render_lesson_selection_preview`
— requires `charness-artifacts/retro/lesson-ledger.json` to already exist, and
nothing created it. A repo that adopted charness after the ledger landed had the
*reporting* half of the lifecycle (`recent-lessons.md`, the selection index,
regenerated on every retro) and no path at all to the *evaluating* half. This is
that path, and it is deliberately an explicit opt-in rather than a side effect of
`seed_retro_memory.py` or `persist_retro_artifact.py`: declaring an evaluator is a
repo-level commitment that turns on a per-retro disposition duty, so it is a
command an operator runs, not something a retro does to them.

What this does NOT do, and why:

- It does not seed transitions from the selection index. `_replay_transitions`
  rebuilds `available_sources` LIVE from `charness-artifacts/retro/*.md` on every
  validation, so a committed seeded transition breaks UNREPAIRABLY (transitions
  are append-only; the only withdrawal is an `archive` lifecycle event) the moment
  its cited retro is renamed or its `recurrence-class:` tag is edited away. The
  empty ledger has no such coupling to mutable files.
- It therefore does not pretend the lifecycle is *finished* by being reachable. An
  empty ledger clears the `FileNotFoundError` and nothing else: `declare_session`
  still refuses over an empty selection until at least one lesson is seeded. The
  receipt below says so in as many words, because converting a loud failure into a
  silent permanent one would be a worse honesty position than the missing file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")
# One sentence, one owner. The SessionStart lesson block prints this same next
# step when a repo has opted in but the preview selects 0 lessons, and that block
# runs inside a host hook, so the sentence is BUILT by the stdlib-only module and
# imported HERE rather than the reverse. Two hand-written copies is how a repo
# ends up being told two different next steps for the identical state.
_hook_context = import_repo_module(__file__, "scripts.session_start_lesson_context")
_records = import_repo_module(__file__, "scripts.lesson_evaluation_records_lib")

# A function called per repo root, not a constant bound once at import: the seeder's
# runnable spelling differs between this source tree and an installed plugin inside a
# consuming repo, and a consuming repo is exactly who reads this sentence.
next_step = _hook_context.seed_lesson_next_step


def empty_ledger_payload() -> dict[str, Any]:
    """The smallest payload `replay_validated_ledger_payload` accepts.

    Built from the library's own constants rather than a literal, so a schema bump
    or a budget change cannot leave a bootstrap that emits a ledger the validator
    refuses. `lessons` is the only recomputed key and replays to `{}` here.
    """
    return {
        "kind": _ledger.KIND,
        "schema_version": _ledger.SCHEMA_VERSION,
        "transitions": [],
        "active_lesson_budget": _ledger.ACTIVE_LESSON_BUDGET,
        "lifecycle_events": [],
        "session_events": [],
        "score_events": [],
        "lessons": {},
    }


def init_lesson_ledger(*, repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, Any]:
    path = _ledger.lesson_ledger_path(output_dir)
    # Refuse rather than overwrite: the ledger is append-only and globally unique
    # in its ids forever, so replacing one with an empty file is not a reset, it is
    # the destruction of every score and lifecycle decision the repo ever recorded.
    if path.exists() or path.is_symlink():
        # Resolved, not spelled. This refusal fires when a repo runs the opt-in twice --
        # a bootstrap moment whose audience is the same freshly-opted-in consumer as the
        # next-step sentence below, and a consuming repo has no `scripts/` to run.
        raise FileExistsError(
            f"lesson ledger already exists at `{path.relative_to(repo_root)}`; it is append-only, "
            "so this refuses to overwrite it. Validate it with "
            f"`{_records.repo_or_installed_command(repo_root, 'check_lesson_ledger.py', '--repo-root', '.')}`"
            " instead."
        )
    payload = empty_ledger_payload()
    output_dir.mkdir(parents=True, exist_ok=True)
    # Validated BEFORE the write, through the real replay the gate uses. This also
    # refuses the one dangerous case a bare `not path.exists()` misses: a ledger
    # that IS committed but absent from the worktree, where an empty file would
    # silently rewrite committed transitions rather than append to them.
    _ledger.replay_validated_ledger_payload(
        repo_root=repo_root,
        output_dir=output_dir,
        summary_path=summary_path,
        path=path,
        payload=payload,
    )
    with _writer.ledger_lock(path):
        if path.exists() or path.is_symlink():
            raise FileExistsError(
                f"lesson ledger appeared at `{path.relative_to(repo_root)}` while initializing"
            )
        _writer.replace_payload(path, payload)
    return _ledger.validate_lesson_ledger(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    # The LITERAL, and this was briefly adapter-resolved before being reverted. Moving
    # the write alone flipped a consumer's floor from inert to ON-and-unsatisfiable: the
    # probe then saw a ledger and enforced the disposition duty, while `open_lesson_session`,
    # `record_lesson_score`, `check_lesson_ledger` and ~26 other entry points still opened
    # the literal path and raised. `check_lesson_ledger.py` is named in this script's own
    # FileExistsError, so the refusal path pointed at a tool that would report the ledger
    # missing. One literal across the whole subsystem is the honest state until all 30 sites
    # move together; `retro_floor_scope_lib.LESSON_LEDGER_PREFIX` records the rule.
    #
    # `summary_path` stays a separately declared adapter field, not a derivation of the
    # output dir -- retro's own adapter contract says so in as many words.
    # Through the owner, not a raw string. An earlier version of these two lines argued
    # at length that the subsystem must stay on ONE literal and then spelled a fresh copy
    # of it -- in a file that already imports `_records`, whose `retro_output_dir` is the
    # literal's owner. The comment naming the rule and the line breaking it were adjacent.
    output_dir = _records.retro_output_dir(root)
    result = init_lesson_ledger(
        repo_root=root,
        output_dir=output_dir,
        summary_path=_records.summary_path(root),
    )
    step = next_step(root)
    # Unconditional YAML. The retired receipt line was a strict projection of
    # `path`, `lesson_count`, and `transition_count`; `next_step` is the sentence
    # that says an empty ledger is not a finished lifecycle, and it has always
    # travelled in the payload rather than only in the prose.
    emit_yaml({**result, "next_step": step})
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
