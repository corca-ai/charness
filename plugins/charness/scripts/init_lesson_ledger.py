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
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")
# One sentence, one owner. The SessionStart lesson block prints this same next
# step when a repo has opted in but the preview selects 0 lessons, and that block
# runs inside a host hook, so the constant lives in the stdlib-only module and is
# imported HERE rather than the reverse. Two hand-written copies is how a repo
# ends up being told two different next steps for the identical state.
_hook_context = import_repo_module(__file__, "scripts.session_start_lesson_context")

NEXT_STEP = _hook_context.SEED_LESSON_NEXT_STEP


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
        raise FileExistsError(
            f"lesson ledger already exists at `{path.relative_to(repo_root)}`; it is append-only, "
            "so this refuses to overwrite it. Validate it with "
            "`python3 scripts/check_lesson_ledger.py --repo-root .` instead."
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
    parser.add_argument("--json", action="store_true", help="Emit the structured receipt instead of prose.")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    result = init_lesson_ledger(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
    )
    if args.json:
        print(json.dumps({**result, "next_step": NEXT_STEP}, ensure_ascii=False, sort_keys=True))
        return 0
    print(
        f"Created empty lesson ledger `{result['path']}`: "
        f"{result['lesson_count']} lessons, {result['transition_count']} seed transitions."
    )
    print(NEXT_STEP)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
