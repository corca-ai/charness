from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

import filelock

ROOT = Path(__file__).resolve().parents[1]

#: How many source-hash entries to keep. Each entry holds TWO full repo copies (the plain
#: seed and the git-initialized one), so an entry costs hundreds of megabytes, and the key
#: is the exact working-tree state -- HEAD plus the diff plus every untracked file's
#: content. Every commit and every intermediate edit therefore mints a NEW entry, which
#: means growth tracks development activity rather than repo size.
#:
#: Measured 2026-08-13 on the authoring machine: 1850 entries, 1.1 TB, oldest from
#: 2026-05-20, accelerating (229 in May, 381 in June, 512 in July, 728 by mid-August; 40
#: from a single session). At 97% disk the suite's fixture `git commit` calls began failing
#: NONDETERMINISTICALLY -- a different set of tests on each run -- which reads as a flaky
#: suite rather than as a full disk, and blocked a push twice before the cause was found.
#: The cache had no eviction at all: `get_or_build` only ever removed the entry it was
#: about to rebuild.
SEED_CACHE_KEEP = 3
#: A source hash is the first 32 chars of a sha256 digest. Pruning matches this shape and
#: nothing else, so an unrelated directory under the cache root is never removed.
_HASH_DIR = re.compile(r"^[0-9a-f]{32}$")
_PRUNE_LOCK_NAME = ".prune.lock"


def _keep_count() -> int:
    raw = os.environ.get("CHARNESS_TEST_SEED_CACHE_KEEP")
    if raw is None:
        return SEED_CACHE_KEEP
    try:
        return max(1, int(raw))
    except ValueError:
        return SEED_CACHE_KEEP


def _user_cache_root() -> Path:
    override = os.environ.get("CHARNESS_TEST_SEED_CACHE_ROOT")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "charness" / "test-seeds"


def _compute_source_hash(source_root: Path) -> str:
    digest = hashlib.sha256()
    head = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    digest.update(head.encode())
    digest.update(b"\n---DIFF---\n")
    diff = subprocess.run(
        ["git", "-C", str(source_root), "diff", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    digest.update(diff.encode())
    digest.update(b"\n---UNTRACKED---\n")
    untracked = subprocess.run(
        ["git", "-C", str(source_root), "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    for rel in sorted(untracked.splitlines()):
        rel = rel.strip()
        if not rel:
            continue
        full = source_root / rel
        if not full.is_file():
            continue
        digest.update(rel.encode())
        digest.update(b"\0")
        try:
            digest.update(full.read_bytes())
        except OSError:
            continue
    return digest.hexdigest()[:32]


_SOURCE_HASH: str | None = None
_SOURCE_HASH_ENV = "CHARNESS_TEST_SEED_SOURCE_HASH"


def source_hash() -> str:
    global _SOURCE_HASH
    if _SOURCE_HASH is not None:
        return _SOURCE_HASH
    inherited = os.environ.get(_SOURCE_HASH_ENV, "").strip()
    if re.fullmatch(r"[0-9a-f]{32}", inherited):
        _SOURCE_HASH = inherited
    else:
        _SOURCE_HASH = _compute_source_hash(ROOT)
    return _SOURCE_HASH


def _touch_used(entry: Path) -> None:
    """Record that this entry was USED, not merely created.

    Recency has to come from a marker we write, not from directory mtime: reading a cached
    seed does not touch the directory, so an mtime policy would evict the entry every run
    reuses and keep the ones nothing has opened since May.
    """
    try:
        (entry / ".used").write_text(str(time.time()), encoding="utf-8")
    except OSError:
        pass


def _last_used(entry: Path) -> float:
    marker = entry / ".used"
    try:
        return float(marker.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        try:
            return marker.stat().st_mtime
        except OSError:
            pass
    try:
        return entry.stat().st_mtime
    except OSError:
        return 0.0


def _prune_unlocked(cache_root: Path, *, current: str, keep: int) -> list[str]:
    """Drop least-recently-used source-hash entries beyond ``keep``.

    Never removes ``current`` -- the caller is about to read it -- and never removes an
    entry whose per-name lock is held, because a concurrent process may be mid-build there.
    A lock we cannot acquire is a skip, not a failure: pruning is opportunistic housekeeping
    and must never be the reason a test run dies.
    """
    try:
        entries = [
            path for path in cache_root.iterdir()
            if path.is_dir() and _HASH_DIR.match(path.name) and path.name != current
        ]
    except OSError:
        return []
    # `keep` counts the current entry too, so the survivors beside it are one fewer.
    survivors = max(0, keep - 1)
    stale = sorted(entries, key=_last_used, reverse=True)[survivors:]
    removed: list[str] = []
    for entry in stale:
        locks = list(entry.glob("*.lock"))
        held = False
        for lock_path in locks:
            lock = filelock.FileLock(str(lock_path), timeout=0)
            try:
                lock.acquire()
            except Exception:
                held = True
                break
            else:
                lock.release()
        if held:
            continue
        try:
            shutil.rmtree(entry)
        except OSError:
            continue
        removed.append(entry.name)
    return removed


def _prune(cache_root: Path, *, current: str, keep: int) -> list[str]:
    """Drop least-recently-used source-hash entries beyond ``keep`` safely.

    The cache-root lock closes the TOCTOU window between a pruner checking an entry's
    per-name lock and a builder acquiring that lock. Callers that are about to build hold
    the same root lock until their per-entry lock is acquired, then release the root lock
    while the potentially expensive builder runs.
    """
    cache_root.mkdir(parents=True, exist_ok=True)
    with filelock.FileLock(str(cache_root / _PRUNE_LOCK_NAME)):
        return _prune_unlocked(cache_root, current=current, keep=keep)


def get_or_build(name: str, builder: Callable[[Path], None]) -> Path:
    cache_root = _user_cache_root()
    cache_dir = cache_root / source_hash()
    final = cache_dir / name
    ready = cache_dir / f"{name}.ready"
    lock_path = cache_dir / f"{name}.lock"
    prune_lock = filelock.FileLock(str(cache_root / _PRUNE_LOCK_NAME))
    build_lock = filelock.FileLock(str(lock_path))
    cache_root.mkdir(parents=True, exist_ok=True)
    # Pruning and acquiring an AVAILABLE per-entry lock are one transaction. Never wait for
    # that lock while holding the root lock: a builder may compose another cached seed, which
    # needs the root lock in turn. When another builder owns this entry, wait without the root
    # lock and retry the whole transaction so pruning cannot race the eventual acquisition.
    while True:
        with prune_lock:
            cache_dir.mkdir(parents=True, exist_ok=True)
            _touch_used(cache_dir)
            # Before the build, so a machine that is already too full to build has its own
            # stale entries reclaimed first. The failure this prevents does not look like a
            # full disk: it looks like nondeterministic fixture `git commit` failures.
            _prune_unlocked(cache_root, current=cache_dir.name, keep=_keep_count())
            try:
                build_lock.acquire(timeout=0)
            except filelock.Timeout:
                pass
            else:
                break
        # Synchronize with the current owner, then reacquire under the prune lock. The ready
        # state is checked only after the transactional retry succeeds.
        with build_lock:
            pass
    try:
        if ready.is_file() and final.is_dir():
            return final
        if ready.exists():
            ready.unlink()
        if final.exists():
            shutil.rmtree(final)
        final.mkdir()
        builder(final)
        ready.write_text("ok", encoding="utf-8")
    finally:
        build_lock.release()
    return final
