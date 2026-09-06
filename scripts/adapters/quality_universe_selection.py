"""Intersect declared universes with supplied files without discovering a corpus.

The full universe reader owns discovery and declared-empty refusals. Selection
can establish neither: it only answers which explicitly supplied files belong
to each universe, preserving the reader's directory/glob and Git visibility rules.
"""

from __future__ import annotations

import fnmatch
import os
import sys
from collections.abc import Iterable, Mapping
from functools import lru_cache
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_universes = import_repo_module(__file__, "scripts.adapters.quality_universes_lib")


def _matches_parts(
    parts: tuple[str, ...], pattern: tuple[str, ...], recursive_barriers: frozenset[int]
) -> bool:
    @lru_cache(maxsize=None)
    def match(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(pattern):
            return path_index == len(parts)
        component = pattern[pattern_index]
        if component == "**":
            return match(path_index, pattern_index + 1) or (
                path_index < len(parts)
                and path_index not in recursive_barriers
                and match(path_index + 1, pattern_index)
            )
        return (
            path_index < len(parts)
            and fnmatch.fnmatch(parts[path_index], component)
            and match(path_index + 1, pattern_index + 1)
        )

    return match(0, 0)


def _in_universe(path: Path, root: Path, patterns: tuple[str, ...]) -> bool:
    relative = path.relative_to(root)
    # pathlib recursion does not descend through directory symlinks; an
    # explicitly matched directory may still be the root of a recursive walk.
    barriers = frozenset(
        index
        for index in range(len(relative.parts) - 1)
        if root.joinpath(*relative.parts[: index + 1]).is_symlink()
    )
    for raw in patterns:
        pattern = Path(raw)
        if pattern.is_absolute() or not raw:
            raise ValueError(f"universe pattern must be nonempty and repository-relative: {raw}")
        if any("**" in part and part != "**" for part in pattern.parts):
            raise ValueError("Invalid pattern: '**' can only be an entire path component")
        # Discovery recursively includes a matched directory's descendants.
        # Thus either the file or one of its ancestor directories must match.
        # pathlib made a trailing separator directory-only in Python 3.11.
        # https://docs.python.org/3/library/pathlib.html#pattern-language
        directories_only = sys.version_info >= (3, 11) and raw.endswith(os.sep)
        stop = len(relative.parts) + (not directories_only)
        for end in range(stop):
            if not any(index >= end for index in barriers) and _matches_parts(
                relative.parts[:end], pattern.parts, barriers
            ):
                return True
    return False


def matching_selected_files(
    repo_root: Path,
    universes: Mapping[str, _universes.Universe],
    selected_paths: Iterable[Path],
) -> dict[str, list[Path]]:
    """Use only supplied existing files and one literal, path-scoped Git query.

    Keep lexical file identity: resolving symlinks here would disagree with
    the discovery reader and Git. The review input owner decides whether a
    selected symlink is admissible. An empty selection never proves an empty
    declared universe, so this API intentionally performs no such refusal.
    """
    root = repo_root.resolve()
    candidates: set[Path] = set()
    for selected in selected_paths:
        path = Path(os.path.abspath(root / selected))
        if path.is_relative_to(root) and path.is_file():
            candidates.add(path)
    allowed = _universes._git_listing(root, selected_paths=sorted(candidates))
    if allowed is None:
        raise RuntimeError("repo selected-file listing failed")
    candidates.intersection_update(allowed)
    return {
        family: sorted(path for path in candidates if _in_universe(path, root, universe.patterns))
        for family, universe in universes.items()
    }
