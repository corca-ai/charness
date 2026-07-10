#!/usr/bin/env python3
"""Parent-side worktree+index integrity proof around a shared-tree reviewer (#428).

Three recorded reviewer-boundary violations motivate this: a bounded fresh-eye
reviewer staged and committed content, one spawned an unauthorized child agent,
one modified docs despite a no-write brief. Prose rules
(``skills/shared/references/fresh-eye-subagent-review.md``, "Shared-Tree Git
Hygiene") and the narrow ``check_staged_reversion`` pre-commit gate did not stop
the recurrence because both trust the reviewer's own report of what it touched.

This script instead fingerprints the ENTIRE worktree+index state before a
reviewer runs and diffs it after, so drift is caught regardless of what the
reviewer claims to have done and regardless of mutation shape (a staged
reversion is only one shape; an unrelated doc edit or a new untracked file are
others).

Two subcommands:

``snapshot --repo-root <dir> [--out <file>]``
    Capture ``HEAD``, the full ``git status --porcelain=v2`` entry set, sha256
    of the staged and unstaged patch bytes, and a content hash per untracked
    file. Default output: ``<repo-root>/.charness/reviewer-boundary/
    snapshot.json`` -- runtime state, not committed (``.charness/`` is a
    generated/scratch surface, unlike the tracked snapshot the reviewer is
    being checked against).

``verify --repo-root <dir> [--before <file>]``
    Recompute the fingerprint and diff it against the snapshot, reporting
    concrete drift (``head``, ``index``, ``worktree``, ``untracked-added``,
    ``untracked-removed``, ``untracked-modified``) with the affected path where
    one is identifiable. The drift list is fail-closed but not exhaustive: it
    names at least one drifted surface, not necessarily every one. Exit 0
    clean, 1 on any drift, 2 on a usage error (missing/unreadable snapshot
    file).

Scope note: gitignored files are intentionally invisible to this fingerprint --
they cannot land in a closeout commit, so they are not a reviewer-boundary
concern this script needs to cover.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

_SNAPSHOT_SUBDIR = os.path.join(".charness", "reviewer-boundary")
_SNAPSHOT_FILENAME = "snapshot.json"


class FingerprintError(Exception):
    """A usage-level failure: bad repo root, unreadable/corrupt snapshot file."""


def _default_snapshot_path(repo_root: str) -> str:
    return os.path.join(repo_root, _SNAPSHOT_SUBDIR, _SNAPSHOT_FILENAME)


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


def build_snapshot(repo_root: str) -> dict:
    entries = _status_entries(repo_root)
    return {
        "head": _git_text(repo_root, "rev-parse", "HEAD").strip(),
        "status": entries,
        "staged_patch_sha256": hashlib.sha256(
            _git_bytes(repo_root, "diff", "--cached", "--binary")
        ).hexdigest(),
        "worktree_patch_sha256": hashlib.sha256(
            _git_bytes(repo_root, "diff", "--binary")
        ).hexdigest(),
        "untracked": _hash_untracked(repo_root, entries),
    }


def _index_worktree_drift(before: dict, after: dict) -> list[dict]:
    before_map = _status_path_map(before["status"])
    after_map = _status_path_map(after["status"])
    drift: list[dict] = []
    for path in sorted(set(before_map) | set(after_map)):
        before_xy = before_map.get(path, "..")
        after_xy = after_map.get(path, "..")
        if before_xy[0] != after_xy[0]:
            drift.append({"kind": "index", "path": path})
        if before_xy[1] != after_xy[1]:
            drift.append({"kind": "worktree", "path": path})
    if not drift:
        if before["staged_patch_sha256"] != after["staged_patch_sha256"]:
            drift.append({"kind": "index", "path": None})
        if before["worktree_patch_sha256"] != after["worktree_patch_sha256"]:
            drift.append({"kind": "worktree", "path": None})
    return drift


def _untracked_drift(before: dict, after: dict) -> list[dict]:
    before_map, after_map = before["untracked"], after["untracked"]
    drift: list[dict] = []
    for path in sorted(set(after_map) - set(before_map)):
        drift.append({"kind": "untracked-added", "path": path})
    for path in sorted(set(before_map) - set(after_map)):
        drift.append({"kind": "untracked-removed", "path": path})
    for path in sorted(set(before_map) & set(after_map)):
        if before_map[path] != after_map[path]:
            drift.append({"kind": "untracked-modified", "path": path})
    return drift


def compare_snapshots(before: dict, after: dict) -> list[dict]:
    drift: list[dict] = []
    if before["head"] != after["head"]:
        drift.append({"kind": "head", "path": None})
    drift.extend(_index_worktree_drift(before, after))
    drift.extend(_untracked_drift(before, after))
    return drift


def _drop_self(snapshot: dict, repo_root: str, snapshot_path: str) -> None:
    """Writing the snapshot file necessarily creates it as a new untracked path
    (unless the caller's ``.gitignore`` already excludes it); without this, the
    tool's own bookkeeping file would fail every ``verify`` regardless of
    reviewer behavior. Drop it from the freshly-computed fingerprint before
    comparison rather than relying on ``.gitignore`` state."""
    rel = os.path.relpath(snapshot_path, repo_root).replace(os.sep, "/")
    snapshot["untracked"].pop(rel, None)


def _cmd_snapshot(args: argparse.Namespace) -> int:
    repo_root = os.path.abspath(args.repo_root)
    out_path = os.path.abspath(args.out) if args.out else _default_snapshot_path(repo_root)
    snapshot = build_snapshot(repo_root)
    # A stale snapshot from a prior review round is itself untracked in repos
    # that do not gitignore it; without this drop, the documented re-snapshot
    # flow would report the tool's own file as untracked-removed drift.
    _drop_self(snapshot, repo_root, out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"ok": True, "out": out_path, "head": snapshot["head"]}))
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    repo_root = os.path.abspath(args.repo_root)
    before_path = os.path.abspath(args.before) if args.before else _default_snapshot_path(repo_root)
    if not os.path.isfile(before_path):
        # floor-addition-restraint: keep — enforcement teeth requested by tracked issue #428 after three recorded recurrences
        print(json.dumps({"ok": False, "error": f"snapshot file not found: {before_path}", "before_path": before_path}))
        return 2
    try:
        with open(before_path, encoding="utf-8") as handle:
            before = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        # floor-addition-restraint: keep — enforcement teeth requested by tracked issue #428 after three recorded recurrences
        print(json.dumps({"ok": False, "error": f"unreadable snapshot file {before_path}: {exc}", "before_path": before_path}))
        return 2

    after = build_snapshot(repo_root)
    _drop_self(after, repo_root, before_path)
    drift = compare_snapshots(before, after)
    # floor-addition-restraint: keep — enforcement teeth requested by tracked issue #428 after three recorded recurrences
    ok = not drift
    print(json.dumps({"ok": ok, "drift": drift, "before_path": before_path}))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Parent-side worktree+index integrity fingerprint around a shared-tree "
            "bounded reviewer (#428): snapshot before, verify after, never trust "
            "reviewer self-report."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    snap = subparsers.add_parser("snapshot", help="Capture the current worktree+index fingerprint.")
    snap.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    snap.add_argument("--out", default=None, help="Output path (default: .charness/reviewer-boundary/snapshot.json)")
    snap.set_defaults(func=_cmd_snapshot)

    verify = subparsers.add_parser("verify", help="Diff the current fingerprint against a prior snapshot.")
    verify.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    verify.add_argument("--before", default=None, help="Snapshot path to compare against (default: .charness/reviewer-boundary/snapshot.json)")
    verify.set_defaults(func=_cmd_verify)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FingerprintError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
