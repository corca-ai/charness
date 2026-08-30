#!/usr/bin/env python3

"""One Git-backed file population shared by documentation validators."""

from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import import_repo_module

_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
RepoFileSnapshot = _repo_file_listing.RepoFileSnapshot
iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files
iter_repo_files = _repo_file_listing.iter_repo_files

DOC_GLOBS = (
    "README.md",
    "AGENTS.md",
    "docs/**/*.md",
    "presets/**/*.md",
    "profiles/**/*.md",
    "skills/public/**/*.md",
    "skills/support/**/*.md",
    "skills/shared/**/*.md",
)
SKIP_DIR_NAMES = {".git", "node_modules", ".pytest_cache", "__pycache__"}


def iter_docs(
    root: Path,
    *,
    require_git: bool = False,
    snapshot: RepoFileSnapshot | None = None,
) -> list[Path]:
    return iter_matching_repo_files(
        root, DOC_GLOBS, require_git=require_git, snapshot=snapshot
    )


def iter_known_repo_paths(
    root: Path,
    *,
    require_git: bool = False,
    suffix: str | None = None,
    snapshot: RepoFileSnapshot | None = None,
) -> set[str]:
    known: set[str] = set()
    for path in iter_repo_files(
        root, require_git=require_git, snapshot=snapshot
    ):
        if suffix is not None and path.suffix != suffix:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        known.add(path.relative_to(root).as_posix())
    return known


def iter_known_markdown_paths(
    root: Path,
    *,
    require_git: bool = False,
    snapshot: RepoFileSnapshot | None = None,
) -> set[str]:
    return iter_known_repo_paths(
        root, require_git=require_git, suffix=".md", snapshot=snapshot
    )
