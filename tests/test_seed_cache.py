from __future__ import annotations

import multiprocessing
import os
import time
from pathlib import Path

from tests import seed_cache


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
        time.sleep(0.2)
        (destination / "complete.txt").write_text("complete\n", encoding="utf-8")

    result = seed_cache.get_or_build("shared", build)
    result_queue.put((result / "complete.txt").read_text(encoding="utf-8"))


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
