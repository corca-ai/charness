#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
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
SKIP_DIR_NAMES = {
    ".cautilus",
    ".charness",
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
}

IGNORE_PATTERNS_RE = re.compile(r"\bshutil\.ignore_patterns\s*\(")
COPYTREE_ROOT_RE = re.compile(r"\bshutil\.copytree\s*\(\s*ROOT\b")
COPY_HEAVY_FIXTURES = frozenset(
    {
        "seeded_charness_repo",
        "seeded_charness_git_repo",
        "seeded_managed_home",
    }
)
COPY_HEAVY_HELPERS = frozenset(
    {
        "clone_seeded_charness_repo",
        "clone_seeded_managed_home",
    }
)
COPY_HEAVY_TOKEN_RE = re.compile(
    r"\b("
    + "|".join(
        re.escape(name)
        for name in sorted(COPY_HEAVY_FIXTURES | COPY_HEAVY_HELPERS)
    )
    + r")\b"
)


def _name_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [*_name_parts(node.value), node.attr]
    if isinstance(node, ast.Call):
        return _name_parts(node.func)
    return []


def _is_release_only_marker(node: ast.AST) -> bool:
    parts = _name_parts(node)
    return len(parts) >= 3 and parts[-3:] == ["pytest", "mark", "release_only"]


def _module_is_release_only(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "pytestmark" for target in node.targets):
            continue
        if _is_release_only_marker(node.value):
            return True
        if isinstance(node.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(item) for item in node.value.elts):
                return True
    return False


def _function_is_release_only(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_is_release_only_marker(decorator) for decorator in node.decorator_list)


def _copy_heavy_reason(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    fixture_hits = sorted(
        arg.arg for arg in node.args.args if arg.arg in COPY_HEAVY_FIXTURES
    )
    helper_hits: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        parts = _name_parts(child.func)
        if parts and parts[-1] in COPY_HEAVY_HELPERS:
            helper_hits.add(parts[-1])
    reasons: list[str] = []
    if fixture_hits:
        reasons.append(f"copy-heavy fixture(s): {', '.join(fixture_hits)}")
    if helper_hits:
        reasons.append(f"copy-heavy helper(s): {', '.join(sorted(helper_hits))}")
    return "; ".join(reasons) if reasons else None


def _copy_heavy_marker_violations(source: str, rel_path: Path) -> list[str]:
    try:
        tree = ast.parse(source, filename=rel_path.as_posix())
    except SyntaxError:
        return []
    if _module_is_release_only(tree):
        return []
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        reason = _copy_heavy_reason(node)
        if reason is None or _function_is_release_only(node):
            continue
        violations.append(
            f"{rel_path.as_posix()}::{node.name}: uses {reason}. "
            "Copy-heavy repo/home/plugin tests must be marked `pytest.mark.release_only` "
            "so standing pre-push excludes full-copy lifecycle proof."
        )
    return violations


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
        if COPY_HEAVY_TOKEN_RE.search(text):
            violations.extend(_copy_heavy_marker_violations(text, rel_path))
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
        "Test fixture drift: repo-copy helpers must stay centralized, and copy-heavy tests must be release-only.",
        file=sys.stderr,
    )
    for violation in violations:
        print(f"- {violation}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
