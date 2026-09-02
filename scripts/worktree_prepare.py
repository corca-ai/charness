#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.worktree_doctor_lib")
run_prepare = _lib.run_prepare
PASS = _lib.PASS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the worktree adapter's prepare commands and re-validate readiness."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run prepare even if doctor already reports pass.",
    )
    args = parser.parse_args()

    payload = run_prepare(args.repo_root, force=args.force)
    emit_yaml(payload)
    return 0 if payload.get("status") == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
