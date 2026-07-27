"""Shared-tree state capture for the reviewer-boundary fingerprint (#428).

This module owns everything that READS the working tree: the git plumbing, the
porcelain v2 parsing, the per-path content digests, and the review-window stamp
that binds a snapshot to one review interval. Its companion
``reviewer_boundary_fingerprint.py`` owns comparison, attribution, and the CLI.

The split is along a real seam — capture is I/O against git and the filesystem,
comparison is pure functions over two captured dicts — so the comparison side
stays testable without a repo and this side stays the only place that shells out.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone


class FingerprintError(Exception):
    """A usage-level failure: bad repo root, unreadable/corrupt snapshot file."""


def _git_text(repo_root: str, *args: str) -> str:
    # surrogateescape keeps non-UTF8 filenames representable instead of
    # crashing the rail with UnicodeDecodeError (fail-closed must stay JSON).
    proc = subprocess.run(
        ["git", "-C", repo_root, *args],
        check=False,
        capture_output=True,
        text=True,
        errors="surrogateescape",
    )
    if proc.returncode != 0:
        raise FingerprintError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def _git_bytes(repo_root: str, *args: str) -> bytes:
    proc = subprocess.run(["git", "-C", repo_root, *args], check=False, capture_output=True)
    if proc.returncode != 0:
        raise FingerprintError(
            f"git {' '.join(args)} failed: {proc.stderr.decode(errors='replace').strip()}"
        )
    return proc.stdout


def _status_entries(repo_root: str) -> list[str]:
    raw = _git_text(repo_root, "status", "--porcelain=v2", "-z", "--untracked-files=all")
    return sorted(entry for entry in raw.split("\0") if entry)


def _status_path(entry: str) -> str | None:
    """Extract the path field from a porcelain v2 change-type entry (1/2/u)."""
    prefix = entry[0] if entry else ""
    field_count = {"1": 8, "2": 9, "u": 10}.get(prefix)
    if field_count is None:
        return None
    parts = entry.split(" ", field_count)
    return parts[field_count] if len(parts) == field_count + 1 else None


def _status_path_map(entries: list[str]) -> dict[str, str]:
    """path -> XY status pair, for the change-type (1/2/u) entries only."""
    result: dict[str, str] = {}
    for entry in entries:
        if len(entry) < 4 or entry[0] not in ("1", "2", "u") or entry[1] != " ":
            continue
        path = _status_path(entry)
        if path is not None:
            result[path] = entry[2:4]
    return result


def _changed_paths(entries: list[str]) -> list[str]:
    return sorted(_status_path_map(entries))


def _hash_worktree(repo_root: str, path: str) -> str:
    """Content+mode digest of one changed path, `missing` when it is gone."""
    full = os.path.join(repo_root, path)
    try:
        if os.path.islink(full):
            return "symlink:" + hashlib.sha256(os.readlink(full).encode(errors="surrogateescape")).hexdigest()
        with open(full, "rb") as handle:
            body = handle.read()
    except OSError:
        return "missing"
    mode = "x" if os.stat(full).st_mode & 0o111 else "-"
    return f"{mode}:" + hashlib.sha256(body).hexdigest()


def _changed_content(repo_root: str, entries: list[str]) -> dict[str, str]:
    """Per-path worktree digests for every path git reports as changed.

    The aggregate patch digests cannot attribute drift to a path, and the
    porcelain XY pair is coarse: a file already modified when the snapshot was
    taken keeps the same XY when it is modified AGAIN, so a reviewer edit to an
    already-dirty file left no per-path trace. That is exactly the state a
    mid-task parent tree is in, so per-path content is what makes attribution
    (and the drift report itself) trustworthy there."""
    return {path: _hash_worktree(repo_root, path) for path in _changed_paths(entries)}


def _hash_untracked(repo_root: str, entries: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for entry in entries:
        if not entry.startswith("? "):
            continue
        path = entry[2:]
        try:
            with open(os.path.join(repo_root, path), "rb") as handle:
                result[path] = hashlib.sha256(handle.read()).hexdigest()
        except OSError:
            result[path] = "unreadable"
    return result


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_window(window_id: str | None = None) -> dict:
    """A review window is the interval a snapshot certifies. Verifying against a
    snapshot from a different window compares two unrelated intervals, so the id
    is recorded at snapshot time and checked at verify time."""
    opened_at = _now_iso()
    return {
        "id": window_id or f"w-{opened_at.replace(':', '').replace('-', '')}-{os.getpid()}",
        "opened_at": opened_at,
    }


def build_snapshot(repo_root: str, window: dict | None = None) -> dict:
    entries = _status_entries(repo_root)
    return {
        "window": window if window is not None else new_window(),
        "head": _git_text(repo_root, "rev-parse", "HEAD").strip(),
        "status": entries,
        "staged_patch_sha256": hashlib.sha256(
            _git_bytes(repo_root, "diff", "--cached", "--binary")
        ).hexdigest(),
        "worktree_patch_sha256": hashlib.sha256(
            _git_bytes(repo_root, "diff", "--binary")
        ).hexdigest(),
        "changed_content": _changed_content(repo_root, entries),
        "untracked": _hash_untracked(repo_root, entries),
    }
