"""The lesson ledger's cooperative WRITE LOCK, proven with real processes.

Split from `test_lesson_ledger.py` (S3, 2026-08-15) on a concept seam rather than
to dodge a cap: everything there is single-process replay and refusal semantics,
while this file forks two writers and asserts the fcntl lock serialises them. It
is also the only lesson test that needs `multiprocessing`, so keeping it here
stops that import from riding along with thirty schema tests.
"""

from __future__ import annotations

import json
import multiprocessing
import os
import time
from pathlib import Path

import pytest

from scripts.lessons import lesson_ledger_writer_lib as writer
from scripts.lessons import record_lesson_score as scorer
from tests.test_lesson_ledger import ANCHOR, _ledger, _retro, _validate


def _append_in_child(
    repo_text: str, event_id: str, source: str, barrier, queue
) -> None:
    repo = Path(repo_text)
    try:
        barrier.wait(timeout=10)
        scorer.append_score(
            repo_root=repo,
            output_dir=repo / "charness-artifacts/retro",
            summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
            event_id=event_id,
            lesson_id="a",
            source_retro=source,
            outcome="changed-an-action",
            anchor=ANCHOR,
        )
        queue.put(None)
    except BaseException as exc:  # pragma: no cover - reported by parent assertion
        queue.put(repr(exc))


@pytest.mark.skipif(writer.fcntl is None, reason="requires POSIX cooperative-lock proof")
def test_two_concurrent_score_writers_preserve_both_events(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    _retro(tmp_path, "second.md", "a")
    path = _ledger(tmp_path)
    context = multiprocessing.get_context("fork")
    barrier, queue = context.Barrier(2), context.Queue()
    processes = [
        context.Process(
            target=_append_in_child,
            args=(
                str(tmp_path),
                "concurrent-a",
                "charness-artifacts/retro/source.md",
                barrier,
                queue,
            ),
        ),
        context.Process(
            target=_append_in_child,
            args=(
                str(tmp_path),
                "concurrent-b",
                "charness-artifacts/retro/second.md",
                barrier,
                queue,
            ),
        ),
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(15)
    assert all(process.exitcode == 0 for process in processes)
    assert [queue.get(timeout=2), queue.get(timeout=2)] == [None, None]
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert {event["event_id"] for event in payload["score_events"]} == {
        "concurrent-a",
        "concurrent-b",
    }
    assert _validate(tmp_path)["score_event_count"] == 2


def _hold_lock_in_child(ledger_text: str, ceiling: str | None, queue) -> None:
    """Acquire the ledger lock under one ceiling environment and hold it.

    The parent starts the second writer only after this one reports `held`,
    so the hold is deterministically established before contention begins.
    """
    ledger = Path(ledger_text)
    try:
        if ceiling is None:
            os.environ.pop("GIT_CEILING_DIRECTORIES", None)
        else:
            os.environ["GIT_CEILING_DIRECTORIES"] = ceiling
        with writer.ledger_lock(ledger):
            queue.put(("held", time.monotonic(), str(writer._lock_path(ledger))))
            time.sleep(3)
            queue.put(("released", time.monotonic()))
    except BaseException as exc:  # pragma: no cover - reported by parent assertion
        queue.put(("error", repr(exc)))


def _contend_lock_in_child(ledger_text: str, queue) -> None:
    """Enter the same ledger lock with no ceiling and report when admitted."""
    ledger = Path(ledger_text)
    try:
        os.environ.pop("GIT_CEILING_DIRECTORIES", None)
        with writer.ledger_lock(ledger):
            queue.put(("entered", time.monotonic(), str(writer._lock_path(ledger))))
    except BaseException as exc:  # pragma: no cover - reported by parent assertion
        queue.put(("error", repr(exc)))


@pytest.mark.skipif(writer.fcntl is None, reason="requires POSIX cooperative-lock proof")
def test_cross_ceiling_writers_serialize_on_one_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A ceiling-hidden writer and a plain writer must serialize, not overlap.

    The holder runs with GIT_CEILING_DIRECTORIES hiding the enclosing
    repository while the contender runs without it. Both must meet at the
    same lock file, and the contender must not enter the protected section
    before the holder releases: with a 3s hold, scheduling jitter cannot
    bridge the gap, so the timestamp order is deterministic.
    """
    outer = tmp_path / "outer"
    (outer / ".git" / "objects").mkdir(parents=True)
    (outer / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    ledger = outer / "inner" / "lesson-ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("{}", encoding="utf-8")
    # Keep the suite-wide ceiling out of the children: each child sets its
    # own discovery environment after forking.
    monkeypatch.delenv("GIT_CEILING_DIRECTORIES", raising=False)
    context = multiprocessing.get_context("fork")
    queue = context.Queue()
    holder = context.Process(
        target=_hold_lock_in_child, args=(str(ledger), str(outer.resolve()), queue)
    )
    holder.start()
    try:
        kind, held_at, holder_lock = queue.get(timeout=10)
        assert kind == "held", kind
        contender = context.Process(
            target=_contend_lock_in_child, args=(str(ledger), queue)
        )
        contender.start()
        holder.join(15)
        contender.join(15)
        assert holder.exitcode == 0
        assert contender.exitcode == 0
        kind, released_at = queue.get(timeout=10)[:2]
        assert kind == "released", kind
        kind, entered_at, contender_lock = queue.get(timeout=10)
        assert kind == "entered", kind
        assert contender_lock == holder_lock
        assert entered_at >= released_at
    finally:
        if holder.is_alive():
            holder.terminate()
        for process in list(context.active_children()):
            if process is not holder:
                process.terminate()
