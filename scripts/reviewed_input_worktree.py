"""Working-tree Git snapshot and patch provenance for reviewed inputs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, NamedTuple

_GIT_OID_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
GitBytes = Callable[..., bytes]


class WorkingTreeSnapshot(NamedTuple):
    branch_oid: str
    untracked_paths: frozenset[str]
    staged_dirty: bool
    unstaged_dirty: bool


def capture(repo_root: Path, git_bytes: GitBytes) -> WorkingTreeSnapshot:
    raw = git_bytes(
        repo_root,
        "status",
        "--porcelain=v2",
        "-z",
        "--branch",
        "--untracked-files=all",
    )
    branch_oid: str | None = None
    untracked_paths: set[str] = set()
    staged_dirty = False
    unstaged_dirty = False
    records = raw.split(b"\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if record.startswith(b"# branch.oid "):
            if branch_oid is not None:
                raise ValueError("git status reported multiple branch OIDs")
            try:
                branch_oid = record.removeprefix(b"# branch.oid ").decode("ascii")
            except UnicodeDecodeError as exc:
                raise ValueError("git status reported a malformed branch OID") from exc
            if _GIT_OID_RE.fullmatch(branch_oid) is None or not set(branch_oid) - {"0"}:
                raise ValueError("git status did not report a valid branch OID")
        elif record.startswith(b"? "):
            untracked_paths.add(record[2:].decode("utf-8", errors="surrogateescape"))
        elif record.startswith((b"1 ", b"2 ")):
            status = record[2:4]
            if len(status) != 2:
                staged_dirty = unstaged_dirty = True
            else:
                staged_dirty |= status[:1] != b"."
                unstaged_dirty |= status[1:] != b"."
            if record.startswith(b"2 ") and index < len(records):
                index += 1
        elif record.startswith(b"u "):
            staged_dirty = unstaged_dirty = True
        elif record and not record.startswith(b"# "):
            staged_dirty = unstaged_dirty = True
    if branch_oid is None:
        raise ValueError("git status did not report a valid branch OID")
    return WorkingTreeSnapshot(
        branch_oid, frozenset(untracked_paths), staged_dirty, unstaged_dirty
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
