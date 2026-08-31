"""Working-tree Git snapshot and patch provenance for reviewed inputs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, NamedTuple

from scripts.git_status_snapshot import GitStatusError
from scripts.git_status_snapshot import capture as capture_git_status

GitBytes = Callable[..., bytes]


class WorkingTreeSnapshot(NamedTuple):
    branch_oid: str
    untracked_paths: frozenset[str]
    staged_dirty: bool
    unstaged_dirty: bool


def local_git_checkout(repo_root: Path) -> bool:
    """True when Git would discover a checkout from ``repo_root`` itself.

    Environment-redirected discovery (``GIT_DIR`` and siblings) still belongs
    to Git: this only admits the ordinary on-disk layout so committed-ref
    identity capture does not spend ``rev-parse --is-inside-work-tree`` to
    learn a fact the files already state.
    """
    if any(os.environ.get(name) for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")):
        return False
    marker = repo_root / ".git"
    if marker.is_file():
        try:
            return marker.read_text(encoding="utf-8").lstrip().startswith("gitdir:")
        except OSError:
            return False
    return (
        marker.is_dir()
        and (marker / "HEAD").is_file()
        and ((marker / "objects").is_dir() or (marker / "commondir").is_file())
    )


def capture(repo_root: Path, git_bytes: GitBytes) -> WorkingTreeSnapshot:
    try:
        snapshot = capture_git_status(repo_root, git_bytes=git_bytes)
    except GitStatusError as exc:
        raise ValueError(str(exc)) from exc
    if snapshot.head_oid is None:
        raise ValueError("git status did not report a valid branch OID")
    staged, unstaged = snapshot.staged_or_unstaged_dirty()
    return WorkingTreeSnapshot(
        snapshot.head_oid, snapshot.untracked_paths(), staged, unstaged
    )


def patch_components(
    repo_root: Path,
    paths: list[str],
    snapshot: WorkingTreeSnapshot | None,
    git_bytes: GitBytes,
) -> tuple[str, bytes, bytes]:
    base_head = snapshot.branch_oid if snapshot else git_bytes(
        repo_root, "rev-parse", "HEAD"
    ).decode().strip()
    path_args = ["--", *paths]
    staged = (
        git_bytes(repo_root, "diff", "--cached", "--binary", *path_args)
        if paths and (snapshot is None or snapshot.staged_dirty)
        else b""
    )
    unstaged = (
        git_bytes(repo_root, "diff", "--binary", *path_args)
        if paths and (snapshot is None or snapshot.unstaged_dirty)
        else b""
    )
    return base_head, staged, unstaged
