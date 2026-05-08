#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CANONICAL_MODULE = "tests/repo_copy.py"
# Files allowed to mention the patterns this guard searches for. The guard's own
# self-test file is included so it can write sample drift code into temporary
# fake repos without tripping itself.
ALLOWED_FILES = frozenset(
    {
        CANONICAL_MODULE,
        "tests/quality_gates/test_repo_copy_invariants.py",
    }
)
SKIP_DIR_NAMES = {".charness", ".git", ".venv", ".pytest_cache", "__pycache__", "node_modules"}

IGNORE_PATTERNS_RE = re.compile(r"\bshutil\.ignore_patterns\s*\(")
COPYTREE_ROOT_RE = re.compile(r"\bshutil\.copytree\s*\(\s*ROOT\b")


def _iter_python_files(tests_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in tests_root.rglob("*.py"):
        rel_path = path.relative_to(tests_root.parent)
        if any(part in SKIP_DIR_NAMES for part in rel_path.parts):
            continue
        files.append(rel_path)
    return sorted(files)


def find_violations(repo_root: Path) -> list[str]:
    tests_root = repo_root / "tests"
    if not tests_root.is_dir():
        return []
    violations: list[str] = []
    for rel_path in _iter_python_files(tests_root):
        if rel_path.as_posix() in ALLOWED_FILES:
            continue
        text = (repo_root / rel_path).read_text(encoding="utf-8")
        if IGNORE_PATTERNS_RE.search(text):
            violations.append(
                f"{rel_path.as_posix()}: defines shutil.ignore_patterns(...). "
                f"Use REPO_COPY_IGNORE from {CANONICAL_MODULE} instead so the ignore set stays a single source of truth."
            )
        if COPYTREE_ROOT_RE.search(text):
            violations.append(
                f"{rel_path.as_posix()}: calls shutil.copytree(ROOT, ...) inline. "
                f"Use clone_seeded_charness_repo(...) with seeded_charness_repo or seeded_charness_git_repo "
                f"from {CANONICAL_MODULE} so fixtures share a session-scoped seed."
            )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Enforce that the charness repo copy ignore set and ROOT-cloning fixtures live in a single "
            "module (tests/repo_copy.py). Drift between local copies caused a 132M test fixture in "
            "early 2026."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    violations = find_violations(repo_root)
    if not violations:
        return 0

    print(
        "Test fixture drift: shutil.ignore_patterns / shutil.copytree(ROOT, ...) must only appear in "
        f"{CANONICAL_MODULE}.",
        file=sys.stderr,
    )
    for violation in violations:
        print(f"- {violation}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
