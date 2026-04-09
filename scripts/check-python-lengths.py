#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_SCRIPT_FILE_MAX = 380
SKILL_HELPER_FILE_MAX = 220
FUNCTION_MAX = 100


class ValidationError(Exception):
    pass


def iter_python_targets(root: Path) -> list[Path]:
    return sorted(
        [*root.glob("scripts/*.py"), *root.glob("skills/public/*/scripts/*.py")]
    )


def file_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("scripts",):
        return REPO_SCRIPT_FILE_MAX
    return SKILL_HELPER_FILE_MAX


def validate_file_length(path: Path, root: Path) -> None:
    line_count = len(path.read_text(encoding="utf-8").splitlines())
    limit = file_limit_for(path, root)
    if line_count > limit:
        raise ValidationError(f"{path}: file length {line_count} exceeds limit {limit}")


def validate_function_lengths(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            continue
        length = node.end_lineno - node.lineno + 1
        if length > FUNCTION_MAX:
            raise ValidationError(
                f"{path}: function `{node.name}` length {length} exceeds limit {FUNCTION_MAX}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    targets = iter_python_targets(root)
    for path in targets:
        try:
            validate_file_length(path, root)
            validate_function_lengths(path)
        except (ValidationError, SyntaxError) as exc:
            raise ValidationError(str(exc)) from exc

    print(f"Validated Python helper length limits for {len(targets)} file(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
