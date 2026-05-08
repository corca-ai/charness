#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.worktree_audit_lib")
run_audit = _lib.run_audit
run_prune = _lib.run_prune
render_audit_text = _lib.render_audit_text
render_prune_text = _lib.render_prune_text
emit_payload = _lib.emit_payload
PASS = _lib.PASS
WARN = _lib.WARN


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit git worktrees registered to a repository: classify primary/active/prunable/stale and optionally prune metadata."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--stale-days",
        type=int,
        default=_lib.DEFAULT_STALE_DAYS,
        help="Detached-HEAD worktrees older than this many days are reported as stale.",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="After auditing, run `git worktree prune` to drop metadata for missing worktrees.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of human text.")
    args = parser.parse_args()

    audit_payload = run_audit(args.repo_root, stale_days=args.stale_days)
    emit_payload(audit_payload, json_mode=args.json, renderer=render_audit_text)

    if audit_payload.get("status") == PASS:
        exit_code = 0
    elif audit_payload.get("status") == WARN:
        exit_code = 1
    else:
        exit_code = 2

    if args.prune and audit_payload.get("status") != "fail":
        prune_payload = run_prune(args.repo_root)
        emit_payload(prune_payload, json_mode=args.json, renderer=render_prune_text)
        if prune_payload["status"] != PASS:
            exit_code = max(exit_code, 2)
        else:
            remaining = prune_payload.get("remaining_after_prune") or {}
            if remaining.get("prunable", 0) == 0 and remaining.get("stale", 0) == 0:
                exit_code = 0
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
