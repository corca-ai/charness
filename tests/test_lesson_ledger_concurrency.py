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
from pathlib import Path

import pytest

from scripts import lesson_ledger_writer_lib as writer
from scripts import record_lesson_score as scorer
from tests.test_lesson_ledger import ANCHOR, _ledger, _retro, _session_event, _validate


def _append_in_child(
    repo_text: str, event_id: str, source: str, session_id: str, barrier, queue
) -> None:
    repo = Path(repo_text)
    try:
        barrier.wait(timeout=10)
        scorer.append_score(
            repo_root=repo,
            output_dir=repo / "charness-artifacts/retro",
            summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
            event_id=event_id,
            session_id=session_id,
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
    # ONE SESSION EACH. This test proves the cooperative LOCK -- both writers'
    # events survive a simultaneous append -- and it used to do that with two
    # events for one lesson in one session, which `append_score` now refuses as a
    # duplicate encounter. Two sessions keeps the lock under test without leaning
    # on a shape the writer no longer allows.
    path = _ledger(
        tmp_path,
        session_events=[_session_event(), _session_event(session_id="session-b")],
    )
    context = multiprocessing.get_context("fork")
    barrier, queue = context.Barrier(2), context.Queue()
    processes = [
        context.Process(
            target=_append_in_child,
            args=(
                str(tmp_path),
                "concurrent-a",
                "charness-artifacts/retro/source.md",
                "session-a",
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
                "session-b",
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
