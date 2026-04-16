#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files

REPO_SCRIPT_FILE_MAX = 380
SKILL_HELPER_FILE_MAX = 220
TEST_FILE_MAX = 500
FUNCTION_MAX = 100
TEST_FUNCTION_MAX = 150


class ValidationError(Exception):
    pass


def iter_python_targets(root: Path) -> list[Path]:
    return iter_matching_repo_files(
        root,
        (
            "scripts/*.py",
            "skills/public/*/scripts/*.py",
            "skills/support/*/scripts/*.py",
            "tests/*.py",
            "tests/**/*.py",
        ),
    )


def file_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("scripts",):
        return REPO_SCRIPT_FILE_MAX
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_MAX
    return SKILL_HELPER_FILE_MAX


def validate_file_length(path: Path, root: Path) -> None:
    line_count = len(path.read_text(encoding="utf-8").splitlines())
    limit = file_limit_for(path, root)
    if line_count > limit:
        raise ValidationError(f"{path}: file length {line_count} exceeds limit {limit}")


def function_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("tests",):
        return TEST_FUNCTION_MAX
    return FUNCTION_MAX


def validate_function_lengths(path: Path, root: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    limit = function_limit_for(path, root)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            continue
        length = node.end_lineno - node.lineno + 1
        if length > limit:
            raise ValidationError(
                f"{path}: function `{node.name}` length {length} exceeds limit {limit}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    targets = iter_python_targets(root)
    for path in targets:
        try:
            validate_file_length(path, root)
            validate_function_lengths(path, root)
        except (ValidationError, SyntaxError) as exc:
            raise ValidationError(str(exc)) from exc

    print(f"Validated Python length limits for {len(targets)} file(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
