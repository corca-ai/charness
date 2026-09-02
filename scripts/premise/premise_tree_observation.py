"""Observe current index/worktree state for a normalized premise tree."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

try:
    _subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
except ModuleNotFoundError:
    _subprocess_guard_spec = importlib.util.spec_from_file_location(
        "subprocess_guard", Path(__file__).resolve().parents[1] / "core" / "subprocess_guard.py"
    )
    if _subprocess_guard_spec is None or _subprocess_guard_spec.loader is None:
        raise
    _subprocess_guard = importlib.util.module_from_spec(_subprocess_guard_spec)
    sys.modules["subprocess_guard"] = _subprocess_guard
    _subprocess_guard_spec.loader.exec_module(_subprocess_guard)
run_process = _subprocess_guard.run_process


class ObservationPathEscape(ValueError):
    pass


class CurrentTreeInspectionError(RuntimeError):
    pass


def _repo_path(repo_root: Path, relative: str) -> Path:
    candidate = repo_root / relative
    try:
        candidate.resolve(strict=False).relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ObservationPathEscape(relative) from exc
    return candidate


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_bytes(repo_root: Path, *args: str):
    return run_process(["git", *args], cwd=repo_root, timeout_seconds=None)


def _index_paths(repo_root: Path) -> set[bytes]:
    try:
        _repo_file_listing = import_repo_module(__file__, "scripts.core.repo_file_listing")
    except ModuleNotFoundError:
        _repo_file_listing_spec = importlib.util.spec_from_file_location(
            "repo_file_listing", Path(__file__).resolve().parents[1] / "core" / "repo_file_listing.py"
        )
        if _repo_file_listing_spec is None or _repo_file_listing_spec.loader is None:
            raise
        _repo_file_listing = importlib.util.module_from_spec(_repo_file_listing_spec)
        sys.modules["repo_file_listing"] = _repo_file_listing
        _repo_file_listing_spec.loader.exec_module(_repo_file_listing)
    RepoFileListingError = _repo_file_listing.RepoFileListingError
    RepoFileSnapshot = _repo_file_listing.RepoFileSnapshot
    try:
        listed = RepoFileSnapshot(repo_root, require_git=True).list_files(include_untracked=False)
    except RepoFileListingError as exc:
        raise CurrentTreeInspectionError("cannot inspect the current index") from exc
    if listed is None:
        raise CurrentTreeInspectionError("cannot inspect the current index")
    return {path.relative_to(repo_root).as_posix().encode("utf-8") for path in listed}


def observe_current_tree(
    repo_root: Path,
    candidate: dict[str, Any],
    *,
    index_objects: dict[str, tuple[str, bytes] | None] | None = None,
    index_paths: set[bytes] | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    """Return normalized observations and whether protected state drifted."""
    observations: dict[str, list[dict[str, Any]]] = {
        "protected": [],
        "expected_missing": [],
    }
    drift = False
    for row in candidate["protected"]:
        path = _repo_path(repo_root, row["path"])
        worktree_sha: str | None = None
        index_sha: str | None = None
        if path.is_symlink() or not path.is_file():
            drift = True
        else:
            try:
                worktree_sha = _sha256(path.read_bytes())
            except OSError:
                drift = True
            else:
                drift = drift or worktree_sha != row["sha256"]
        if index_objects is not None:
            indexed = index_objects.get(row["path"])
            if indexed is not None and indexed[0] == "blob":
                index_sha = _sha256(indexed[1])
        else:
            index = _git_bytes(repo_root, "show", f":{row['path']}")
            if index.returncode == 0:
                index_sha = _sha256(index.stdout.encode("utf-8", errors="surrogateescape"))
        if index_sha != row["sha256"]:
            drift = True
        observations["protected"].append(
            {
                "path": row["path"],
                "captured_sha256": row["sha256"],
                "index_sha256": index_sha,
                "worktree_sha256": worktree_sha,
            }
        )
    if index_paths is None:
        index_paths = _index_paths(repo_root) if candidate["expected_missing"] else set()
    for relative in candidate["expected_missing"]:
        path = _repo_path(repo_root, relative)
        relative_bytes = relative.encode("utf-8")
        index_present = any(
            indexed == relative_bytes or indexed.startswith(relative_bytes + b"/")
            for indexed in index_paths
        )
        worktree_present = os.path.lexists(path)
        if worktree_present or index_present:
            drift = True
        observations["expected_missing"].append(
            {
                "path": relative,
                "expected_absent": True,
                "index_present": index_present,
                "worktree_present": worktree_present,
            }
        )
    return observations, drift
