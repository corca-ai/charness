"""The goal-locating CLI surface every achieve helper shares.

`--repo-root / --goal-path / --slug / --date` and the resolution rule behind them
were written out per script. Two copies is where a rule starts drifting: one script
learning a new selector, or a changed refusal message, silently makes the two
disagree about which file "the goal" means. This is the one statement.

It lives beside the helpers rather than in `goal_artifact_lib` because `SystemExit`
and `argparse` are CLI concerns; the library stays importable by anything.
"""
from __future__ import annotations

import argparse
from datetime import date as date_cls
from pathlib import Path


def add_goal_target_args(parser: argparse.ArgumentParser) -> None:
    """The four flags that name a goal artifact, identically in every helper."""
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--goal-path", type=Path, help="Explicit path to the goal artifact (overrides --slug/--date)")
    parser.add_argument("--slug", help="Goal slug, used with --date to locate the artifact")
    parser.add_argument("--date", default=date_cls.today().isoformat(), help="Goal date prefix YYYY-MM-DD used with --slug")


def resolve_goal_path(args, goal_lib) -> Path:
    """`--goal-path` wins; otherwise `--slug` + `--date`. Refuses rather than guessing.

    ``goal_lib`` is injected so this module stays free of the library's import cost
    and its callers keep loading it their own way.
    """
    repo_root = args.repo_root.expanduser().resolve()
    if args.goal_path is not None:
        return args.goal_path.expanduser().resolve()
    if not (args.slug and args.date):
        raise SystemExit("provide --goal-path, or both --slug and --date")
    try:
        return goal_lib.goal_path(repo_root, args.date, args.slug)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
