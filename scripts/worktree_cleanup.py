#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.worktree_cleanup_lib")
run_cleanup = _lib.run_cleanup
emit_payload = _lib.emit_payload
PASS = _lib.PASS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely remove a registered git worktree and optionally delete its merged local branch."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--path", type=Path, required=True, help="Registered worktree path to remove.")
    parser.add_argument(
        "--delete-merged-branch",
        action="store_true",
        help="Delete the local branch only after it is contained in --branch-base.",
    )
    parser.add_argument(
        "--branch-base",
        default="HEAD",
        help="Local ref that must contain the target branch before branch deletion; defaults to HEAD.",
    )
    parser.add_argument("--yes", action="store_true", help="Execute the planned cleanup. Defaults to dry-run.")
    parser.add_argument("--force", action="store_true", help="Pass --force to git worktree remove for dirty targets.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of human text.")
    args = parser.parse_args()

    payload = run_cleanup(
        args.repo_root,
        target_path=args.path,
        delete_merged_branch=args.delete_merged_branch,
        branch_base=args.branch_base,
        yes=args.yes,
        force=args.force,
    )
    emit_payload(payload, json_mode=args.json)
    return 0 if payload.get("status") == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
