#!/usr/bin/env python3

"""One Git-backed file population shared by documentation validators."""

from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import import_repo_module

_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
RepoFileSnapshot = _repo_file_listing.RepoFileSnapshot
iter_repo_files = _repo_file_listing.iter_repo_files
_quality_adapter = import_repo_module(__file__, "scripts.quality_adapter_lib")
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = import_repo_module(__file__, "scripts.quality_universes_lib")
DEFAULT_UNIVERSES = _quality_universes.DEFAULT_UNIVERSES
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe

DOC_GLOBS = tuple(DEFAULT_UNIVERSES["doc_surfaces"])
SKIP_DIR_NAMES = {".git", "node_modules", ".pytest_cache", "__pycache__"}


def resolve_doc_universe(root: Path):
    return resolve_universe(
        load_quality_adapter(root),
        "doc_surfaces",
        default=DEFAULT_UNIVERSES["doc_surfaces"],
    )


def iter_docs(
    root: Path,
    *,
    require_git: bool = False,
    snapshot: RepoFileSnapshot | None = None,
) -> list[Path]:
    universe = resolve_doc_universe(root)
    docs = [path for path in matching_files(root, universe) if path.suffix.lower() == ".md"]
    refusal = refuse_if_declared_and_empty(universe, docs, "check-doc-links")
    if refusal:
        raise ValueError(refusal)
    return docs


def iter_known_repo_paths(
    root: Path,
    *,
    require_git: bool = False,
    suffix: str | None = None,
    snapshot: RepoFileSnapshot | None = None,
) -> set[str]:
    known: set[str] = set()
    for path in iter_repo_files(root, require_git=require_git, snapshot=snapshot):
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
    return iter_known_repo_paths(root, require_git=require_git, suffix=".md", snapshot=snapshot)
