#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.worktree_audit_lib")
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
        help="After auditing, run `git worktree prune` to drop metadata for missing worktrees.",
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
    emit_yaml(audit_payload)

    if audit_payload.get("status") == PASS:
        exit_code = 0
    elif audit_payload.get("status") == WARN:
        exit_code = 1
    else:
        exit_code = 2

    if args.prune and audit_payload.get("status") != "fail":
        prune_payload = run_prune(args.repo_root)
        # A prune run emits a SECOND payload on the same stdout. Two YAML mappings
        # concatenated are not one document, so the explicit `---` start marker keeps
        # the stream readable with `yaml.safe_load_all`; without it a --prune run
        # would print output no YAML reader could parse.
        print("---")
        emit_yaml(prune_payload)
        if prune_payload["status"] != PASS:
            exit_code = max(exit_code, 2)
        else:
            remaining = prune_payload.get("remaining_after_prune") or {}
            if remaining.get("prunable", 0) == 0 and remaining.get("stale", 0) == 0:
                exit_code = 0
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
