#!/usr/bin/env python3
"""Create the opt-in empty lesson ledger for durable lesson memory and selection.

The ledger is deliberately explicit rather than a side effect of
`seed_retro_memory.py` or `persist_retro_artifact.py`: it is durable repo state
and must never appear because a setup or retro command happened to run. This
command creates only the empty ledger; later transitions are still derived from
tagged retro lessons and validated append-only.

What this does NOT do, and why:

- It does not seed transitions from the selection index. `_replay_transitions`
  rebuilds `available_sources` LIVE from `charness-artifacts/retro/*.md` on every
  validation, so a committed seeded transition breaks UNREPAIRABLY the moment its
  cited retro is renamed or its `recurrence-class:` tag is edited away. The empty
  ledger has no such coupling to mutable files.
- It initializes ledger state only; it does not create a second lesson-memory
  artifact. The ledger remains the memory/selection surface.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lessons.lesson_ledger_lib")
_writer = import_repo_module(__file__, "scripts.lessons.lesson_ledger_writer_lib")
_commands = import_repo_module(__file__, "scripts.lessons.lesson_command_citation")
_retro = import_repo_module(__file__, "scripts.retro_debug.retro_output_dir_lib")


def seed_lesson_next_step(repo_root: Path) -> str:
    """Explain the explicit next step for an empty, newly-created ledger.

    Keep the one-time seed guidance at this explicit opt-in boundary instead of
    coupling ledger initialization to a host lifecycle event.
    """
    seed_command = _commands.repo_or_installed_command(
        repo_root, "seed_lesson_transitions.py", "--repo-root", "."
    )
    return (
        "Next: a lesson enters the ledger only from a retro bullet tagged "
        "`recurrence-class: <slug>`; tag one, then append its seed transition with "
        f"`{seed_command} --dry-run` to inspect and the same command without "
        "`--dry-run` to write."
    )


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
            f"`{_commands.repo_or_installed_command(repo_root, 'check_lesson_ledger.py', '--repo-root', '.')}`"
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
    output_dir = _retro.retro_output_dir(root)
    result = init_lesson_ledger(
        repo_root=root,
        output_dir=output_dir,
        summary_path=_retro.retro_summary_path(root),
    )
    step = seed_lesson_next_step(root)
    # Unconditional YAML. `next_step` carries the one useful follow-up for an
    # empty memory ledger without creating a session or retro-closeout contract.
    emit_yaml({**result, "next_step": step})
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
