"""The seed cache must not grow without bound.

It had no eviction at all: `get_or_build` only ever removed the entry it was about to
rebuild, while the KEY is the exact working-tree state (HEAD plus the diff plus every
untracked file's content), so every commit and every intermediate edit minted a new entry
holding two full repo copies. Measured 2026-08-13 on the authoring machine: 1850 entries,
1.1 TB, oldest from 2026-05-20, still accelerating.

What made it expensive to diagnose is that a full disk does not present as a full disk
here. The suite's fixture `git commit` calls start returning 1 nondeterministically, so a
different set of tests fails on each run and the whole thing reads as flakiness.
"""
from __future__ import annotations

import itertools
import time
import types
from pathlib import Path

import pytest

from tests import seed_cache


def _entry(root: Path, name: str, *, used: float) -> Path:
    entry = root / name
    entry.mkdir(parents=True)
    (entry / "payload").write_text("seed", encoding="utf-8")
    (entry / ".used").write_text(str(used), encoding="utf-8")
    return entry


HASHES = [f"{index:032x}".replace("0", "a" if index % 2 else "0") for index in range(1, 7)]


def test_least_recently_used_entries_are_dropped_beyond_the_cap(tmp_path: Path) -> None:
    now = time.time()
    current = "b" * 32
    _entry(tmp_path, current, used=now)
    for offset, name in enumerate(HASHES, start=1):
        _entry(tmp_path, name, used=now - offset * 60)

    removed = seed_cache._prune(tmp_path, current=current, keep=3)

    survivors = sorted(
        path.name for path in tmp_path.iterdir() if seed_cache._HASH_DIR.match(path.name)
    )
    # `keep` counts the current entry, so two others survive: the two most recently USED.
    assert current in survivors
    assert sorted(survivors) == sorted([current, HASHES[0], HASHES[1]])
    assert sorted(removed) == sorted(HASHES[2:])


def test_recency_comes_from_use_not_from_creation(tmp_path: Path) -> None:
    """Reading a cached seed does not touch its directory, so an mtime policy would evict
    the entry every run reuses and keep the ones nothing has opened in months."""
    now = time.time()
    current = "b" * 32
    _entry(tmp_path, current, used=now)
    old_but_used = _entry(tmp_path, HASHES[0], used=now - 10)
    new_but_idle = _entry(tmp_path, HASHES[1], used=now - 10_000)
    # Creation order is the opposite of use order.
    assert new_but_idle.stat().st_mtime >= old_but_used.stat().st_mtime

    seed_cache._prune(tmp_path, current=current, keep=2)

    assert old_but_used.is_dir()
    assert not new_but_idle.exists()


def test_pruning_never_touches_a_non_hash_directory(tmp_path: Path) -> None:
    """A source hash is 32 hex chars. Anything else under the cache root is not ours."""
    current = "b" * 32
    _entry(tmp_path, current, used=time.time())
    for name in ("notes", "my-backup", "0123", "b" * 40):
        (tmp_path / name).mkdir()
        (tmp_path / name / "keep").write_text("x", encoding="utf-8")

    seed_cache._prune(tmp_path, current=current, keep=1)

    for name in ("notes", "my-backup", "0123", "b" * 40):
        assert (tmp_path / name / "keep").is_file(), name


def test_a_locked_entry_is_skipped_rather_than_removed(tmp_path: Path) -> None:
    """A concurrent process may be mid-build in an entry we would otherwise evict."""
    import filelock

    now = time.time()
    current = "b" * 32
    _entry(tmp_path, current, used=now)
    busy = _entry(tmp_path, HASHES[0], used=now - 10_000)
    lock = filelock.FileLock(str(busy / "charness-repo-seed.lock"))
    lock.acquire()
    try:
        removed = seed_cache._prune(tmp_path, current=current, keep=1)
    finally:
        lock.release()

    assert busy.is_dir()
    assert removed == []


def test_the_current_entry_is_never_evicted(tmp_path: Path) -> None:
    """The caller is about to read it; evicting it would delete the build in progress."""
    current = "b" * 32
    _entry(tmp_path, current, used=0.0)
    for offset, name in enumerate(HASHES, start=1):
        _entry(tmp_path, name, used=time.time() + offset)

    seed_cache._prune(tmp_path, current=current, keep=1)

    assert (tmp_path / current).is_dir()


def test_get_or_build_prunes_and_marks_use(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The wiring, not just the helper: an unwired prune is the same defect."""
    monkeypatch.setattr(seed_cache, "_user_cache_root", lambda: tmp_path)
    monkeypatch.setattr(seed_cache, "source_hash", lambda: "c" * 32)
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_KEEP", "1")
    stale = _entry(tmp_path, HASHES[0], used=0.0)

    # A controlled clock: `seed_cache.time` is replaced with a private namespace whose
    # `.time()` hands out 1000.0, 1001.0, ... in order. Patching only `seed_cache.time`
    # (not the global `time` module) keeps every other user of wall-clock time in the
    # process unaffected, so the second `.used` marker is deterministically distinct from
    # the first without sleeping for real time to pass.
    fake_now = itertools.count(1000)
    monkeypatch.setattr(seed_cache, "time", types.SimpleNamespace(time=lambda: float(next(fake_now))))

    built = seed_cache.get_or_build("demo", lambda path: (path / "f").write_text("x", encoding="utf-8"))

    assert built.is_dir()
    assert not stale.exists()
    assert (tmp_path / ("c" * 32) / ".used").read_text(encoding="utf-8") == "1000.0"

    # A second call reuses the entry and re-marks it, so reuse keeps it alive.
    seed_cache.get_or_build("demo", lambda path: pytest.fail("must not rebuild a ready entry"))
    assert (tmp_path / ("c" * 32) / ".used").read_text(encoding="utf-8") == "1001.0"


def _shape(root: Path, name: str, *, used: float) -> Path:
    entry = root / name
    entry.mkdir(parents=True)
    (entry / "payload").write_text("shape", encoding="utf-8")
    (root / f"{name}.ready").write_text("ok", encoding="utf-8")
    (root / f"{name}.used").write_text(str(used), encoding="utf-8")
    return entry


def test_the_shape_namespace_is_capped_per_shape_and_by_use(tmp_path: Path) -> None:
    """Unbounded is how this cache reached 1.1 TB once. The shape namespace is cheap
    (~40 KB an entry) but not free, so it is capped too -- per SHAPE, because evicting the
    namespace wholesale would reinstate the invalidation the namespace exists to remove."""
    now = time.time()
    current = "shape-one-commit-current"
    _shape(tmp_path, current, used=0.0)
    fresh = _shape(tmp_path, "shape-one-commit-fresh", used=now)
    stale = _shape(tmp_path, "shape-two-commit-stale", used=now - 10_000)

    removed = seed_cache._prune_shapes_unlocked(tmp_path, current=current, keep=2)

    assert (tmp_path / current).is_dir(), "the entry being built is never evicted"
    assert fresh.is_dir()
    assert not stale.exists()
    assert removed == ["shape-two-commit-stale"]
    # The whole trio goes, so a surviving `.ready` can never point at a deleted tree.
    assert not (tmp_path / "shape-two-commit-stale.ready").exists()
    assert not (tmp_path / "shape-two-commit-stale.used").exists()


def test_the_source_hash_pruner_cannot_reach_the_shape_namespace(tmp_path: Path) -> None:
    """`shapes` is a name, not a 32-hex hash, so the source-hash pruner never sees it. That
    is load-bearing now, not incidental: it is what makes a shape outlive an edit."""
    current = "b" * 32
    _entry(tmp_path, current, used=time.time())
    shapes = tmp_path / seed_cache._SHAPES_DIRNAME
    kept = _shape(shapes, "shape-one-commit-abc", used=0.0)

    seed_cache._prune(tmp_path, current=current, keep=1)

    assert kept.is_dir()
    assert (shapes / "shape-one-commit-abc.ready").is_file()


def test_a_locked_shape_is_skipped_rather_than_removed(tmp_path: Path) -> None:
    import filelock

    stale = _shape(tmp_path, "shape-one-commit-busy", used=0.0)
    lock = filelock.FileLock(str(tmp_path / "shape-one-commit-busy.lock"))
    lock.acquire()
    try:
        removed = seed_cache._prune_shapes_unlocked(tmp_path, current="other", keep=1)
    finally:
        lock.release()

    assert stale.is_dir()
    assert removed == []


def test_the_keep_count_is_bounded_and_survives_a_bad_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHARNESS_TEST_SEED_CACHE_KEEP", raising=False)
    assert seed_cache._keep_count() == seed_cache.SEED_CACHE_KEEP
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_KEEP", "7")
    assert seed_cache._keep_count() == 7
    # Never zero: a cap of 0 would evict the entry the caller is building against.
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_KEEP", "0")
    assert seed_cache._keep_count() == 1
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_KEEP", "not-a-number")
    assert seed_cache._keep_count() == seed_cache.SEED_CACHE_KEEP

    monkeypatch.delenv("CHARNESS_TEST_SHAPE_CACHE_KEEP", raising=False)
    assert seed_cache._shape_keep_count() == seed_cache.SHAPE_CACHE_KEEP
    monkeypatch.setenv("CHARNESS_TEST_SHAPE_CACHE_KEEP", "9")
    assert seed_cache._shape_keep_count() == 9
    monkeypatch.setenv("CHARNESS_TEST_SHAPE_CACHE_KEEP", "0")
    assert seed_cache._shape_keep_count() == 1
    monkeypatch.setenv("CHARNESS_TEST_SHAPE_CACHE_KEEP", "not-a-number")
    assert seed_cache._shape_keep_count() == seed_cache.SHAPE_CACHE_KEEP
