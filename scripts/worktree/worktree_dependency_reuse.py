"""Reuse an already-installed dependency tree instead of re-running the installer.

Owned by worktree preparation (#792). On copy-on-write filesystems a fresh
worktree can clone the parent's `node_modules` cheaply; on ext4 with npm there
was no reuse path at all, so every `task run` lane paid a full `npm ci`. This
module gives `charness worktree prepare` one strategy, tried in order:

1. the parent (source) tree, when its lockfile digest matches the worktree's
   lockfile and the install directory is present;
2. the runtime cache keyed by the lockfile digest, populated after a fresh
   install succeeded in some earlier worktree.

Each candidate is linked with `cp --reflink=always` first and `cp -al`
(hard links) second. Anything else -- no candidate, cross-device, a tool that
refuses -- leaves the worktree untouched and the declared install command runs
as before. The result records which path was taken so the operator can read it
from the prepare payload (and `task run`'s `result.json`) instead of `pstree`.

Hard links share inodes with the source tree, and a cache entry is itself a
hard-link copy of the first install that seeded it, so the donor worktree, the
cache, and every later worktree linked from it share one set of files. Package
managers replace files rather than editing them in place, so an install in a
lane leaves the others intact; a tool that rewrites a file inside the install
directory in place reaches all of them. Recovery is deleting the cache entry
(`cache_entry`) and preparing with `--no-dependency-reuse`. The manifest opt-in
is where a consumer accepts that.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
TIMEOUT_EXIT_CODE = _subprocess_guard.TIMEOUT_EXIT_CODE

CACHE_TREE_NAME = "tree"
CACHE_META_NAME = "meta.json"
CACHE_DIR_NAME = "worktree-deps"
STRATEGY_NONE = "none"
STRATEGY_REFLINK = "reflink"
STRATEGY_HARDLINK = "hardlink"
ORIGIN_PARENT = "parent"
ORIGIN_CACHE = "cache"


@dataclass(frozen=True)
class ReuseSpec:
    command_id: str
    lockfile: str
    directory: str

    @classmethod
    def from_manifest(cls, prepare: dict[str, Any] | None) -> ReuseSpec | None:
        raw = (prepare or {}).get("dependency_reuse")
        if not isinstance(raw, dict):
            return None
        return cls(
            command_id=str(raw.get("command_id")),
            lockfile=str(raw.get("lockfile")),
            directory=str(raw.get("directory")),
        )


def validate_dependency_reuse(prepare: dict[str, Any], errors: list[str]) -> None:
    raw = prepare.get("dependency_reuse")
    if raw is None:
        return
    label = "manifest.prepare.dependency_reuse"
    if not isinstance(raw, dict):
        errors.append(f"{label} must be a mapping")
        return
    for key in ("command_id", "lockfile", "directory"):
        value = raw.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{label}.{key} must be a non-empty string")
    for key in ("lockfile", "directory"):
        value = raw.get(key)
        if isinstance(value, str) and value and not _is_relative_inside(value):
            errors.append(f"{label}.{key} must be a relative path inside the worktree")
    command_id = raw.get("command_id")
    if isinstance(command_id, str) and command_id:
        matches = sum(
            1
            for entry in prepare.get("commands") or []
            if isinstance(entry, dict) and entry.get("id") == command_id
        )
        if matches == 0:
            errors.append(f"{label}.command_id {command_id!r} names no prepare command id")
        elif matches > 1:
            errors.append(
                f"{label}.command_id {command_id!r} names {matches} prepare commands; "
                "reuse replaces exactly one"
            )


def _is_relative_inside(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and value not in {"", "."}


def lockfile_digest(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def runtime_fingerprint() -> str:
    """Platform and architecture: a native module built here does not load elsewhere.
    Interpreter and package-manager versions are not folded in; a runtime upgrade
    that changes a native ABI needs the entry removed (documented residual)."""
    return f"{sys.platform}/{platform.machine()}"


def cache_entry(cache_root: Path, digest: str, spec: ReuseSpec) -> Path:
    """One cache entry per (lockfile digest, install directory, platform/arch)."""
    key = hashlib.sha256(
        f"{digest}\n{spec.directory}\n{runtime_fingerprint()}".encode("utf-8")
    ).hexdigest()
    return cache_root / key


def disabled_result(spec: ReuseSpec, *, reason: str) -> dict[str, Any]:
    return _result(
        strategy=STRATEGY_NONE, reason=reason, command_id=spec.command_id, directory=spec.directory
    )


def _result(
    *,
    strategy: str,
    origin: str | None = None,
    source: Path | None = None,
    digest: str | None = None,
    reason: str | None = None,
    duration_ms: int = 0,
    attempts: list[dict[str, Any]] | None = None,
    command_id: str,
    directory: str,
) -> dict[str, Any]:
    return {
        "command_id": command_id,
        "directory": directory,
        "strategy": strategy,
        "origin": origin,
        "source": str(source) if source is not None else None,
        "lockfile_digest": digest,
        "reason": reason,
        "duration_ms": duration_ms,
        "attempts": attempts or [],
    }


def _run(argv: list[str], timeout_seconds: int) -> tuple[int | None, str]:
    try:
        completed = run_process(argv, cwd=Path.cwd(), timeout_seconds=timeout_seconds)
    except FileNotFoundError as exc:
        return None, f"command not found: {exc.filename or argv[0]}"
    if completed.returncode == TIMEOUT_EXIT_CODE:
        return None, f"timed out after {timeout_seconds}s"
    lines = (completed.stderr or "").strip().splitlines()
    return completed.returncode, (lines[-1] if lines else "")[-300:]


def _first_regular_file(root: Path) -> Path | None:
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            return path
    return None


def _reflink_supported(source: Path, destination_parent: Path) -> tuple[bool, str]:
    """Clone ONE file before the tree: on ext4 `--reflink=always` fails per file,
    so a whole-tree attempt would spend a full walk to learn what one file says."""
    probe_source = _first_regular_file(source)
    if probe_source is None:
        return False, "no regular file to probe"
    probe = destination_parent / f".charness-reflink-probe-{os.getpid()}"
    try:
        exit_code, stderr = _run(
            ["cp", "--reflink=always", str(probe_source), str(probe)], timeout_seconds=30
        )
    finally:
        probe.unlink(missing_ok=True)
    return exit_code == 0, stderr


def _link_tree(
    source: Path, destination: Path, *, timeout_seconds: int
) -> tuple[str | None, list[dict[str, Any]]]:
    """Link `source` to `destination` atomically; return the strategy that held."""
    attempts: list[dict[str, Any]] = []
    staging = destination.parent / f".{destination.name}.charness-reuse-{os.getpid()}"
    strategies = [(STRATEGY_HARDLINK, ["-al"])]
    supported, detail = _reflink_supported(source, destination.parent)
    if supported:
        strategies.insert(0, (STRATEGY_REFLINK, ["-a", "--reflink=always"]))
    else:
        attempts.append({"strategy": STRATEGY_REFLINK, "ok": False, "detail": detail})
    for strategy, flags in strategies:
        _remove_tree(staging)
        exit_code, stderr = _run(
            ["cp", *flags, str(source), str(staging)], timeout_seconds=timeout_seconds
        )
        if exit_code == 0:
            try:
                os.rename(staging, destination)
            except OSError as exc:
                _remove_tree(staging)
                attempts.append({"strategy": strategy, "ok": False, "detail": str(exc)})
                return None, attempts
            attempts.append({"strategy": strategy, "ok": True})
            return strategy, attempts
        attempts.append(
            {"strategy": strategy, "ok": False, "detail": stderr or f"exit {exit_code}"}
        )
    _remove_tree(staging)
    return None, attempts


def _remove_tree(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)


def _cache_matches(entry: Path, digest: str, spec: ReuseSpec) -> bool:
    meta = entry / CACHE_META_NAME
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        isinstance(data, dict)
        and data.get("lockfile_digest") == digest
        and data.get("directory") == spec.directory
        and data.get("runtime") == runtime_fingerprint()
        and (entry / CACHE_TREE_NAME).is_dir()
    )


def attempt_reuse(
    target_root: Path,
    spec: ReuseSpec,
    *,
    source_root: Path | None,
    cache_root: Path | None,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    """Populate the worktree's install directory from a matching installed tree."""
    started = time.monotonic()
    target_root = target_root.resolve()
    destination = target_root / spec.directory
    base = dict(command_id=spec.command_id, directory=spec.directory)
    if destination.exists() or destination.is_symlink():
        return _result(strategy=STRATEGY_NONE, reason="install directory already present", **base)
    digest = lockfile_digest(target_root / spec.lockfile)
    if digest is None:
        return _result(
            strategy=STRATEGY_NONE, reason=f"lockfile {spec.lockfile} unreadable", **base
        )

    candidates: list[tuple[str, Path, str | None]] = []
    if source_root is not None:
        source_root = source_root.resolve()
        if source_root == target_root:
            candidates.append((ORIGIN_PARENT, source_root, "parent is the worktree itself"))
        elif lockfile_digest(source_root / spec.lockfile) != digest:
            candidates.append((ORIGIN_PARENT, source_root, "parent lockfile digest differs"))
        elif not (source_root / spec.directory).is_dir():
            candidates.append((ORIGIN_PARENT, source_root, "parent has no install directory"))
        else:
            candidates.append((ORIGIN_PARENT, source_root / spec.directory, None))
    if cache_root is not None:
        entry = cache_entry(cache_root, digest, spec)
        if _cache_matches(entry, digest, spec):
            candidates.append((ORIGIN_CACHE, entry / CACHE_TREE_NAME, None))
        else:
            candidates.append((ORIGIN_CACHE, entry, "no cache entry for this lockfile digest"))

    attempts: list[dict[str, Any]] = []
    for origin, path, decline_reason in candidates:
        if decline_reason is not None:
            attempts.append({"origin": origin, "path": str(path), "declined": decline_reason})
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        strategy, link_attempts = _link_tree(path, destination, timeout_seconds=timeout_seconds)
        if (
            strategy is not None
            and origin == ORIGIN_PARENT
            and source_root is not None
            and lockfile_digest(source_root / spec.lockfile) != digest
        ):
            # The parent moved under the copy: the linked tree may mix two installs.
            _remove_tree(destination)
            link_attempts.append(
                {"strategy": strategy, "ok": False, "detail": "parent lockfile changed during link"}
            )
            strategy = None
        attempts.append({"origin": origin, "path": str(path), "link": link_attempts})
        if strategy is not None:
            return _result(
                strategy=strategy,
                origin=origin,
                source=path,
                digest=digest,
                duration_ms=int((time.monotonic() - started) * 1000),
                attempts=attempts,
                **base,
            )
    return _result(
        strategy=STRATEGY_NONE,
        digest=digest,
        reason="no linkable installed tree; the declared install command runs",
        duration_ms=int((time.monotonic() - started) * 1000),
        attempts=attempts,
        **base,
    )


def seed_cache(
    target_root: Path,
    spec: ReuseSpec,
    *,
    cache_root: Path | None,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    """After a fresh install, hard-link the tree into the cache for later worktrees."""
    started = time.monotonic()
    target_root = target_root.resolve()
    installed = target_root / spec.directory
    payload: dict[str, Any] = {"seeded": False, "entry": None, "reason": None, "duration_ms": 0}
    if cache_root is None:
        payload["reason"] = "no cache root"
        return payload
    if not installed.is_dir():
        payload["reason"] = "install directory absent after the install command"
        return payload
    digest = lockfile_digest(target_root / spec.lockfile)
    if digest is None:
        payload["reason"] = f"lockfile {spec.lockfile} unreadable"
        return payload
    entry = cache_entry(cache_root, digest, spec)
    payload["entry"] = str(entry)
    if _cache_matches(entry, digest, spec):
        payload["reason"] = "cache entry already present"
        return payload
    staging = entry.parent / f".{entry.name}.seed-{os.getpid()}"
    _remove_tree(staging)
    try:
        staging.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        payload["reason"] = f"cache root not writable: {exc}"
        return payload
    exit_code, stderr = _run(
        ["cp", "-al", str(installed), str(staging / CACHE_TREE_NAME)],
        timeout_seconds=timeout_seconds,
    )
    if exit_code != 0:
        _remove_tree(staging)
        payload["reason"] = f"hard-link into cache failed: {stderr or f'exit {exit_code}'}"
        payload["duration_ms"] = int((time.monotonic() - started) * 1000)
        return payload
    (staging / CACHE_META_NAME).write_text(
        json.dumps(
            {
                "lockfile": spec.lockfile,
                "lockfile_digest": digest,
                "directory": spec.directory,
                "runtime": runtime_fingerprint(),
                "seeded_from": str(target_root),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        os.rename(staging, entry)
    except OSError:
        # Another worktree seeded the same digest first; theirs is equivalent.
        _remove_tree(staging)
        payload["reason"] = "cache entry appeared concurrently"
        payload["duration_ms"] = int((time.monotonic() - started) * 1000)
        return payload
    payload["seeded"] = True
    payload["duration_ms"] = int((time.monotonic() - started) * 1000)
    return payload
