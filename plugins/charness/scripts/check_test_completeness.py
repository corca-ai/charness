#!/usr/bin/env python3
"""Check that standing pytest targets cover all discoverable test files.

Portable across repos: takes --repo-root and the standing targets as
positional arguments. The gate is intentionally file-target based: if a pytest
target includes a test file, every nodeid in that file is covered by the
standing run. That preserves the coverage contract without paying for duplicate
pytest collection during the quality gate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def is_pytest_file(path: Path) -> bool:
    return path.suffix == ".py" and (
        path.name.startswith("test_") or path.name.endswith("_test.py")
    )


def find_test_root(repo_root: Path) -> str | None:
    for candidate in ("tests", "test"):
        if (repo_root / candidate).is_dir():
            return candidate
    return None


def relative_test_files(repo_root: Path, root: Path) -> set[str]:
    if not root.exists():
        return set()
    if root.is_file():
        return {root.relative_to(repo_root).as_posix()} if is_pytest_file(root) else set()
    return {
        path.relative_to(repo_root).as_posix()
        for path in root.rglob("*.py")
        if path.is_file() and is_pytest_file(path)
    }


def target_files(repo_root: Path, targets: list[str]) -> set[str]:
    files: set[str] = set()
    for raw_target in targets:
        matches = (
            list(repo_root.glob(raw_target))
            if any(char in raw_target for char in "*?[")
            else [repo_root / raw_target]
        )
        for match in matches:
            files.update(relative_test_files(repo_root, match))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("targets", nargs="*", help="Standing pytest targets (files, dirs, or globs)")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    test_root = find_test_root(repo_root)
    if test_root is None:
        return 0

    all_tests = relative_test_files(repo_root, repo_root / test_root)
    if not all_tests:
        return 0

    if not args.targets:
        print("no standing targets provided; skipping completeness check", file=sys.stderr)
        return 0

    targeted_tests = target_files(repo_root, args.targets)
    missing = all_tests - targeted_tests
    if not missing:
        return 0

    print(
        f"{len(missing)} test file(s) not covered by standing pytest targets:",
        file=sys.stderr,
    )
    for path in sorted(missing):
        print(f"  {path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
