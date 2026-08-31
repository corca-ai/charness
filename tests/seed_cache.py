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

#: The shape namespace, which is NOT source-hash keyed. See `get_or_build`'s
#: `content_addressed` parameter for why, and for what a caller must guarantee to use it.
#:
#: Its entries cost ~40 KB each, not hundreds of megabytes, because a shape holds only the
#: literal files its own key digests -- never a copy of this repository. Measured 2026-08-31:
#: 147 shapes, 16 MB. Its growth axis is also different: a source-hash entry is minted by
#: every EDIT, a shape only by a fixture asking for a file set no fixture has asked for
#: before. So the cap is generous where `SEED_CACHE_KEEP` is tight -- 512 shapes is ~20 MB,
#: three orders of magnitude away from the failure this file's other cap exists to prevent.
SHAPE_CACHE_KEEP = 512
#: A source hash is the first 32 chars of a sha256 digest. Pruning matches this shape and
#: nothing else, so an unrelated directory under the cache root is never removed. The
#: shape namespace is a NAME, not a hash, and is therefore invisible to that pruner.
_HASH_DIR = re.compile(r"^[0-9a-f]{32}$")
_PRUNE_LOCK_NAME = ".prune.lock"
_SHAPES_DIRNAME = "shapes"


def _keep_count() -> int:
    raw = os.environ.get("CHARNESS_TEST_SEED_CACHE_KEEP")
    if raw is None:
        return SEED_CACHE_KEEP
    try:
        return max(1, int(raw))
    except ValueError:
        return SEED_CACHE_KEEP


def _shape_keep_count() -> int:
    raw = os.environ.get("CHARNESS_TEST_SHAPE_CACHE_KEEP")
    if raw is None:
        return SHAPE_CACHE_KEEP
    try:
        return max(1, int(raw))
    except ValueError:
        return SHAPE_CACHE_KEEP


def _user_cache_root() -> Path:
    override = os.environ.get("CHARNESS_TEST_SEED_CACHE_ROOT")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "charness" / "test-seeds"


class SourceStateUnreadable(RuntimeError):
    """Git could not establish the source state this cache key is supposed to name."""


def _git_read(source_root: Path, *args: str) -> str:
    """One read-only git query whose FAILURE is never mistaken for an empty answer.

    Every gate in this repo already refuses on this shape -- "an empty list from a
    failed git is indistinguishable from nothing staged, so returning it would
    render a clean verdict over a scope that was never read". This function is
    where that rule was missing, and the consequence is worse here than a wrong
    verdict.

    `source_hash()` NAMES A CACHE DIRECTORY. Discarding the return code meant a
    failed read contributed the empty string, so every source state that fails the
    same way digests to the SAME constant key -- one shared namespace that unrelated
    checkouts would both write into and both read back. A dubious-ownership repo and
    a detached checkout at a different commit would be served each other's seeds,
    silently, as if the cache had hit.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(source_root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:  # git absent, source_root unusable
        raise SourceStateUnreadable(f"git {args[0]}: {exc}") from exc
    if proc.returncode != 0:
        reason = next((ln for ln in proc.stderr.splitlines() if ln.strip()), "")
        raise SourceStateUnreadable(
            f"git {args[0]} exited {proc.returncode} in {source_root}: "
            f"{reason.strip() or 'no stderr'}. The seed cache cannot name a key for a "
            f"source state it could not read. Fix repository access (e.g. "
            f"`git config --global --add safe.directory {source_root}`), or set "
            f"{_SOURCE_HASH_ENV}=<32 hex chars> to supply the key yourself."
        )
    return proc.stdout


def _compute_source_hash(source_root: Path) -> str:
    digest = hashlib.sha256()
    head = _git_read(source_root, "rev-parse", "HEAD").strip()
    digest.update(head.encode())
    digest.update(b"\n---DIFF---\n")
    diff = _git_read(source_root, "diff", "HEAD")
    digest.update(diff.encode())
    digest.update(b"\n---UNTRACKED---\n")
    untracked = _git_read(source_root, "ls-files", "--others", "--exclude-standard")
    for rel in sorted(untracked.splitlines()):
        rel = rel.strip()
        if not rel:
            continue
        full = source_root / rel
        # LENGTH-PREFIXED, not NUL-separated. `name\0content` concatenated is
        # ambiguous: files `a` (empty) and `b` (b"c") emit `a\0b\0c`, and so does
        # a single file `a` holding b"b\0c". Two different trees, one key.
        digest.update(f"{rel}\0".encode())
        if not full.is_file():
            # `git ls-files --others` reports a nested untracked repository as one
            # `dir/` entry. Skipping it dropped the whole subtree from the key, so
            # two trees differing only inside it collided. Recorded as a distinct
            # kind instead -- still not its contents, but no longer indistinguishable
            # from the file being absent.
            digest.update(b"non-file\0")
            continue
        try:
            payload = full.read_bytes()
        except OSError as exc:
            # UNKNOWN is not EMPTY -- the same rule `_git_read` enforces above. A
            # file present but unreadable (mode 000, EPERM, or deleted in the race
            # between `is_file()` and this read) digested identically to an empty
            # one, which is a collision between two different source states.
            raise SourceStateUnreadable(f"cannot read untracked {rel!r}: {exc}") from exc
        digest.update(f"{len(payload)}\0".encode())
        digest.update(payload)
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


def _touch_marker(marker: Path) -> None:
    """Record that the thing this marker names was USED, not merely created.

    Recency has to come from a marker we write, not from directory mtime: reading a cached
    seed does not touch the directory, so an mtime policy would evict the entry every run
    reuses and keep the ones nothing has opened since May.
    """
    try:
        marker.write_text(str(time.time()), encoding="utf-8")
    except OSError:
        pass


def _marker_time(marker: Path, *, fallback: Path) -> float:
    try:
        return float(marker.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        try:
            return marker.stat().st_mtime
        except OSError:
            pass
    try:
        return fallback.stat().st_mtime
    except OSError:
        return 0.0


def _last_used(entry: Path) -> float:
    return _marker_time(entry / ".used", fallback=entry)


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
        if _entry_is_locked(list(entry.glob("*.lock"))):
            continue
        try:
            shutil.rmtree(entry)
        except OSError:
            continue
        removed.append(entry.name)
    return removed


def _entry_is_locked(entry_locks: list[Path]) -> bool:
    """Whether any of these lock files is held by another process right now."""
    for lock_path in entry_locks:
        lock = filelock.FileLock(str(lock_path), timeout=0)
        try:
            lock.acquire()
        except Exception:
            return True
        else:
            lock.release()
    return False


def _prune_shapes_unlocked(shapes_root: Path, *, current: str, keep: int) -> list[str]:
    """Drop least-recently-used SHAPES beyond ``keep``.

    Recency is per shape name, not per namespace: the whole point of this namespace is that
    one shape survives edits that mint a new source hash, so evicting the namespace
    wholesale would reinstate exactly the invalidation it exists to remove.

    A shape's three sibling files (`<name>`, `<name>.ready`, `<name>.used`) are removed
    together, and `<name>.lock` is left alone -- it is the file another process synchronizes
    on, and deleting it out from under a waiter breaks the lock rather than the cache.
    """
    try:
        names = sorted(
            path.name[: -len(".ready")]
            for path in shapes_root.iterdir()
            if path.is_file() and path.name.endswith(".ready")
        )
    except OSError:
        return []
    names = [name for name in names if name != current]
    survivors = max(0, keep - 1)
    stale = sorted(
        names,
        key=lambda name: _marker_time(
            shapes_root / f"{name}.used", fallback=shapes_root / name
        ),
        reverse=True,
    )
    removed: list[str] = []
    for name in stale[survivors:]:
        if _entry_is_locked([shapes_root / f"{name}.lock"]):
            continue
        try:
            # `.ready` first. It is the claim "this tree is complete", so a prune that dies
            # midway must leave a MISSING seed, never a ready marker over a half-deleted one.
            (shapes_root / f"{name}.ready").unlink(missing_ok=True)
            shutil.rmtree(shapes_root / name, ignore_errors=True)
            (shapes_root / f"{name}.used").unlink(missing_ok=True)
        except OSError:
            continue
        removed.append(name)
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


def shapes_root() -> Path:
    """The source-hash-INDEPENDENT namespace. See `get_or_build(content_addressed=True)`."""
    return _user_cache_root() / _SHAPES_DIRNAME


def get_or_build(
    name: str, builder: Callable[[Path], None], *, content_addressed: bool = False
) -> Path:
    """Build ``name`` once and reuse it.

    By default the entry lives under `source_hash()` -- HEAD plus the diff plus every
    untracked file's content -- because the default seed COPIES THIS REPOSITORY, and a copy
    of a tree that has changed is the wrong tree.

    ``content_addressed=True`` puts the entry in a namespace with no source hash at all.
    The caller promises TWO things, and both are required:

      1. The built tree is a function of ``name`` alone. It contains no repo content, so
         there is nothing for a source change to invalidate.
      2. ``name`` digests the BUILDER'S BEHAVIOUR as well as its inputs. The source hash was
         silently providing this second guarantee -- edit the builder, mint a new hash, get
         a rebuild -- and a caller leaving that namespace gives it up. `repo_shapes.py` folds
         `_SHAPE_BUILDER_VERSION` into every shape key for exactly this reason.

    Measured cost of the default for a seed that did not need it (2026-08-31, full standing
    suite): a cold cache spent 397 fixture `git` calls where a warm one spent 65. Because
    every edit minted a new source hash, the 147 content-addressed shapes paid that ~330-call
    rebuild again after every edit, forever, having depended on none of it.
    """
    cache_root = _user_cache_root()
    if content_addressed:
        cache_dir = cache_root / _SHAPES_DIRNAME
        used_marker = cache_dir / f"{name}.used"
        keep = _shape_keep_count()

        def prune() -> None:
            _prune_shapes_unlocked(cache_dir, current=name, keep=keep)
    else:
        cache_dir = cache_root / source_hash()
        used_marker = cache_dir / ".used"
        keep = _keep_count()

        def prune() -> None:
            _prune_unlocked(cache_root, current=cache_dir.name, keep=keep)

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
    #
    # ONE prune lock serves both namespaces on purpose: a shape builder composes other shapes
    # (`install_submodule_repo` builds two committed repos), so two locks would be two orders
    # to take them in.
    while True:
        with prune_lock:
            cache_dir.mkdir(parents=True, exist_ok=True)
            _touch_marker(used_marker)
            # Before the build, so a machine that is already too full to build has its own
            # stale entries reclaimed first. The failure this prevents does not look like a
            # full disk: it looks like nondeterministic fixture `git commit` failures.
            prune()
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
