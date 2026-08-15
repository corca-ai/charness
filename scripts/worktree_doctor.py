#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.worktree_doctor_lib")
run_doctor = _lib.run_doctor
PASS = _lib.PASS


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a git worktree's readiness for mutate-phase work.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--require-isolation",
        action="store_true",
        help=(
            "Fail unless this checkout is a linked worktree rather than the main one. Pass it "
            "before handing a WRITE-CAPABLE agent a checkout: without isolation that agent "
            "shares the parent's tree and index, and a stray git op lands in the parent's "
            "commit. Without the flag, isolation is reported as a fact and never enforced."
        ),
    )
    args = parser.parse_args()

    payload = run_doctor(args.repo_root, require_isolation=args.require_isolation)
    emit_yaml(payload)
    return 0 if payload.get("status") == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
