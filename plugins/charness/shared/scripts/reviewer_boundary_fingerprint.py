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

``verify --repo-root <dir> [--before <file>] [--window-id <id>]
       [--parent-path <path>]... [--parent-head-moved]``
    Recompute the fingerprint and diff it against the snapshot, reporting
    concrete drift (``head``, ``index``, ``worktree``, ``untracked-added``,
    ``untracked-removed``, ``untracked-modified``) with the affected path where
    one is identifiable. The drift list is fail-closed but not exhaustive: it
    names at least one drifted surface, not necessarily every one. Exit 0
    clean, 1 on undeclared drift, 2 on a usage error (missing/unreadable
    snapshot file, or a snapshot from a different review window).

Attribution, and what this proof does NOT establish. Git records that the
shared tree changed, never who changed it. A parent that applies review
findings before running ``verify`` gets drift on its own edits, shaped exactly
like a reviewer boundary violation -- an unattributable ``ok: false`` teaches
the parent to discount the signal, which is how a real violation later gets
waved through. Two bindings keep the verdict meaningful:

``--window-id``
    ``snapshot`` stamps a review-window id (generated unless supplied) and
    ``verify`` refuses a snapshot from a different window rather than
    answering across it.

``--parent-path`` / ``--parent-staged`` / ``--parent-head-moved``
    The parent declares the surfaces it changed itself inside the window.
    Declared drift is reported separately as ``parent_attributed_drift`` and
    does not fail the verify; anything undeclared still does. Declarations are
    scoped by kind: ``--parent-path`` covers worktree content and never excuses
    index drift, which needs ``--parent-staged``. The declaration is parent
    testimony, not proof -- an attributed pass exits **3**, not 0, and prints
    the full ``parent_declared`` set, so it cannot be quoted as an undeclared
    clean run. Drift with no identifiable path is never attributable and always
    fails.

State capture lives in the sibling ``reviewer_boundary_state.py``.

Scope note: gitignored files are intentionally invisible to this fingerprint --
they cannot land in a closeout commit, so they are not a reviewer-boundary
concern this script needs to cover.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

_SNAPSHOT_SUBDIR = os.path.join(".charness", "reviewer-boundary")
_SNAPSHOT_FILENAME = "snapshot.json"
_ATTRIBUTION_NOTE = (
    "git proves the shared tree changed, never who changed it; parent-declared paths are "
    "recorded testimony, and undeclared drift is a boundary signal only for a window in "
    "which the parent made no writes"
)


def _load_state_module():
    """Load the sibling capture module by path, not by package import: this file
    runs from the repo AND from an installed plugin's `shared/scripts/`, where no
    package context exists and the cwd is the consuming repository."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviewer_boundary_state.py")
    spec = importlib.util.spec_from_file_location("reviewer_boundary_state", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"reviewer boundary state module not found beside this script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_STATE = _load_state_module()
FingerprintError = _STATE.FingerprintError
build_snapshot = _STATE.build_snapshot
new_window = _STATE.new_window
_status_path_map = _STATE._status_path_map


def _default_snapshot_path(repo_root: str) -> str:
    return os.path.join(repo_root, _SNAPSHOT_SUBDIR, _SNAPSHOT_FILENAME)


def _index_worktree_drift(before: dict, after: dict) -> list[dict]:
    before_map = _status_path_map(before["status"])
    after_map = _status_path_map(after["status"])
    before_content = before.get("changed_content", {})
    after_content = after.get("changed_content", {})
    content_comparable = "changed_content" in before and "changed_content" in after
    drift: list[dict] = []
    for path in sorted(set(before_map) | set(after_map)):
        before_xy = before_map.get(path, "..")
        after_xy = after_map.get(path, "..")
        if before_xy[0] != after_xy[0]:
            drift.append({"kind": "index", "path": path})
        if before_xy[1] != after_xy[1]:
            drift.append({"kind": "worktree", "path": path})
        elif content_comparable and before_content.get(path) != after_content.get(path):
            # Same XY, different bytes: an already-dirty file edited again.
            drift.append({"kind": "worktree", "path": path})
    # The aggregate digests name no path, so they can neither be attributed nor
    # tell the parent what moved; they stay a backstop for whatever the per-path
    # comparison above cannot see, and only when it saw nothing at all.
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


def split_parent_attributed(
    drift: list[dict],
    parent_paths: list[str],
    parent_head_moved: bool,
    parent_staged: list[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Partition drift into (undeclared, parent-attributed).

    Declarations are scoped by KIND, not only by path. ``--parent-path``
    excuses worktree drift; index drift needs its own ``--parent-staged``,
    because index mutation is the one class an enveloped read-only reviewer
    can never legitimately produce and the staged-reversion trap it hides is
    the reason this rail exists. A parent that edited a file it also told a
    reviewer to read would otherwise excuse that reviewer's `git add` of the
    same path with one flag.

    A `head` entry is attributable only through the explicit
    ``--parent-head-moved`` declaration, and a pathless entry (the aggregate
    patch-digest backstop, which names no surface) is never attributable: an
    unnamed change cannot be matched against a parent's declaration, so it
    stays fail-closed."""
    declared = {"worktree": set(parent_paths), "index": set(parent_staged or [])}
    undeclared: list[dict] = []
    attributed: list[dict] = []
    for entry in drift:
        if entry["kind"] == "head":
            (attributed if parent_head_moved else undeclared).append(entry)
        elif entry["path"] is not None and entry["path"] in declared.get(entry["kind"], set()):
            attributed.append(entry)
        elif entry["kind"].startswith("untracked") and entry["path"] in declared["worktree"]:
            attributed.append(entry)
        else:
            undeclared.append(entry)
    return undeclared, attributed


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
    snapshot = build_snapshot(repo_root, new_window(args.window_id))
    # A stale snapshot from a prior review round is itself untracked in repos
    # that do not gitignore it; without this drop, the documented re-snapshot
    # flow would report the tool's own file as untracked-removed drift.
    _drop_self(snapshot, repo_root, out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2)
        handle.write("\n")
    print(
        json.dumps(
            {"ok": True, "out": out_path, "head": snapshot["head"], "window": snapshot["window"]}
        )
    )
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

    missing = [key for key in ("head", "status", "staged_patch_sha256", "worktree_patch_sha256", "untracked") if key not in before]
    if missing:
        # A snapshot that parses but is truncated must refuse as JSON, not die on
        # a KeyError traceback with nothing on stdout for the caller to read.
        print(json.dumps({"ok": False, "error": f"snapshot file {before_path} is missing keys: {missing}", "before_path": before_path}))
        return 2

    window = before.get("window") or {}
    if args.window_id and window.get("id") != args.window_id:
        # Refusing beats answering: a snapshot from another window certifies a
        # different interval, so its drift says nothing about this review.
        print(json.dumps({
            "ok": False,
            "error": (
                f"snapshot records review window "
                f"{window.get('id') or 'none (snapshot predates window binding)'}, not the "
                f"requested {args.window_id!r}; re-snapshot before this review window"
            ),
            "before_path": before_path,
            "window": window,
        }))
        return 2

    after = build_snapshot(repo_root, window or None)
    _drop_self(after, repo_root, before_path)
    drift = compare_snapshots(before, after)
    parent_paths = list(args.parent_path or [])
    parent_staged = list(args.parent_staged or [])
    undeclared, attributed = split_parent_attributed(
        drift, parent_paths, args.parent_head_moved, parent_staged
    )
    # floor-addition-restraint: keep — enforcement teeth requested by tracked issue #428 after three recorded recurrences
    ok = not undeclared
    declared_anything = bool(parent_paths or parent_staged or args.parent_head_moved)
    verdict = "boundary-drift" if undeclared else ("parent-attributed" if declared_anything else "clean")
    print(json.dumps({
        "ok": ok,
        "verdict": verdict,
        "drift": undeclared,
        "parent_attributed_drift": attributed,
        "parent_declared": {
            "paths": sorted(set(parent_paths)),
            "staged_paths": sorted(set(parent_staged)),
            "head_moved": args.parent_head_moved,
        },
        # A declared path that never drifted is reported, not silently dropped: it
        # means the parent's account of the window does not match the tree.
        "unmatched_parent_paths": sorted(
            (set(parent_paths) | set(parent_staged))
            - {entry["path"] for entry in attributed if entry["path"]}
        ),
        "window": window,
        # A snapshot taken before per-path capture existed cannot be compared by
        # content, so an edit to an already-dirty file is invisible in that run.
        # Say which sensitivity the verdict actually had rather than let a
        # weaker comparison read like the full one.
        "content_comparison": "per-path" if "changed_content" in before else "unavailable-legacy-snapshot",
        "attribution": _ATTRIBUTION_NOTE,
        "before_path": before_path,
    }))
    if not ok:
        return 1
    # Exit 3, not 0, when the clean result rests on a parent declaration. Every
    # closeout in this repo quotes `{"ok": true, "drift": []}` as proof of a clean
    # review; an attributed pass prints exactly that shape, so the exit code is
    # what stops it from being cited as an undeclared clean run.
    return 3 if verdict == "parent-attributed" else 0


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
    snap.add_argument("--window-id", default=None, help="Review-window id this snapshot opens (default: generated)")
    snap.set_defaults(func=_cmd_snapshot)

    verify = subparsers.add_parser("verify", help="Diff the current fingerprint against a prior snapshot.")
    verify.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    verify.add_argument("--before", default=None, help="Snapshot path to compare against (default: .charness/reviewer-boundary/snapshot.json)")
    verify.add_argument("--window-id", default=None, help="Review window this verify certifies; a snapshot from another window is refused")
    verify.add_argument("--parent-path", action="append", default=None,
                        help="Exact repo-relative path (as git prints it) whose WORKTREE content the "
                             "PARENT changed inside the window (repeatable); drift there is reported "
                             "as parent-attributed instead of failing")
    verify.add_argument("--parent-staged", action="append", default=None,
                        help="Exact repo-relative path the PARENT staged inside the window (repeatable). "
                             "Index drift needs this separate declaration: --parent-path never excuses it")
    verify.add_argument("--parent-head-moved", action="store_true",
                        help="Declare that the parent moved HEAD inside the window")
    verify.set_defaults(func=_cmd_verify)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FingerprintError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
