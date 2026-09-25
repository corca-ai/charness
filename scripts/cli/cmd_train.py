"""Merge-train commands."""

from __future__ import annotations

import argparse
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    CharnessError,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.process import (  # noqa: E402
    _load_train_lib,
    _resolve_worktree_target,
)


def cmd_train(args: argparse.Namespace) -> int:
    repo_root = _resolve_worktree_target(args)
    if args.stats:
        if args.branches:
            raise CharnessError("train --stats takes no branches")
        return cmd_train_stats(args, repo_root)
    if not args.branches:
        raise CharnessError("train needs at least one branch (or --stats)")
    lib = _load_train_lib(args)
    payload = lib.run_train(
        repo_root,
        args.branches,
        main_ref=args.main,
        profile_path=args.profile,
    )
    emit_yaml(payload)
    # Decision-based, not status-based: `run_train` always sets `decision` to
    # one of land / land-prefix / requeue / refused, and a flat 0/1 made a
    # refused (bad input) train read as a red (verification-failed) one.
    return lib.exit_code_for_decision({"action": payload.get("decision")})


def cmd_train_stats(args: argparse.Namespace, repo_root: Path) -> int:
    from scripts.task_run import task_run_train_stats as train_stats

    try:
        window_hours = train_stats.parse_window(args.window)
    except ValueError as exc:
        raise CharnessError(str(exc)) from exc
    profile = _load_train_lib(args).load_verify_profile(repo_root, args.profile)
    payload = train_stats.train_stats_for_repo(
        repo_root,
        window_hours=window_hours,
        loosening=profile.get("loosening"),
    )
    emit_yaml(payload)
    return 0
