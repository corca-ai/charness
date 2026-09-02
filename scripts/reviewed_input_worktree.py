"""Working-tree Git snapshot and patch provenance for reviewed inputs."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable, NamedTuple

from scripts.checkout_view import CheckoutView
from scripts.core.git_checkout import head_oid_from_files, local_checkout
from scripts.core.git_status_snapshot import GitStatusError, GitStatusSnapshot
from scripts.core.git_status_snapshot import capture as capture_git_status
from scripts.reviewed_input_path_selection import checked_path, lexical_path

GitBytes = Callable[..., bytes]


class WorkingTreeSnapshot(NamedTuple):
    branch_oid: str
    untracked_paths: frozenset[str]
    staged_dirty: bool
    unstaged_dirty: bool

    @classmethod
    def from_status(cls, snapshot: GitStatusSnapshot) -> WorkingTreeSnapshot:
        if snapshot.head_oid is None:
            raise ValueError("git status did not report a valid branch OID")
        staged, unstaged = snapshot.staged_or_unstaged_dirty()
        return cls(snapshot.head_oid, snapshot.untracked_paths(), staged, unstaged)


def local_git_checkout(repo_root: Path) -> bool:
    """Ordinary on-disk checkout at this root; env redirect still belongs to Git."""
    return local_checkout(repo_root)


def capture(
    repo_root: Path,
    git_bytes: GitBytes | None = None,
    *,
    checkout: CheckoutView | None = None,
) -> WorkingTreeSnapshot:
    try:
        if checkout is not None:
            snapshot = checkout.status()
        else:
            snapshot = capture_git_status(repo_root, git_bytes=git_bytes)
    except GitStatusError as exc:
        raise ValueError(str(exc)) from exc
    return WorkingTreeSnapshot.from_status(snapshot)


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


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def content_sha256(repo_root: Path, path: str) -> str | None:
    """None only when the path is ABSENT from the working tree.

    A read failure over a PRESENT file used to return None too, and the deletion
    fallbacks then bound HEAD's bytes and stamped `disposition: deleted` on a
    file that is still there with unreadable, changed contents -- capture and
    verification agreeing on bytes neither read. Absence is a state; a failure to
    read is not.
    """
    try:
        # No symlink arm: `_checked_path` above refuses symlinks (f7a09d672), so
        # the link-payload branch that used to sit here was unreachable from the
        # moment that approval boundary landed, and the public contract went on
        # describing it. Removed rather than left as decoration.
        candidate = checked_path(repo_root, path)
        if not candidate.is_file():
            return None
        # The exec bit belongs in the content digest: otherwise `chmod +x` on a
        # reviewed script would pass as unchanged because its bytes are identical.
        mode_tag = b"x\0" if candidate.stat().st_mode & 0o111 else b"-\0"
        return _digest(b"file\0" + mode_tag + candidate.read_bytes())
    except OSError:
        # Resolved from `path`, not from `candidate`: `_checked_path` itself can
        # raise, leaving `candidate` unbound, and referencing it there turned an
        # OSError into a NameError. The existing contract test named exactly that
        # path.
        probe = repo_root / lexical_path(path)
        if probe.exists() or probe.is_symlink():
            raise
        return None
