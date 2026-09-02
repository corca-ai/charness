#!/usr/bin/env python3
"""Run all repo-owned mutation summary checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
_mutation_score = import_repo_module(__file__, "scripts.mutation.check_mutation_score")
_js_mutation_score = import_repo_module(__file__, "scripts.mutation.check_js_mutation_score")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def run(module, repo_root: Path) -> int:
    previous_argv = sys.argv
    sys.argv = [str(module.__file__), "--repo-root", str(repo_root)]
    try:
        return int(module.main())
    finally:
        sys.argv = previous_argv


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    cosmic_rc = run(_mutation_score, repo_root)
    js_rc = run(_js_mutation_score, repo_root)
    return cosmic_rc or js_rc


if __name__ == "__main__":
    raise SystemExit(main())
