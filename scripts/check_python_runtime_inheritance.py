#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

DEFAULT_SCAN_GLOBS = ("scripts/*.py", "skills/public/*/scripts/*.py", "skills/support/*/scripts/*.py")
SKIP_PATH_PARTS = {"__pycache__", "vendor", "generated"}


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _is_bash_login_shell_command(node: ast.AST) -> bool:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return False
    values = [_literal_string(item) for item in node.elts[:2]]
    return values == ["/bin/bash", "-lc"]


def _called_function_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_called_function_name(node.value)}.{node.attr}"
    return ""


def _function_source(lines: list[str], node: ast.AST) -> str:
    start = getattr(node, "lineno", 1)
    end = getattr(node, "end_lineno", start)
    return "\n".join(lines[start - 1 : end])


def _encloses(parent: ast.AST, child: ast.AST) -> bool:
    parent_start = getattr(parent, "lineno", -1)
    parent_end = getattr(parent, "end_lineno", -1)
    child_start = getattr(child, "lineno", -1)
    child_end = getattr(child, "end_lineno", child_start)
    return parent_start <= child_start and child_end <= parent_end


def _enclosing_function(tree: ast.AST, call: ast.Call) -> ast.AST:
    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _encloses(node, call)
    ]
    if not functions:
        return tree
    return max(functions, key=lambda node: getattr(node, "lineno", 0))


def _path_is_scannable(path: Path) -> bool:
    return path.suffix == ".py" and not any(part in SKIP_PATH_PARTS for part in path.parts)


def _iter_scan_paths(repo_root: Path) -> list[Path]:
    paths: set[Path] = set()
    for pattern in DEFAULT_SCAN_GLOBS:
        paths.update(repo_root.glob(pattern))
    return sorted(path for path in paths if path.is_file() and _path_is_scannable(path.relative_to(repo_root)))


def check_file(repo_root: Path, path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [f"{path.relative_to(repo_root)}:{exc.lineno}: cannot parse Python source: {exc.msg}"]

    lines = text.splitlines()
    failures: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _called_function_name(node.func) != "subprocess.run":
            continue
        if not node.args or not _is_bash_login_shell_command(node.args[0]):
            continue
        enclosing = _enclosing_function(tree, node)
        source = _function_source(lines, enclosing)
        if "sys.executable" in source and "PATH" in source:
            continue
        failures.append(
            f"{path.relative_to(repo_root)}:{node.lineno}: `/bin/bash -lc` subprocess command must pin "
            "`Path(sys.executable).resolve().parent` at the front of PATH before running Python-bearing commands"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    failures: list[str] = []
    for path in _iter_scan_paths(repo_root):
        failures.extend(check_file(repo_root, path))

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("Validated Python runtime inheritance for bash login-shell subprocess commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
