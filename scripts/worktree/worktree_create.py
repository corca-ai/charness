#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.worktree.worktree_create_lib")
run_create = _lib.run_create
PASS = _lib.PASS
WARN = _lib.WARN


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a git worktree through Charness, then run readiness doctor and optional prepare."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--path", type=Path, required=True, help="Path for the new git worktree.")
    parser.add_argument("--branch", help="Create a new local branch for the worktree.")
    parser.add_argument("--base", help="Base ref passed to `git worktree add` after the path.")
    parser.add_argument("--detach", action="store_true", help="Create a detached-HEAD worktree.")
    parser.add_argument(
        "--prepare", action="store_true", help="Run `charness worktree prepare` after creation."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned git command without creating the worktree.",
    )
    parser.add_argument("--force", action="store_true", help="Pass --force to `git worktree add`.")
    lifetime = parser.add_mutually_exclusive_group()
    lifetime.add_argument(
        "--ephemeral",
        action="store_true",
        help="Mark the worktree disposable: create reclaims expired leftovers and caps residue.",
    )
    lifetime.add_argument(
        "--owned",
        action="store_true",
        help="Keep the worktree until `charness worktree cleanup`; never auto-removed.",
    )
    args = parser.parse_args()

    payload = run_create(
        args.repo_root,
        target_path=args.path,
        branch=args.branch,
        base=args.base,
        detach=args.detach,
        prepare=args.prepare,
        dry_run=args.dry_run,
        force=args.force,
        ephemeral=args.ephemeral,
        owned=args.owned,
    )
    emit_yaml(payload)
    if payload.get("status") == PASS:
        return 0
    if payload.get("status") == WARN:
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
