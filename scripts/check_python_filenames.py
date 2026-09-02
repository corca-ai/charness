#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

_repo_file_listing = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files

VALID_NAME_RE = re.compile(r"^(?:__init__|[a-z][a-z0-9_]*)\.py$")
IMPORT_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SKIP_DIR_NAMES = {".charness", ".git", ".venv", ".pytest_cache", "__pycache__", "node_modules"}
SKIP_PATH_PARTS = {"vendor"}


def iter_python_files(repo_root: Path, *, require_git: bool = False) -> list[Path]:
    files: list[Path] = []
    for path in iter_matching_repo_files(repo_root, ("**/*.py",), require_git=require_git):
        rel_path = path.relative_to(repo_root)
        if any(part in SKIP_DIR_NAMES for part in rel_path.parts):
            continue
        if any(part in SKIP_PATH_PARTS for part in rel_path.parts):
            continue
        files.append(rel_path)
    return sorted(files)


def _resolved_path(value: str | Path) -> Path | None:
    try:
        return Path(value or ".").resolve()
    except (OSError, RuntimeError, TypeError, ValueError):
        return None


def _external_module_spec(name: str, repo_root: Path):
    """Resolve a name without allowing this checkout to satisfy the lookup."""
    excluded: set[Path] = set()
    for path in (
        repo_root,
        repo_root / "scripts",
        Path(__file__).resolve().parents[1],
        Path(__file__).resolve().parent,
    ):
        resolved = _resolved_path(path)
        if resolved is not None:
            excluded.add(resolved)
    saved_path = list(sys.path)
    try:
        sys.path[:] = [
            entry
            for entry in saved_path
            if (resolved := _resolved_path(entry)) is None or resolved not in excluded
        ]
        importlib.invalidate_caches()
        spec = importlib.util.find_spec(name)
    except (ImportError, ModuleNotFoundError, ValueError):
        return None
    finally:
        sys.path[:] = saved_path
    if spec is None:
        return None
    locations = list(spec.submodule_search_locations or ())
    origins = [spec.origin, *locations]
    for origin in origins:
        if origin in {None, "built-in", "frozen"}:
            continue
        resolved = _resolved_path(origin)
        if resolved is not None and all(
            resolved != root and root not in resolved.parents for root in excluded
        ):
            return spec
    return spec if spec.origin in {"built-in", "frozen"} else None


def script_directory_collisions(repo_root: Path) -> list[tuple[Path, str]]:
    scripts_root = repo_root / "scripts"
    if not scripts_root.is_dir():
        return []
    collisions: list[tuple[Path, str]] = []
    for path in sorted(scripts_root.iterdir()):
        if (
            not path.is_dir()
            or path.name in SKIP_DIR_NAMES
            or not IMPORT_NAME_RE.fullmatch(path.name)
        ):
            continue
        if _external_module_spec(path.name, repo_root) is not None:
            collisions.append((path.relative_to(repo_root), path.name))
    return collisions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    invalid = [
        path
        for path in iter_python_files(repo_root, require_git=args.require_git_file_listing)
        if not VALID_NAME_RE.fullmatch(path.name)
    ]
    collisions = script_directory_collisions(repo_root)
    if not invalid and not collisions:
        return 0

    if invalid:
        print("Python filenames must use snake_case outside vendor paths:", file=sys.stderr)
        for path in invalid:
            print(f"- {path.as_posix()}", file=sys.stderr)
    if collisions:
        print(
            "Script directory names must not collide with importable external modules:",
            file=sys.stderr,
        )
        for path, name in collisions:
            print(f"- {path.as_posix()} shadows importable module {name!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
