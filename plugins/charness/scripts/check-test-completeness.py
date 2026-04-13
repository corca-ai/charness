#!/usr/bin/env python3
"""Check that standing pytest targets cover all discoverable tests.

Portable across repos: takes --repo-root and the standing targets as
positional arguments. Runs pytest --collect-only twice (full test root
vs targets) and reports any tests missing from the standing targets.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def collect_test_ids(repo_root: Path, targets: list[str]) -> set[str]:
    result = subprocess.run(
        ["python3", "-m", "pytest", "--collect-only", "-q", *targets],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    ids: set[str] = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if line and "::" in line and not line.startswith(("=", "-", " ")):
            ids.add(line)
    return ids


def find_test_root(repo_root: Path) -> str | None:
    for candidate in ("tests", "test"):
        if (repo_root / candidate).is_dir():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("targets", nargs="*", help="Standing pytest targets (files, dirs, or globs)")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    test_root = find_test_root(repo_root)
    if test_root is None:
        return 0

    all_tests = collect_test_ids(repo_root, [test_root])
    if not all_tests:
        return 0

    if not args.targets:
        print("no standing targets provided; skipping completeness check", file=sys.stderr)
        return 0

    targeted_tests = collect_test_ids(repo_root, args.targets)
    missing = all_tests - targeted_tests
    if not missing:
        return 0

    missing_files = sorted({tid.split("::")[0] for tid in missing})
    print(
        f"{len(missing)} test(s) in {len(missing_files)} file(s) not covered by standing pytest targets:",
        file=sys.stderr,
    )
    for path in missing_files:
        count = sum(1 for tid in missing if tid.startswith(path + "::"))
        print(f"  {path} ({count})", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
