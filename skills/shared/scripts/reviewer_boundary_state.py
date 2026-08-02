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


SOURCE_BLOB_DIRNAME = "blobs"
SOURCE_BLOB_SUFFIXES = (".py",)
SOURCE_BLOB_MAX_BYTES = 512 * 1024


def _capture_source_blobs(repo_root: str, snapshot_dir: str, entries: list[str]) -> dict[str, str]:
    """Content-address the Python sources a reviewer is about to read.

    The digests above answer "did this path change"; they cannot answer "change
    from WHAT". That second question is the one a repair needs: the baseline for
    a function created earlier in the same slice is not any committed ref -- at
    commit granularity it is simply a new function -- it is the version the
    reviewer read. Nothing else in the repo records that, so it is recorded here.

    Python only, deliberately: the consumer is a callable-level parity harness,
    and capturing every changed artifact would grow a machine-local cache for
    files nothing can compare. A path absent from the returned map was not
    captured; that is not the same as unchanged, and callers must not read it so.
    """
    blob_dir = os.path.join(snapshot_dir, SOURCE_BLOB_DIRNAME)
    captured: dict[str, str] = {}
    paths = set(_changed_paths(entries))
    paths.update(entry[2:] for entry in entries if entry.startswith("? "))
    for path in sorted(paths):
        if not path.endswith(SOURCE_BLOB_SUFFIXES):
            continue
        full = os.path.join(repo_root, path)
        try:
            if os.path.islink(full) or os.path.getsize(full) > SOURCE_BLOB_MAX_BYTES:
                continue
            with open(full, "rb") as handle:
                body = handle.read()
        except OSError:
            continue
        key = hashlib.sha256(body).hexdigest()
        try:
            os.makedirs(blob_dir, exist_ok=True)
            blob_path = os.path.join(blob_dir, key)
            if not os.path.exists(blob_path):
                with open(blob_path, "wb") as handle:
                    handle.write(body)
        except OSError:
            continue
        captured[path] = key
    return captured


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


def build_snapshot(repo_root: str, window: dict | None = None, snapshot_dir: str | None = None) -> dict:
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
        "source_blobs": (
            _capture_source_blobs(repo_root, snapshot_dir, entries) if snapshot_dir else {}
        ),
    }
