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

_lib = import_repo_module(__file__, "scripts.worktree.worktree_audit_lib")
run_audit = _lib.run_audit
run_prune = _lib.run_prune
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
        help="After auditing, reclaim expired ephemeral worktrees and prune metadata for missing ones.",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Run readiness doctor for existing worktrees and include per-worktree readiness summaries.",
    )
    args = parser.parse_args()

    audit_payload = run_audit(
        args.repo_root, stale_days=args.stale_days, include_doctor=args.doctor
    )
    output: dict[str, object] = {"audit": audit_payload}

    if audit_payload.get("status") == PASS:
        exit_code = 0
    elif audit_payload.get("status") == WARN:
        exit_code = 1
    else:
        exit_code = 2

    if args.prune and audit_payload.get("status") != "fail":
        prune_payload = run_prune(args.repo_root)
        output["prune"] = prune_payload
        if prune_payload["status"] != PASS:
            exit_code = max(exit_code, 2)
        else:
            remaining = prune_payload.get("remaining_after_prune") or {}
            if remaining.get("prunable", 0) == 0 and remaining.get("stale", 0) == 0:
                exit_code = 0
    emit_yaml(output)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
