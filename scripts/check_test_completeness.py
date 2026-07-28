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


def repo_root_targets(repo_root: Path, targets: list[str]) -> list[tuple[int, str]]:
    """1-based ``(position, target)`` for every target that IS the repo root.

    `repo_root / ""` resolves to the REPO ROOT, so such a target made
    `relative_test_files` rglob the entire repo and every test file counted as
    covered by standing targets — this gate reporting full completeness having
    established nothing. It is not a hypothetical input: `run-quality.sh` builds the
    array with `mapfile` from `run_standing_pytest.py --print-expanded-targets`, and
    `mapfile` on empty output yields exactly one empty element.

    Blankness is NOT the test, because it is only one spelling of the same thing.
    `PurePath` drops single-dot components at construction, so `.` and `./` resolve
    to the repo root too — and `.` is the most natural pytest target anyone would
    write, reachable through `run_standing_pytest.py --pytest-target .`. The check is
    therefore on the RESOLVED path, which catches every spelling including an
    absolute path that happens to be the root.
    """
    resolved_root = repo_root.resolve()
    offenders: list[tuple[int, str]] = []
    for index, target in enumerate(targets, start=1):
        if any(char in target for char in "*?["):
            continue
        try:
            candidate = (repo_root / target).resolve()
        except OSError:
            continue
        if candidate == resolved_root:
            offenders.append((index, target))
    return offenders


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

    # Reached only when this repo HAS test files (both earlier returns are about a repo
    # with none), so an empty target list here is the producer having failed, not a repo
    # without tests. It used to skip with exit 0 — the same unestablished-scope pass the
    # blank-target refusal below exists to stop, which meant the refusal's own advice
    # ("check the producer") routed an operator into a green run by filtering the blank
    # out of the array.
    if not args.targets:
        print(
            f"no standing pytest targets provided, but {len(all_tests)} test file(s) exist under "
            f"{test_root}; the target list did not resolve, so completeness was never established. "
            "Check the producer (`run_standing_pytest.py --print-expanded-targets`).",
            file=sys.stderr,
        )
        return 1

    offenders = repo_root_targets(repo_root, args.targets)
    if offenders:
        # LOUD, not skipped: such a target is the caller's target list failing to
        # resolve, and both silent options are wrong here. Widening to the repo root
        # reports full completeness over an unestablished scope; dropping the offender
        # would report completeness against the remaining targets as if the list were
        # whole.
        rendered = ", ".join(f"position {index} ({target!r})" for index, target in offenders)
        print(
            f"standing target(s) resolve to the repo root: {rendered}. `repo_root / \"\"` (and "
            "`.`, and `./`) IS the repo root, so this would rglob the whole repo and report every "
            "test file as covered. Check the producer of the target list "
            "(`run_standing_pytest.py --print-expanded-targets`).",
            file=sys.stderr,
        )
        return 1

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
