#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "evals",
    "node_modules",
    "plugins",
    "tests",
}
DEFAULT_MAX_RATIO = 1.0


class RatioError(Exception):
    pass


def python_files(root: Path, *, exclude_dirs: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        relative_parts = path.relative_to(root).parts
        if any(part in exclude_dirs for part in relative_parts[:-1]):
            continue
        files.append(path)
    return sorted(files)


def count_lines(paths: list[Path]) -> int:
    return sum(len(path.read_text(encoding="utf-8").splitlines()) for path in paths)


def summarize(repo_root: Path) -> dict[str, object]:
    tests_root = repo_root / "tests"
    source_files = python_files(repo_root, exclude_dirs=IGNORED_DIRS)
    test_files = python_files(tests_root, exclude_dirs=set()) if tests_root.is_dir() else []
    source_lines = count_lines(source_files)
    test_lines = count_lines(test_files)
    ratio = test_lines / source_lines if source_lines else 0.0
    return {
        "schema_version": 1,
        "scope": "python-source-truth",
        "source_lines": source_lines,
        "test_lines": test_lines,
        "ratio": round(ratio, 4),
        "source_file_count": len(source_files),
        "test_file_count": len(test_files),
        "excluded_source_dirs": sorted(IGNORED_DIRS),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--max-ratio", type=float, default=DEFAULT_MAX_RATIO)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = summarize(args.repo_root.resolve())
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(
            "Test-production ratio: "
            f"{summary['ratio']:.2f} ({summary['test_lines']}/{summary['source_lines']} Python lines, "
            f"max {args.max_ratio:.2f})"
        )
    if float(summary["ratio"]) > args.max_ratio:
        raise RatioError(f"test-production ratio {summary['ratio']:.2f} exceeds max {args.max_ratio:.2f}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RatioError as exc:
        print(str(exc))
        raise SystemExit(1)
