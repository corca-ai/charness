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

REPO_SCRIPT_FILE_MAX = 480
SKILL_HELPER_FILE_MAX = 360
TEST_FILE_MAX = 800
FUNCTION_MAX = 100
TEST_FUNCTION_MAX = 150

# Advisory file-length warn band (file length only — function limits stay
# hard-only). A file in ``[warn, limit]`` keeps exit 0 but emits a ``WARN:``
# line so this saturated codebase gets an early signal before the existing hard
# fail. The ``WARN:`` prefix is load-bearing: ``run-quality.sh`` only surfaces a
# *passing* gate's output when it matches
# ``^(WARNING|WARN|WEAK|ADVISORY)(:|[[:space:]])`` — an unprefixed advisory is
# captured to the log but never shown, silently defeating the tier.
REPO_SCRIPT_FILE_WARN = 432
SKILL_HELPER_FILE_WARN = 330
TEST_FILE_WARN = 720


class ValidationError(Exception):
    pass


def iter_python_targets(root: Path, *, require_git: bool = False) -> list[Path]:
    return iter_matching_repo_files(
        root,
        (
            "scripts/*.py",
            "skills/public/*/scripts/*.py",
            "skills/support/*/scripts/*.py",
            "tests/*.py",
            "tests/**/*.py",
        ),
        require_git=require_git,
    )


def file_limit_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("scripts",):
        return REPO_SCRIPT_FILE_MAX
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_MAX
    return SKILL_HELPER_FILE_MAX


def file_warn_for(path: Path, root: Path) -> int:
    relative = path.relative_to(root)
    if relative.parts[:1] == ("scripts",):
        return REPO_SCRIPT_FILE_WARN
    if relative.parts[:1] == ("tests",):
        return TEST_FILE_WARN
    return SKILL_HELPER_FILE_WARN


def validate_file_length(path: Path, root: Path) -> str | None:
    """Hard-fail when a file exceeds its limit; otherwise return an advisory
    ``WARN:`` line when the file sits in the ``[warn, limit]`` band, or ``None``.
    """
    line_count = len(path.read_text(encoding="utf-8").splitlines())
    limit = file_limit_for(path, root)
    if line_count > limit:
        raise ValidationError(f"{path}: file length {line_count} exceeds limit {limit}")
    warn = file_warn_for(path, root)
    if line_count >= warn:
        relative = path.relative_to(root)
        return (
            f"WARN: {relative}: file length {line_count} is within the advisory warn "
            f"band [{warn}, {limit}]; trim before it reaches the hard limit {limit}."
        )
    return None


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


def select_targets(
    root: Path, *, paths: list[Path] | None, require_git: bool
) -> list[Path]:
    """Whole-repo glob by default. When ``paths`` is given (e.g. staged files in
    a pre-commit hook), restrict to the subset of those paths the whole-repo
    glob would also gate, so the same per-class limits/bands apply and a path
    outside the gated universe (an export mirror, a top-level file) is never
    gated. Staged-only by design: a pre-existing over-limit file not in
    ``paths`` is left to the whole-repo run.
    """
    if paths is None:
        return iter_python_targets(root, require_git=require_git)
    universe = set(iter_python_targets(root, require_git=False))
    requested = {(p if p.is_absolute() else root / p).resolve() for p in paths}
    return sorted(universe & requested)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument(
        "--paths",
        nargs="+",
        type=Path,
        metavar="FILE",
        help=(
            "Explicit files to check (e.g. staged files in a pre-commit hook). "
            "Restricts the check to the subset of these paths the whole-repo "
            "glob would also gate, applying the same per-class limits and warn "
            "bands. Takes precedence over the glob scan; "
            "--require-git-file-listing is then irrelevant."
        ),
    )
    args = parser.parse_args()

    root = args.repo_root.resolve()
    targets = select_targets(
        root, paths=args.paths, require_git=args.require_git_file_listing
    )
    warnings: list[str] = []
    for path in targets:
        try:
            warning = validate_file_length(path, root)
            validate_function_lengths(path, root)
        except (ValidationError, SyntaxError) as exc:
            raise ValidationError(str(exc)) from exc
        if warning is not None:
            warnings.append(warning)

    for warning in warnings:
        print(warning)
    print(f"Validated Python length limits for {len(targets)} file(s).")
    if warnings:
        print(
            f"WARN: {len(warnings)} file(s) within the advisory file-length warn band "
            "(exit 0; trim before they reach the hard limit)."
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
