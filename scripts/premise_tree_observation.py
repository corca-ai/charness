"""Observe current index/worktree state for a normalized premise tree."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any


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


def _git_bytes(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )


def _index_paths(repo_root: Path) -> set[bytes]:
    result = _git_bytes(repo_root, "ls-files", "-z")
    if result.returncode != 0:
        raise CurrentTreeInspectionError("cannot inspect the current index")
    return {entry for entry in result.stdout.split(b"\0") if entry}


def observe_current_tree(
    repo_root: Path,
    candidate: dict[str, Any],
    *,
    index_objects: dict[str, tuple[str, bytes] | None] | None = None,
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
                index_sha = _sha256(index.stdout)
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
