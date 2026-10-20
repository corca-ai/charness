"""Event bytes survive every way a lane's executor can end, or the loss is recorded.

The carrier stamps executor stdout through a pipe (`StampingPipe`). The
v8.15.0 release critique (R1) found that close() could give up on the reader
and the caller then closed the sink, dropping bytes silently. These pin the
contract: everything written before close reaches the events log
byte-for-byte on normal exit, timeout, a signalled child and a parent
interrupt; a writer that outlives close, or a failing sink, is reported in
the capture receipt and never blocks the executor.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import threading
from pathlib import Path

import pytest

from scripts.task_run import task_run_event_timing as timing
from scripts.task_run import task_run_execution

from .test_task_run_fixtures import _codex, _repo, _run

pytestmark = pytest.mark.boundary_contract(
    reason="the claim is what a real executor process leaves in the pipe on timeout, signal and detach"
)

STAMP = "2026-10-20T08:00:00.000Z"
LINES = (
    b'{"type":"thread.started","thread_id":"fake-thread"}\n'
    b'{"type":"item.started","item":{"id":"c1","type":"command_execution"}}\n'
    b"plain progress text\n"
)
PARTIAL = b'{"type":"turn'
STAMPED = (
    b'{"charness_received_at":"2026-10-20T08:00:00.000Z","type":"thread.started",'
    b'"thread_id":"fake-thread"}\n'
    b'{"charness_received_at":"2026-10-20T08:00:00.000Z","type":"item.started",'
    b'"item":{"id":"c1","type":"command_execution"}}\n'
    b"plain progress text\n"
)


@pytest.fixture(autouse=True)
def _fixed_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(timing, "utc_receive_stamp", lambda: STAMP)


def _emit_body(tail: str) -> str:
    # printf %s keeps the bytes exact; the partial line has no newline.
    payload = (LINES + PARTIAL).decode("ascii").replace("'", "'\\''")
    return f"printf 'VALUE = 2\\n' > module.py\nprintf '%s' '{payload}'\n{tail}"


def _events(payload: dict[str, object]) -> bytes:
    """This run's slice of the lane events log (the log appends across runs)."""
    window = payload["execution"]["event_log_window"]  # type: ignore[index]
    with Path(window["path"]).open("rb") as handle:
        handle.seek(window["offset_bytes"])
        return handle.read(window["byte_count"])


def test_timeout_keeps_every_event_byte_including_the_partial_tail(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, _emit_body("sleep 5"))

    payload = _run(repo, tmp_path, executable, timeout_seconds=1)

    assert payload["status"] == "timed-out"
    # The retained log ends the partial line with the newline retention adds.
    assert _events(payload) == STAMPED + PARTIAL + b"\n"
    assert "event_capture_incomplete" not in payload["execution"]


def test_a_signalled_child_keeps_every_event_byte(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _codex(tmp_path, _emit_body("kill -TERM $$"), deliver=False)

    payload = _run(repo, tmp_path, executable)

    assert payload["candidate"]["status"] == "wip"
    assert _events(payload) == STAMPED + PARTIAL + b"\n"
    assert "event_capture_incomplete" not in payload["execution"]


def test_parent_interrupt_drains_the_pipe_before_the_sink_closes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stdout_log = tmp_path / "stdout.log"

    def writing_then_interrupted(*_args, **_kwargs):
        # fd 1 is the stamping pipe's write end while the executor runs.
        os.write(1, LINES + PARTIAL)
        raise KeyboardInterrupt

    monkeypatch.setattr(task_run_execution, "run_monitored_phase", writing_then_interrupted)

    result = task_run_execution._execute_codex(
        ["codex"],
        prompt="stop",
        target_path=tmp_path,
        configured_env={},
        stdout_log=stdout_log,
        stderr_log=tmp_path / "stderr.log",
        timeout_seconds=1,
    )

    assert result["interrupted"] is True
    assert "event_capture_incomplete" not in result
    assert (tmp_path / "codex.events.log").read_bytes() == STAMPED + PARTIAL + b"\n"


def test_a_writer_that_outlives_close_is_reported_not_waited_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(timing, "_CLOSE_GRACE_SECONDS", 0.2)
    sink = io.BytesIO()
    pipe = timing.StampingPipe(sink, clock=lambda: STAMP)
    descendant = os.dup(pipe.fileno())  # a descendant that escaped the group kill
    try:
        os.write(descendant, LINES + PARTIAL)
        pipe.close()
        capture = pipe.capture()
    finally:
        os.close(descendant)

    # Everything written before close is kept; what the survivor writes later
    # is not, and the receipt says so instead of staying silent.
    assert sink.getvalue() == STAMPED + PARTIAL
    assert capture["complete"] is False
    assert capture["writer_open_at_close"] is True
    assert capture["received_bytes"] == len(LINES + PARTIAL)


class _FailingSink(io.BytesIO):
    def write(self, data: bytes) -> int:  # type: ignore[override]
        raise OSError(28, "No space left on device")


def test_a_failing_sink_is_reported_and_never_blocks_the_executor() -> None:
    pipe = timing.StampingPipe(_FailingSink(), clock=lambda: STAMP)
    # Far more than a pipe buffer: a reader that stopped draining would block
    # this writer forever, which is how a failed sink would hang the lane.
    flood = b'{"type":"item.started"}\n' * 40_000
    writer = threading.Thread(target=os.write, args=(pipe.fileno(), flood), daemon=True)
    writer.start()
    writer.join(timeout=10)
    assert not writer.is_alive()
    pipe.close()

    capture = pipe.capture()
    assert capture["complete"] is False
    assert capture["error"] == "OSError: [Errno 28] No space left on device"
    assert capture["received_bytes"] == len(flood)
    assert capture["dropped_bytes"] > 0


def test_incomplete_capture_reaches_the_execution_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if shutil.which("setsid") is None:
        pytest.skip("setsid is unavailable")
    monkeypatch.setattr(timing, "_CLOSE_GRACE_SECONDS", 0.2)
    repo = _repo(tmp_path)
    # A detached descendant keeps stdout open past the process-group kill; the
    # executor exits only once it has left the group, so the kill cannot win.
    ready = tmp_path / "detached"
    executable = _codex(
        tmp_path,
        _emit_body(
            f"setsid sh -c 'touch {ready}; exec sleep 3' &\n"
            f"while [ ! -e {ready} ]; do :; done"
        ),
    )

    payload = _run(repo, tmp_path, executable)

    gaps = payload["execution"]["event_capture_incomplete"]
    assert [(gap["invocation"], gap["writer_open_at_close"]) for gap in gaps] == [(0, True)]
    assert _events(payload).startswith(STAMPED + PARTIAL)
    json.dumps(payload)  # the receipt stays serializable


class _HungSink(io.BytesIO):
    """A sink whose first write blocks until the test releases it."""

    def __init__(self) -> None:
        super().__init__()
        self.entered = threading.Event()
        self.release = threading.Event()

    def write(self, data: bytes) -> int:  # type: ignore[override]
        self.entered.set()
        self.release.wait(timeout=30)
        return super().write(data)


def test_a_hung_sink_cannot_hang_close_or_receive_writes_after_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(timing, "_CLOSE_GRACE_SECONDS", 0.05)
    sink = _HungSink()
    pipe = timing.StampingPipe(sink, clock=lambda: STAMP)
    os.write(pipe.fileno(), LINES)
    assert sink.entered.wait(timeout=30)

    pipe.close()  # returns although the reader is stuck in the sink
    capture = pipe.capture()
    sink.release.set()
    pipe._thread.join(timeout=30)

    assert capture["complete"] is False
    assert capture["error"] == "event reader did not finish before close"
    # The stuck write finishes; every later line is dropped and counted.
    assert pipe.capture()["dropped_bytes"] > 0
    assert sink.getvalue().count(b"\n") == 1


def test_a_failing_clock_keeps_the_bytes_unstamped_and_records_it() -> None:
    def broken_clock() -> str:
        raise ValueError("clock broke")

    sink = io.BytesIO()
    pipe = timing.StampingPipe(sink, clock=broken_clock)
    os.write(pipe.fileno(), LINES + PARTIAL)
    pipe.close()

    assert sink.getvalue() == LINES + PARTIAL
    assert pipe.capture()["error"] == "ValueError: clock broke"


def test_a_failing_pipe_read_is_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_select(*_args: object) -> object:
        raise OSError("select failed")

    # Rebinds only the timing module's name, not the process-wide select module.
    monkeypatch.setattr(timing, "select", type("S", (), {"select": staticmethod(failing_select)}))
    pipe = timing.StampingPipe(io.BytesIO(), clock=lambda: STAMP)
    pipe.close()

    assert pipe.capture()["error"] == "OSError: select failed"
    assert pipe.capture()["complete"] is False


def test_the_observer_sees_complete_events_and_its_faults_cost_no_bytes() -> None:
    seen: list[dict[str, object]] = []

    def observer(event: dict[str, object]) -> None:
        seen.append(event)
        raise RuntimeError("observer bug")

    sink = io.BytesIO()
    pipe = timing.StampingPipe(sink, clock=lambda: STAMP, observer=observer)
    os.write(pipe.fileno(), LINES + b"{broken json\n" + PARTIAL)
    pipe.close()

    assert sink.getvalue() == STAMPED + b"{broken json\n" + PARTIAL
    # Two JSON objects reach the observer; text, broken JSON and the
    # unfinished line do not, and its exceptions are contained.
    assert [event["type"] for event in seen] == ["thread.started", "item.started"]
    assert pipe.capture()["complete"] is True
