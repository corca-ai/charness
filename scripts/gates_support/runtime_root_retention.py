#!/usr/bin/env python3
"""Retention for the per-repo runtime tree `<base>/charness/runtime/<key>/` (#787).

`scripts/runtime_bootstrap.py` gives every repo one key under `charness/runtime/`
and routes caches, temp, coverage, and `task run` lanes there. Until 2026-09-03
nothing reclaimed any of it: the tree measured 340 GB across 1,871 keys, 266 GB of
it finished lane records that kept their worktrees, 41 GB nested fixture-repo keys
inside this repo's own `xdg-cache`, and 1,867 keys whose repo no longer existed.
The `pytest-tmp` subtree had a rule (`standing_pytest_basetemp.py`); the key and
its other subtrees had none. This module is the rule for the rest, and the
operator's decision on 2026-09-03 was that it deletes directly, with a log, and
without a report-first step.

What it removes, and what it never touches:

- `task-run/<id>/worktree` and `task-run/<id>/runtime` of a FINISHED lane (its
  `result.json` reads a terminal phase). `result.json` and the lane's logs stay.
  A worktree carrying uncommitted edits is salvaged first: `uncommitted.patch`
  (`git diff HEAD --binary`) and `uncommitted-untracked.tar` beside the result,
  verified with `git apply --check -R` before the worktree goes; a salvage that
  cannot be verified keeps the worktree and logs why. A receipt with
  `keep_worktree: true` keeps the worktree even after a verified salvage, because
  that flag is the producer saying the directory is still the named copy (#797).
  A linked worktree (``.git`` is a file) is unregistered with `git worktree
  remove` before the directory is removed, so `.git/worktrees/` does not keep a
  ghost entry.
- `xdg-cache/charness/runtime/<nested key>`: a key inside a key, the shape the
  bootstrap fix in #787 stops creating. Removed whole once idle.
- `pycache`, `coverage`, `tmp`, `ruff`, `npm`, `pip`, `pytest-cache`: removed
  whole once idle for `SUBTREE_MAX_AGE_DAYS`; they are rebuilt on demand.
- sibling keys under `charness/runtime/`: removed whole when the repo root the
  key recorded (`.charness-repo-root`, written by the bootstrap) no longer exists,
  or, for a key with no marker, when nothing under it moved for
  `LEGACY_KEY_MAX_AGE_DAYS`.

A lane whose result is not terminal, a key or subtree with an entry newer than
`ACTIVE_WINDOW_DAYS`, a `pytest-tmp` run holding its liveness lock, and this
run's own key are skipped, each with its reason in the log. Nothing outside the
`charness/runtime/` tree is ever a candidate: every path is checked to be inside
it before removal. `--dry-run` reports the same plan and removes nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tarfile
import time
from pathlib import Path
from typing import Any, Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import run_process  # noqa: E402
from scripts.gates_support import standing_pytest_basetemp as _basetemp  # noqa: E402
from scripts.runtime_bootstrap import (  # noqa: E402
    RUNTIME_KEYS_NAME,
    RUNTIME_TREE_NAME,
    runtime_root,
)
from scripts.yaml_output import emit_yaml  # noqa: E402

#: Anything touched inside this window is a live session's, whatever else is true.
ACTIVE_WINDOW_DAYS = 1.0
#: Rebuilt-on-demand subtrees are kept while a session keeps using them.
SUBTREE_MAX_AGE_DAYS = 14.0
LEGACY_KEY_MAX_AGE_DAYS = _basetemp.LEGACY_KEY_MAX_AGE_DAYS
REPO_ROOT_MARKER = _basetemp.REPO_ROOT_MARKER
IDLE_SUBTREES = ("pycache", "coverage", "tmp", "ruff", "npm", "pip", "pytest-cache")
LANE_RECORDS = "task-run"
NESTED_KEYS_REL = Path("xdg-cache") / RUNTIME_TREE_NAME / RUNTIME_KEYS_NAME
LOG_DIR_NAME = "retention"
SALVAGE_PATCH = "uncommitted.patch"
SALVAGE_TAR = "uncommitted-untracked.tar"
SALVAGE_RECORD = "uncommitted.json"
TERMINAL_PHASES = frozenset({"terminal"})

Log = Callable[[str], None]


def _now(now: float | None) -> float:
    return time.time() if now is None else now


def _tree_size_bytes(root: Path) -> int:
    return _basetemp._tree_size_bytes(root)


def _has_entry_newer_than(root: Path, cutoff: float) -> bool:
    return _basetemp._has_entry_newer_than(root, cutoff)


def _children(path: Path) -> list[Path]:
    """Sorted directory entries, or none when the directory cannot be read."""
    try:
        return sorted(path.iterdir())
    except OSError:
        return []


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def keys_root_of(key_root: Path) -> Path:
    """`<base>/charness/runtime` for a key, refusing a path that is not a key."""
    keys_root = key_root.parent
    if keys_root.name != RUNTIME_KEYS_NAME or keys_root.parent.name != RUNTIME_TREE_NAME:
        raise ValueError(f"{key_root} is not a charness runtime key")
    return keys_root


class Sweep:
    """One pass over one key and its siblings; every decision lands in `entries`."""

    def __init__(
        self,
        key_root: Path,
        *,
        now: float | None = None,
        dry_run: bool = False,
        log: Log | None = None,
        git: Callable[..., Any] | None = None,
        log_skips: bool = True,
    ) -> None:
        self.key_root = key_root.resolve()
        self.keys_root = keys_root_of(self.key_root)
        self.now = _now(now)
        self.dry_run = dry_run
        self.log = log
        #: A quiet pass on this repo's key skips over a thousand entries; the
        #: standing runner logs only what changed and one summary line, while the
        #: JSON log and the CLI keep every skip with its reason.
        self.log_skips = log_skips
        self.git = git if git is not None else self._git
        self.entries: list[dict[str, Any]] = []
        self.removed_bytes = 0

    # -- recording -------------------------------------------------------

    def _record(self, action: str, path: Path, reason: str, **extra: Any) -> None:
        entry = {"action": action, "path": str(path), "reason": reason, **extra}
        self.entries.append(entry)
        if self.log is not None and (self.log_skips or action != "skipped"):
            size = entry.get("bytes")
            size_text = f" ({size // (1024 * 1024)} MiB)" if isinstance(size, int) else ""
            self.log(f"{action} {path}{size_text}: {reason}")

    def _remove_tree(self, path: Path, reason: str, **extra: Any) -> bool:
        if not _inside(path, self.keys_root):
            self._record("refused", path, f"outside {self.keys_root}; never a candidate")
            return False
        size = _tree_size_bytes(path)
        action = "would-remove" if self.dry_run else "removed"
        if not self.dry_run:
            try:
                if (path / ".git").is_file():
                    from scripts.worktree.worktree_lifetime import unregister

                    unregister(path)
                if path.exists():
                    _rmtree_writable(path)
            except OSError as exc:
                self._record("failed", path, f"{reason}; removal failed: {exc}", bytes=size)
                return False
        self.removed_bytes += 0 if self.dry_run else size
        self._record(action, path, reason, bytes=size, **extra)
        return True

    # -- liveness --------------------------------------------------------

    def _active_cutoff(self) -> float:
        return self.now - ACTIVE_WINDOW_DAYS * 86400

    def _is_fresh(self, path: Path) -> bool:
        return _has_entry_newer_than(path, self._active_cutoff())

    # -- lanes -----------------------------------------------------------

    def _lane_result(self, record: Path) -> dict[str, Any] | None:
        result = record / "result.json"
        try:
            payload = json.loads(result.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return payload if isinstance(payload, dict) else None

    def sweep_lanes(self, key_root: Path | None = None) -> None:
        lanes = (key_root or self.key_root) / LANE_RECORDS
        for record in _children(lanes):
            if record.is_dir() and not record.is_symlink():
                self.sweep_lane(record)

    def sweep_lane(self, record: Path) -> None:
        worktree = record / "worktree"
        runtime = record / "runtime"
        if not worktree.exists() and not runtime.exists():
            return
        payload = self._lane_result(record)
        if payload is not None and payload.get("phase") in TERMINAL_PHASES:
            reason = f"finished lane ({payload.get('status')}); result.json and logs kept"
        else:
            state = (
                "no readable result.json"
                if payload is None
                else f"lane phase {payload.get('phase')!r} is not terminal"
            )
            if self._is_fresh(record):
                self._record("skipped", record, f"{state} and the record is fresh")
                return
            reason = f"{state} and the record is idle past the active window"
        if worktree.is_dir():
            salvage = salvage_uncommitted(worktree, record, git=self.git, dry_run=self.dry_run)
            if payload is not None and payload.get("keep_worktree") is True:
                extra = (
                    "; salvage written beside the result"
                    if salvage.get("status") in {"salvaged", "would-salvage"}
                    else ""
                )
                self._record(
                    "skipped",
                    worktree,
                    f"keep_worktree retains the named worktree{extra}",
                    salvage=salvage,
                )
            elif salvage.get("status") == "unverified":
                self._record("skipped", worktree, f"uncommitted edits could not be salvaged verifiably: {salvage.get('error')}")
                return
            else:
                self._remove_tree(worktree, reason, salvage=salvage)
        if runtime.exists() and not (payload is not None and payload.get("keep_worktree") is True):
            self._remove_tree(runtime, reason)

    # -- nested keys and idle subtrees -----------------------------------

    def sweep_nested_keys(self, key_root: Path | None = None) -> None:
        nested_root = (key_root or self.key_root) / NESTED_KEYS_REL
        for nested in _children(nested_root):
            if not nested.is_dir() or nested.is_symlink():
                continue
            self.sweep_lanes(nested)
            if self._is_fresh(nested):
                self._record("skipped", nested, "nested runtime key touched within the active window")
                continue
            self._remove_tree(nested, "runtime key nested inside another key; keys are siblings now")

    def sweep_idle_subtrees(self, key_root: Path | None = None) -> None:
        root = key_root or self.key_root
        cutoff = self.now - SUBTREE_MAX_AGE_DAYS * 86400
        for name in IDLE_SUBTREES:
            subtree = root / name
            if not subtree.is_dir() or subtree.is_symlink():
                continue
            if _has_entry_newer_than(subtree, cutoff):
                continue
            self._remove_tree(subtree, f"rebuilt-on-demand subtree idle for {SUBTREE_MAX_AGE_DAYS:g} days")

    # -- sibling keys ----------------------------------------------------

    def _key_is_active(self, key: Path) -> bool:
        for tmp_key in _children(key / _basetemp._KEY_ROOT_NAME):
            if tmp_key.is_dir() and _basetemp._key_is_active(tmp_key):
                return True
        return self._is_fresh(key)

    def sweep_sibling_keys(self) -> None:
        legacy_cutoff = self.now - LEGACY_KEY_MAX_AGE_DAYS * 86400
        for key in _children(self.keys_root):
            if key.is_symlink() or not key.is_dir() or key.resolve() == self.key_root:
                continue
            recorded = _read_marker(key)
            if recorded is not None and Path(recorded).exists():
                self.sweep_lanes(key)
                self.sweep_nested_keys(key)
                self.sweep_idle_subtrees(key)
                continue
            if self._key_is_active(key):
                self._record("skipped", key, "a run under this key is live or the key was touched within the active window")
                continue
            if recorded is None and _has_entry_newer_than(key, legacy_cutoff):
                self._record("skipped", key, f"no repo-root marker and an entry newer than {LEGACY_KEY_MAX_AGE_DAYS:g} days")
                continue
            reason = (
                f"recorded repo root {recorded} no longer exists"
                if recorded is not None
                else f"no repo-root marker and idle for {LEGACY_KEY_MAX_AGE_DAYS:g} days"
            )
            self._remove_tree(key, reason)

    # -- the whole pass --------------------------------------------------

    def run(self) -> dict[str, Any]:
        self.sweep_lanes()
        self.sweep_nested_keys()
        self.sweep_idle_subtrees()
        self.sweep_sibling_keys()
        return self.report()

    def report(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry["action"]] = counts.get(entry["action"], 0) + 1
        return {
            "schema": "charness.runtime-root-retention/v1",
            "key_root": str(self.key_root),
            "keys_root": str(self.keys_root),
            "dry_run": self.dry_run,
            "at": self.now,
            "counts": counts,
            "removed_bytes": self.removed_bytes,
            "entries": self.entries,
        }

    @staticmethod
    def _git(cwd: Path, *args: str) -> Any:
        return run_process(["git", *args], cwd=cwd, timeout_seconds=600)


def _read_marker(key: Path) -> str | None:
    """The recorded repo root: the key's own marker, else the older `pytest-tmp` one."""
    candidates = [key / REPO_ROOT_MARKER]
    candidates += [tmp_key / REPO_ROOT_MARKER for tmp_key in _children(key / _basetemp._KEY_ROOT_NAME)]
    for marker in candidates:
        text = _read_text(marker) if marker.is_file() else None
        if text is not None and text.strip():
            return text.strip()
    return None


def record_repo_root_marker(key_root: Path, repo_root: Path) -> None:
    """Name the repo this key hashes, once, so a later sweep can tell dead from quiet."""
    marker = key_root / REPO_ROOT_MARKER
    if marker.is_file():
        return
    try:
        key_root.mkdir(parents=True, exist_ok=True)
        marker.write_text(f"{repo_root}\n", encoding="utf-8")
    except OSError:
        pass


def _rmtree_writable(path: Path) -> None:
    """`rmtree` after restoring write bits: lane runtimes hold read-only manifests.

    69 of the hand sweep's removals first failed on exactly that (2026-09-03).
    """
    for parent, dirs, files in os.walk(path):
        for name in (*dirs, *files):
            target = os.path.join(parent, name)
            if not os.path.islink(target):
                os.chmod(target, 0o700 if os.path.isdir(target) else 0o600)
        os.chmod(parent, 0o700)
    shutil.rmtree(path)


def salvage_uncommitted(
    worktree: Path, record: Path, *, git: Callable[..., Any], dry_run: bool = False
) -> dict[str, Any]:
    """Keep a finished lane's uncommitted edits beside its result before the worktree goes.

    Returns `{"status": "clean"}` when HEAD carries everything, `"salvaged"` with the
    files written and their verification, or `"unverified"` with the error when the
    patch could not be proven to apply, in which case the caller keeps the worktree.
    """
    if not (worktree / ".git").exists():
        return {"status": "not-a-worktree"}
    head = git(worktree, "rev-parse", "HEAD")
    if head.returncode != 0:
        return {"status": "unverified", "error": f"rev-parse HEAD failed: {head.stderr.strip()}"}
    # `-z`: NUL-separated, unquoted paths. The human porcelain form quotes and
    # escapes a path with a space, quote, backslash, or non-ASCII byte, and a path
    # read back from that form need not name the file; the release critique for
    # 8.0.3 caught that the first cut would then have skipped the file silently and
    # still reported the salvage complete.
    status = git(worktree, "status", "--porcelain", "-z", "--untracked-files=all")
    if status.returncode != 0:
        return {"status": "unverified", "error": f"status failed: {status.stderr.strip()}"}
    lines = _porcelain_z_entries(status.stdout)
    if not lines:
        return {"status": "clean", "head": head.stdout.strip()}
    tracked = [line for line in lines if not line.startswith("??")]
    untracked = [line[3:] for line in lines if line.startswith("??")]
    result: dict[str, Any] = {"status": "salvaged", "head": head.stdout.strip(), "files": []}
    if dry_run:
        result["status"] = "would-salvage"
        result["tracked"] = len(tracked)
        result["untracked"] = len(untracked)
        return result
    if tracked:
        diff = git(worktree, "diff", "HEAD", "--binary")
        if diff.returncode != 0:
            return {"status": "unverified", "error": f"diff failed: {diff.stderr.strip()}"}
        patch = record / SALVAGE_PATCH
        patch.write_text(diff.stdout, encoding="utf-8")
        check = git(worktree, "apply", "--check", "-R", str(patch))
        if check.returncode != 0:
            return {
                "status": "unverified",
                "error": f"apply --check -R refused the salvaged patch: {check.stderr.strip()[-400:]}",
            }
        result["files"].append(str(patch))
        result["patch_verified"] = True
    if untracked:
        archive = record / SALVAGE_TAR
        missing = [rel for rel in untracked if not (worktree / rel).exists()]
        if missing:
            return {
                "status": "unverified",
                "error": f"untracked path(s) reported by git are not on disk: {', '.join(missing[:5])}",
            }
        with tarfile.open(archive, "w") as tar:
            for rel in untracked:
                tar.add(worktree / rel, arcname=rel)
        # Read the archive back: every untracked path git named is a member, or the
        # worktree stays.
        with tarfile.open(archive) as tar:
            members = set(tar.getnames())
        absent = [rel for rel in untracked if rel not in members and rel.rstrip("/") not in members]
        if absent:
            return {
                "status": "unverified",
                "error": f"salvage archive is missing {len(absent)} untracked path(s): {', '.join(absent[:5])}",
            }
        result["files"].append(str(archive))
        result["archive_members"] = len(members)
    (record / SALVAGE_RECORD).write_text(
        json.dumps(
            {"head": result["head"], "tracked": tracked, "untracked": untracked, "files": result["files"]},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result["files"].append(str(record / SALVAGE_RECORD))
    return result


#: The sweep runs on every standing pytest run and a quiet pass still lists every
#: skipped entry with its reason (about 300 KB on this repo's key), so the logs
#: are themselves bounded: the newest `SWEEP_LOG_KEEP` stay.
SWEEP_LOG_KEEP = 20


def _porcelain_z_entries(stdout: str) -> list[str]:
    """`XY path` entries from `git status --porcelain -z`.

    A rename entry is `XY new\0old\0`; the second record is the old name and is
    dropped so it is not read as a separate path.
    """
    records = stdout.split("\0")
    entries: list[str] = []
    skip_next = False
    for record in records:
        if skip_next:
            skip_next = False
            continue
        if not record:
            continue
        entries.append(record)
        if record[:1] in {"R", "C"} or record[1:2] in {"R", "C"}:
            skip_next = True
    return entries


def write_sweep_log(key_root: Path, report: dict[str, Any]) -> Path | None:
    log_dir = key_root / LOG_DIR_NAME
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / f"sweep-{int(report['at'])}.json"
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        logs = sorted(log_dir.glob("sweep-*.json"))
        for stale in logs[: max(0, len(logs) - SWEEP_LOG_KEEP)]:
            if stale != path:
                stale.unlink()
    except OSError:
        return None
    return path


def sweep_runtime_root(
    repo_root: Path,
    *,
    key_root: Path | None = None,
    now: float | None = None,
    dry_run: bool = False,
    log: Log | None = None,
    git: Callable[..., Any] | None = None,
    log_skips: bool = True,
) -> dict[str, Any]:
    """The whole pass for one repo's key, logged under `<key>/retention/`."""
    root = key_root if key_root is not None else runtime_root(repo_root)
    try:
        keys_root_of(root.resolve())
    except ValueError as exc:
        if log is not None:
            log(f"skipped: {exc}; an explicit CHARNESS_RUNTIME_ROOT has no sibling keys to sweep")
        return {
            "schema": "charness.runtime-root-retention/v1",
            "key_root": str(root),
            "keys_root": None,
            "dry_run": dry_run,
            "at": _now(now),
            "counts": {},
            "removed_bytes": 0,
            "entries": [],
            "log_path": None,
            "skipped": str(exc),
        }
    record_repo_root_marker(root, repo_root.resolve())
    sweep = Sweep(root, now=now, dry_run=dry_run, log=log, git=git, log_skips=log_skips)
    report = sweep.run()
    report["log_path"] = None if dry_run else _path_text(write_sweep_log(root, report))
    if log is not None:
        log(summary_line(report))
    return report


def summary_line(report: dict[str, Any]) -> str:
    counts = ", ".join(f"{k} {v}" for k, v in sorted(report["counts"].items())) or "nothing to do"
    mib = report["removed_bytes"] // (1024 * 1024)
    return (
        f"{counts}; {mib} MiB removed"
        + (" (dry run)" if report["dry_run"] else "")
        + (f"; log {report['log_path']}" if report.get("log_path") else "")
    )


def _path_text(path: Path | None) -> str | None:
    return None if path is None else str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--key-root", type=Path, default=None, help="Sweep this key instead of the repo's own.")
    parser.add_argument("--dry-run", action="store_true", help="Plan and log without removing anything.")
    parser.add_argument(
        "--verbose", action="store_true", help="Include every entry in the report on stdout."
    )
    args = parser.parse_args(argv)
    report = sweep_runtime_root(
        args.repo_root.resolve(),
        key_root=args.key_root,
        dry_run=args.dry_run,
        log=lambda message: print(f"runtime-root-retention: {message}", file=sys.stderr),
    )
    rendered = dict(report)
    if not args.verbose:
        rendered.pop("entries", None)
    rendered["summary"] = summary_line(report)
    emit_yaml(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
