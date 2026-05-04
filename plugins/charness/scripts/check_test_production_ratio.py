#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
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
SUPPORTED_ENGINES = ("splitlines", "tokei")


class RatioError(Exception):
    pass


class TokeiUnavailableError(RuntimeError):
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


def _splitlines_summary(repo_root: Path) -> dict[str, object]:
    tests_root = repo_root / "tests"
    source_files = python_files(repo_root, exclude_dirs=IGNORED_DIRS)
    test_files = python_files(tests_root, exclude_dirs=set()) if tests_root.is_dir() else []
    source_lines = count_lines(source_files)
    test_lines = count_lines(test_files)
    return {
        "source_lines": source_lines,
        "test_lines": test_lines,
        "source_file_count": len(source_files),
        "test_file_count": len(test_files),
    }


def _tokei_python_code(target: Path, *, exclude: set[str]) -> tuple[int, int]:
    if shutil.which("tokei") is None:
        raise TokeiUnavailableError(
            "tokei binary not found on PATH; install per integrations/tools/tokei.json or "
            "fall back to --engine splitlines."
        )
    cmd = ["tokei", "--output", "json", "--type", "Python"]
    for name in sorted(exclude):
        cmd.extend(["--exclude", name])
    cmd.append(str(target))
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise TokeiUnavailableError(
            f"tokei exited with status {completed.returncode}: {completed.stderr.strip()}"
        )
    payload = json.loads(completed.stdout)
    python = payload.get("Python")
    if not isinstance(python, dict):
        return 0, 0
    code = int(python.get("code", 0))
    files = len(python.get("reports", []) or [])
    return code, files


def _tokei_summary(repo_root: Path) -> dict[str, object]:
    tests_root = repo_root / "tests"
    source_code, source_files = _tokei_python_code(repo_root, exclude=IGNORED_DIRS)
    if tests_root.is_dir():
        test_code, test_files = _tokei_python_code(tests_root, exclude=set())
    else:
        test_code, test_files = 0, 0
    return {
        "source_lines": source_code,
        "test_lines": test_code,
        "source_file_count": source_files,
        "test_file_count": test_files,
    }


def summarize(repo_root: Path, *, engine: str = "splitlines") -> dict[str, object]:
    if engine not in SUPPORTED_ENGINES:
        raise ValueError(f"unsupported engine {engine!r}; expected one of {SUPPORTED_ENGINES}")
    if engine == "tokei":
        counts = _tokei_summary(repo_root)
    else:
        counts = _splitlines_summary(repo_root)
    source_lines = int(counts["source_lines"])
    test_lines = int(counts["test_lines"])
    ratio = test_lines / source_lines if source_lines else 0.0
    return {
        "schema_version": 1,
        "scope": "python-source-truth",
        "engine": engine,
        "source_lines": source_lines,
        "test_lines": test_lines,
        "ratio": round(ratio, 4),
        "source_file_count": counts["source_file_count"],
        "test_file_count": counts["test_file_count"],
        "excluded_source_dirs": sorted(IGNORED_DIRS),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--max-ratio", type=float, default=DEFAULT_MAX_RATIO)
    parser.add_argument("--engine", choices=SUPPORTED_ENGINES, default="splitlines")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        summary = summarize(args.repo_root.resolve(), engine=args.engine)
    except TokeiUnavailableError as exc:
        print(str(exc))
        return 2
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(
            "Test-production ratio: "
            f"{summary['ratio']:.2f} ({summary['test_lines']}/{summary['source_lines']} Python lines, "
            f"engine={summary['engine']}, max {args.max_ratio:.2f})"
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
