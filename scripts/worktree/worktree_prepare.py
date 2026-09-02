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

_lib = import_repo_module(__file__, "scripts.worktree.worktree_doctor_lib")
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
