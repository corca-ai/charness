"""Working-tree Git snapshot and patch provenance for reviewed inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, NamedTuple

from scripts.git_checkout import head_oid_from_files, local_checkout
from scripts.git_status_snapshot import GitStatusError
from scripts.git_status_snapshot import capture as capture_git_status

GitBytes = Callable[..., bytes]


class WorkingTreeSnapshot(NamedTuple):
    branch_oid: str
    untracked_paths: frozenset[str]
    staged_dirty: bool
    unstaged_dirty: bool


def local_git_checkout(repo_root: Path) -> bool:
    """Ordinary on-disk checkout at this root; env redirect still belongs to Git."""
    return local_checkout(repo_root)


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
    base_head = (
        snapshot.branch_oid
        if snapshot
        else head_oid_from_files(repo_root)
        or git_bytes(repo_root, "rev-parse", "HEAD").decode().strip()
    )
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
