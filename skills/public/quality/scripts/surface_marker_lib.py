from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

NESTED_CLI_RE = re.compile(
    r"\b(subprocess\.(?:run|check_call|check_output|Popen)|spawnSync|execFileSync|execSync|spawn\(|execa\()"
)


def nested_cli_files(repo_root: Path, test_files: list[Path]) -> list[str]:
    matches: list[str] = []
    for path in test_files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if NESTED_CLI_RE.search(text):
            matches.append(path.relative_to(repo_root).as_posix())
    return matches


def _name_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [*_name_parts(node.value), node.attr]
    if isinstance(node, ast.Call):
        return _name_parts(node.func)
    return []


def _pytest_aliases(tree: ast.Module) -> tuple[set[str], set[str]]:
    pytest_aliases = {"pytest"}
    mark_aliases: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pytest":
                    pytest_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "pytest":
            for alias in node.names:
                if alias.name == "mark":
                    mark_aliases.add(alias.asname or alias.name)
    return pytest_aliases, mark_aliases


def _is_release_only_marker(node: ast.AST, pytest_aliases: set[str], mark_aliases: set[str]) -> bool:
    parts = _name_parts(node)
    return (
        (len(parts) >= 3 and parts[-3] in pytest_aliases and parts[-2:] == ["mark", "release_only"])
        or (len(parts) >= 2 and parts[-2] in mark_aliases and parts[-1] == "release_only")
    )


def _module_release_only(tree: ast.Module) -> bool:
    pytest_aliases, mark_aliases = _pytest_aliases(tree)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if "pytestmark" not in targets:
            continue
        if _is_release_only_marker(node.value, pytest_aliases, mark_aliases):
            return True
        if isinstance(node.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(item, pytest_aliases, mark_aliases) for item in node.value.elts):
                return True
    return False


def _class_release_only(node: ast.ClassDef, pytest_aliases: set[str], mark_aliases: set[str]) -> bool:
    if any(_is_release_only_marker(decorator, pytest_aliases, mark_aliases) for decorator in node.decorator_list):
        return True
    for item in node.body:
        if not isinstance(item, ast.Assign):
            continue
        targets = [target.id for target in item.targets if isinstance(target, ast.Name)]
        if "pytestmark" in targets and _is_release_only_marker(item.value, pytest_aliases, mark_aliases):
            return True
        if "pytestmark" in targets and isinstance(item.value, (ast.List, ast.Tuple)):
            if any(_is_release_only_marker(marker, pytest_aliases, mark_aliases) for marker in item.value.elts):
                return True
    return False


def _function_release_only(
    node: ast.FunctionDef | ast.AsyncFunctionDef, pytest_aliases: set[str], mark_aliases: set[str]
) -> bool:
    return any(_is_release_only_marker(decorator, pytest_aliases, mark_aliases) for decorator in node.decorator_list)


def _iter_tests(tree: ast.Module) -> list[tuple[str, bool]]:
    pytest_aliases, mark_aliases = _pytest_aliases(tree)
    module_release_only = _module_release_only(tree)
    tests: list[tuple[str, bool]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            tests.append((node.name, module_release_only or _function_release_only(node, pytest_aliases, mark_aliases)))
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            class_release_only = module_release_only or _class_release_only(node, pytest_aliases, mark_aliases)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test_"):
                    tests.append(
                        (
                            f"{node.name}.{item.name}",
                            class_release_only or _function_release_only(item, pytest_aliases, mark_aliases),
                        )
                    )
    return tests


def pytest_file_test_counts(repo_root: Path, rel_paths: list[str]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for rel_path in rel_paths:
        try:
            text = (repo_root / rel_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(text, filename=rel_path)
        except SyntaxError:
            continue
        tests = _iter_tests(tree)
        release_only_count = sum(1 for _, marked in tests if marked)
        files.append(
            {
                "path": rel_path,
                "test_count": len(tests),
                "release_only_count": release_only_count,
                "standing_count": len(tests) - release_only_count,
            }
        )
    return files


def module_release_only_files(repo_root: Path, rel_paths: list[str]) -> list[str]:
    matches: list[str] = []
    for rel_path in rel_paths:
        try:
            text = (repo_root / rel_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(text, filename=rel_path)
        except SyntaxError:
            continue
        if _module_release_only(tree):
            matches.append(rel_path)
    return matches
