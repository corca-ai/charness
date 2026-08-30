from __future__ import annotations

import multiprocessing
import os
import time
from pathlib import Path

import pytest

from tests import seed_cache


def test_source_hash_reuses_the_controller_value_in_workers(monkeypatch) -> None:
    inherited = "a" * 32
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", None)
    monkeypatch.setenv(seed_cache._SOURCE_HASH_ENV, inherited)
    monkeypatch.setattr(
        seed_cache,
        "_compute_source_hash",
        lambda _root: (_ for _ in ()).throw(AssertionError("must reuse controller hash")),
    )

    assert seed_cache.source_hash() == inherited


def test_invalid_inherited_source_hash_is_not_trusted(monkeypatch) -> None:
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", None)
    monkeypatch.setenv(seed_cache._SOURCE_HASH_ENV, "not-a-source-hash")
    monkeypatch.setattr(seed_cache, "_compute_source_hash", lambda _root: "b" * 32)

    assert seed_cache.source_hash() == "b" * 32


def _concurrent_seed_worker(
    cache_root: str,
    counter_path: str,
    start_event,
    result_queue,
) -> None:
    os.environ["CHARNESS_TEST_SEED_CACHE_ROOT"] = cache_root
    seed_cache._SOURCE_HASH = "concurrency-contract"
    start_event.wait(timeout=10)

    def build(destination: Path) -> None:
        with Path(counter_path).open("a", encoding="utf-8") as counter:
            counter.write("build\n")
        # Give the peer time to wait for this outer seed. The cache must release its
        # root lock while waiting so a builder can safely compose another cached seed.
        time.sleep(0.2)
        dependency = seed_cache.get_or_build(
            "dependency",
            lambda nested: (nested / "ready.txt").write_text("ready\n", encoding="utf-8"),
        )
        assert (dependency / "ready.txt").read_text(encoding="utf-8") == "ready\n"
        (destination / "complete.txt").write_text("complete\n", encoding="utf-8")

    result = seed_cache.get_or_build("shared", build)
    result_queue.put((result / "complete.txt").read_text(encoding="utf-8"))


def _cross_hash_seed_worker(
    cache_root: str,
    source_hash: str,
    start_event,
    started_queue,
    release_event,
    result_queue,
) -> None:
    os.environ["CHARNESS_TEST_SEED_CACHE_ROOT"] = cache_root
    os.environ["CHARNESS_TEST_SEED_CACHE_KEEP"] = "1"
    seed_cache._SOURCE_HASH = source_hash
    start_event.wait(timeout=10)

    def build(destination: Path) -> None:
        started_queue.put(source_hash)
        release_event.wait(timeout=10)
        (destination / "complete.txt").write_text("complete\n", encoding="utf-8")

    result = seed_cache.get_or_build("shared", build)
    result_queue.put((source_hash, (result / "complete.txt").read_text(encoding="utf-8")))


@pytest.mark.boundary_contract(
    reason="Cross-process locking is the behavior under test; an in-process fake cannot prove it."
)
def test_seed_cache_builds_once_across_processes(tmp_path: Path) -> None:
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    result_queue = context.Queue()
    counter = tmp_path / "build-count.txt"
    workers = [
        context.Process(
            target=_concurrent_seed_worker,
            args=(str(tmp_path / "cache"), str(counter), start_event, result_queue),
        )
        for _ in range(2)
    ]

    for worker in workers:
        worker.start()
    start_event.set()
    for worker in workers:
        worker.join(timeout=15)

    assert [worker.exitcode for worker in workers] == [0, 0]
    assert counter.read_text(encoding="utf-8").splitlines() == ["build"]
    assert sorted(result_queue.get(timeout=2) for _ in workers) == ["complete\n", "complete\n"]


@pytest.mark.boundary_contract(
    reason="Cross-process pruning races are the behavior under test."
)
def test_seed_cache_pruning_does_not_delete_a_different_hash_build(
    tmp_path: Path,
) -> None:
    """Root pruning and per-entry lock acquisition must be one transaction.

    With only the per-entry lock, a second source hash can observe the first hash between
    its prune and lock acquisition and delete the directory before its builder starts.
    """
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    release_event = context.Event()
    started_queue = context.Queue()
    result_queue = context.Queue()
    workers = [
        context.Process(
            target=_cross_hash_seed_worker,
            args=(
                str(tmp_path / "cache"),
                source_hash,
                start_event,
                started_queue,
                release_event,
                result_queue,
            ),
        )
        for source_hash in ("a" * 32, "b" * 32)
    ]

    try:
        for worker in workers:
            worker.start()
        start_event.set()
        assert sorted(started_queue.get(timeout=15) for _ in workers) == ["a" * 32, "b" * 32]
        assert (tmp_path / "cache" / ("a" * 32)).is_dir()
        assert (tmp_path / "cache" / ("b" * 32)).is_dir()
    finally:
        release_event.set()
        for worker in workers:
            worker.join(timeout=15)

    assert [worker.exitcode for worker in workers] == [0, 0]
    assert sorted(result_queue.get(timeout=2) for _ in workers) == [
        ("a" * 32, "complete\n"),
        ("b" * 32, "complete\n"),
    ]


def test_seed_cache_rebuilds_stale_ready_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_ROOT", str(tmp_path / "cache"))
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", "stale-ready")
    cache_dir = tmp_path / "cache" / "stale-ready"
    cache_dir.mkdir(parents=True)
    (cache_dir / "demo.ready").write_text("stale", encoding="utf-8")

    result = seed_cache.get_or_build(
        "demo",
        lambda destination: (destination / "complete.txt").write_text(
            "rebuilt", encoding="utf-8"
        ),
    )

    assert (result / "complete.txt").read_text(encoding="utf-8") == "rebuilt"
    assert (cache_dir / "demo.ready").read_text(encoding="utf-8") == "ok"


def test_seed_cache_rebuilds_partial_directory_without_ready_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHARNESS_TEST_SEED_CACHE_ROOT", str(tmp_path / "cache"))
    monkeypatch.setattr(seed_cache, "_SOURCE_HASH", "partial-directory")
    partial = tmp_path / "cache" / "partial-directory" / "demo"
    partial.mkdir(parents=True)
    (partial / "partial.txt").write_text("incomplete", encoding="utf-8")

    result = seed_cache.get_or_build(
        "demo",
        lambda destination: (destination / "complete.txt").write_text(
            "rebuilt", encoding="utf-8"
        ),
    )

    assert not (result / "partial.txt").exists()
    assert (result / "complete.txt").read_text(encoding="utf-8") == "rebuilt"
