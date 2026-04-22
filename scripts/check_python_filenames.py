#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VALID_NAME_RE = re.compile(r"^(?:__init__|[a-z][a-z0-9_]*)\.py$")
SKIP_DIR_NAMES = {".git", ".venv", ".pytest_cache", "__pycache__", "node_modules"}
SKIP_PATH_PARTS = {"vendor"}


def iter_python_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*.py"):
        rel_path = path.relative_to(repo_root)
        if any(part in SKIP_DIR_NAMES for part in rel_path.parts):
            continue
        if any(part in SKIP_PATH_PARTS for part in rel_path.parts):
            continue
        files.append(rel_path)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    invalid = [path for path in iter_python_files(repo_root) if not VALID_NAME_RE.fullmatch(path.name)]
    if not invalid:
        return 0

    print("Python filenames must use snake_case outside vendor paths:", file=sys.stderr)
    for path in invalid:
        print(f"- {path.as_posix()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
