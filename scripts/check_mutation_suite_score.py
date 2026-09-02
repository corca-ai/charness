#!/usr/bin/env python3
"""Run all repo-owned mutation summary checks."""

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

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
_mutation_score = import_repo_module(__file__, "scripts.check_mutation_score")
_js_mutation_score = import_repo_module(__file__, "scripts.check_js_mutation_score")


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
