#!/usr/bin/env python3
"""Run all repo-owned mutation summary checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def run(command: list[str], repo_root: Path) -> int:
    completed = subprocess.run(command, cwd=repo_root, check=False)
    return completed.returncode


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    cosmic_rc = run([sys.executable, "scripts/check_mutation_score.py", "--repo-root", str(repo_root)], repo_root)
    js_rc = run([sys.executable, "scripts/check_js_mutation_score.py", "--repo-root", str(repo_root)], repo_root)
    return cosmic_rc or js_rc


if __name__ == "__main__":
    raise SystemExit(main())
