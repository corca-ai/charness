"""Receive-time stamps on executor event lines, and the command-timing reader.

Codex `--json` items and Muse envelopes carry no wall time (Muse
`recorded_at` is a logical counter), so a lane's `<executor>.events.log`
could not say how long any command or phase took. The carrier now reads the
executor's stdout through a pipe and inserts `charness_received_at` (UTC,
millisecond ISO-8601) at the front of every JSON-object line as it arrives.
Non-JSON lines pass through unchanged. The stamp is the time charness
received the line, not the time the executor produced it; pipe buffering
makes it an upper bound on the producer's own time, so a duration between
two stamps can err in either direction.

`command_timing` reads a stamped events log back into per-command durations
(`item.started` to `item.completed` for Codex, `task.lifecycle.started` to
`task.lifecycle.completed` of a `tool.bash` task for Muse), starts per
command family, and the first time each lane phase marker was seen.
"""

from __future__ import annotations

import json
import os
import re
import select
import threading
import time
from datetime import datetime, timezone
from typing import Any, BinaryIO, Callable, Iterable, Mapping

RECEIVED_AT_FIELD = "charness_received_at"
_FIELD_BYTES = json.dumps(RECEIVED_AT_FIELD).encode("ascii")
_CLOSE_GRACE_SECONDS = 2.0
_POLL_SECONDS = 0.1
_CHUNK_BYTES = 64 * 1024
_LANE_PHASES = ("CONTRACT-READ", "EDITING", "TESTING")

#: Runner invocations, not mentions: `gateway/test/x.ts` is not a test run.
#: A heuristic over command text; one command may match several families
#: (`pnpm run lint && pnpm run check:types` counts in both).
_PM = r"\b(?:pnpm|npm|yarn|bun)\b[^;&|\n]*?\s(?:run\s+)?"
COMMAND_FAMILIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "test",
        re.compile(
            _PM + r"test(?::[\w-]+)?\b|\bpytest\b|\bvitest\b|\bjest\b"
            r"|\b(?:go|cargo)\s+test\b|node\s+--test\b|run_standing_pytest"
        ),
    ),
    (
        "lint",
        re.compile(
            _PM + r"lint(?::[\w-]+)?\b|\beslint\b|\bruff\s+(?:check|format)\b"
            r"|\bgolangci-lint\b|\bgofmt\b|check-docs\.sh"
        ),
    ),
    (
        "typecheck",
        re.compile(
            _PM + r"(?:check:types|typecheck)\b|\btsc\b|\bmypy\b|\bpyright\b|\bgo\s+vet\b"
        ),
    ),
    ("merge", re.compile(r"\bgit\s+(?:merge|rebase|cherry-pick)\b")),
)


def utc_receive_stamp() -> str:
    """The production receive clock: UTC wall time to the millisecond."""
    return (
        datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    )


def stamp_event_line(line: bytes, received_at: str) -> bytes:
    """Insert the receive-time field first in one JSON-object line.

    The rest of the line keeps its original bytes, so a reader that ignores
    the field sees the executor's event unchanged.
    """
    start = line.find(b"{")
    if start < 0 or line[:start].strip():
        return line
    try:
        event = json.loads(line)
    except ValueError:
        return line
    if not isinstance(event, dict) or RECEIVED_AT_FIELD in event:
        return line
    head, rest = line[: start + 1], line[start + 1 :]
    separator = b"" if rest.lstrip().startswith(b"}") else b","
    stamp = _FIELD_BYTES + b":" + json.dumps(received_at).encode("ascii")
    return head + stamp + separator + rest


class StampingPipe:
    """A pipe whose reader copies each line into `sink` with its receive time.

    `fileno()` is the write end, so the carrier can hand it to the executor
    as stdout. An optional `observer` sees each complete JSON event after its
    bytes reach the sink (the lane progress rule reads commands from it). `close()` releases the write end, then drains every byte that
    is already in the pipe and returns; it never waits on a writer that is
    still alive. Bytes are retained byte-for-byte up to the moment of close:
    once the executor's process group is killed, everything it wrote is in
    the kernel pipe buffer, so the drain reads it all.

    Two things can still lose bytes, and neither is silent: a descendant
    outside the killed group that keeps the pipe open (its later output is
    not captured, `writer_open_at_close`), and a sink write failure (`error`;
    the reader keeps reading and counts `dropped_bytes` so the executor never
    blocks on a full pipe). `capture()` reports both; the sink is written
    only under a lock that `close()` takes before it returns, so a reader
    that outlives `close()` can never write into a sink the caller closed.
    """

    def __init__(
        self,
        sink: BinaryIO,
        *,
        clock: Callable[[], str] = utc_receive_stamp,
        observer: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> None:
        self._sink = sink
        self._clock = clock
        self._observer = observer
        self._read_fd, self._write_fd = os.pipe()
        self._stop = threading.Event()
        self._sink_lock = threading.Lock()
        self._released = False
        self._sink_failed = False
        self._pending = b""
        self.received_bytes = 0
        self.dropped_bytes = 0
        self.error: str | None = None
        self.writer_open_at_close = False
        self._thread = threading.Thread(
            target=self._drain, name="charness-event-stamp", daemon=True
        )
        self._thread.start()

    def fileno(self) -> int:
        return self._write_fd

    def _emit(self, data: bytes) -> None:
        with self._sink_lock:
            if self._released:
                self.dropped_bytes += len(data)
                return
            if not self._sink_failed:
                try:
                    written = self._sink.write(data)
                    if isinstance(written, int) and written < len(data):
                        # A sink that accepted part of the line: record the rest as lost.
                        self._sink_failed = True
                        self.error = self.error or f"short write: {written} of {len(data)} bytes"
                        self.dropped_bytes += len(data) - written
                        return
                    self._sink.flush()
                    return
                except (OSError, ValueError) as exc:
                    self._sink_failed = True
                    self.error = self.error or f"{type(exc).__name__}: {exc}"
            self.dropped_bytes += len(data)

    def _stamped(self, line: bytes) -> bytes:
        try:
            return stamp_event_line(line, self._clock())
        except Exception as exc:  # noqa: BLE001 - keep the bytes, record the clock fault
            self.error = self.error or f"{type(exc).__name__}: {exc}"
            return line

    def _feed(self, chunk: bytes) -> None:
        self.received_bytes += len(chunk)
        *lines, self._pending = (self._pending + chunk).split(b"\n")
        for line in lines:
            self._emit(self._stamped(line + b"\n"))
            self._observe(line)

    def _observe(self, line: bytes) -> None:
        """Hand each complete JSON-object event to the observer, after it is kept."""
        if self._observer is None or not line.lstrip().startswith(b"{"):
            return
        try:
            event = json.loads(line)
        except ValueError:
            return
        if isinstance(event, dict):
            try:
                self._observer(event)
            except Exception:  # noqa: BLE001 - an observer fault must not cost event bytes
                pass

    def _drain(self) -> None:
        deadline: float | None = None
        try:
            while True:
                timeout = _POLL_SECONDS
                if self._stop.is_set():
                    # Closing: keep reading what is buffered, and give a just
                    # killed writer a short grace to release its end; never
                    # wait on a writer that outlives it.
                    deadline = deadline or time.monotonic() + _CLOSE_GRACE_SECONDS
                    timeout = deadline - time.monotonic()
                    if timeout <= 0:
                        self.writer_open_at_close = True
                        break
                readable, _, _ = select.select([self._read_fd], [], [], timeout)
                if not readable:
                    continue
                chunk = os.read(self._read_fd, _CHUNK_BYTES)
                if not chunk:
                    break
                self._feed(chunk)
        except (OSError, ValueError) as exc:
            self.error = self.error or f"{type(exc).__name__}: {exc}"
        finally:
            if self._pending:
                self._emit(self._stamped(self._pending))
                self._pending = b""
            os.close(self._read_fd)

    def close(self) -> None:
        if self._write_fd >= 0:
            os.close(self._write_fd)
            self._write_fd = -1
        self._stop.set()
        self._thread.join(timeout=_CLOSE_GRACE_SECONDS + 1.0)
        # The caller closes the sink after this; a reader still running (a
        # hung sink write holds the lock) must drop, not write into a closed
        # file. The lock wait is bounded so a hung sink cannot hang close.
        locked = self._sink_lock.acquire(timeout=_CLOSE_GRACE_SECONDS)
        try:
            self._released = True
            if self._thread.is_alive():
                self.error = self.error or "event reader did not finish before close"
        finally:
            if locked:
                self._sink_lock.release()

    def capture(self) -> dict[str, Any]:
        """The capture receipt: complete only if every received byte reached the sink."""
        return {
            "complete": not (self.error or self.writer_open_at_close or self.dropped_bytes),
            "received_bytes": self.received_bytes,
            "dropped_bytes": self.dropped_bytes,
            "writer_open_at_close": self.writer_open_at_close,
            "error": self.error,
        }


def _parse_stamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    # A naive value cannot be ordered against the carrier's UTC stamps, so it
    # counts as unstamped rather than crashing the subtraction later.
    return parsed if parsed.utcoffset() is not None else None


def _stamped_events(text: str) -> Iterable[tuple[datetime | None, dict[str, Any]]]:
    for line in text.splitlines():
        if not line.lstrip().startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            yield _parse_stamp(event.get(RECEIVED_AT_FIELD)), event


def command_families(command: str) -> list[str]:
    return [name for name, pattern in COMMAND_FAMILIES if pattern.search(command)]


def _muse_command(payload: Mapping[str, Any]) -> str | None:
    event = payload.get("event")
    chunk = event.get("chunk") if isinstance(event, Mapping) else None
    try:
        record = json.loads(chunk) if isinstance(chunk, str) else None
    except ValueError:
        return None
    command = record.get("command") if isinstance(record, Mapping) else None
    return command if isinstance(command, str) else None


def _muse_exit_code(payload: Mapping[str, Any], previous: object) -> object:
    event = payload.get("event")
    chunk = event.get("chunk") if isinstance(event, Mapping) else None
    try:
        record = json.loads(chunk) if isinstance(chunk, str) else None
    except ValueError:
        return previous
    code = record.get("exit_code") if isinstance(record, Mapping) else None
    return code if isinstance(code, int) else previous


class _Timeline:
    """Fold one events log into commands and first-seen phase markers."""

    def __init__(
        self, *, on_complete: Callable[[str | None, object], None] | None = None
    ) -> None:
        self._on_complete = on_complete
        self.commands: dict[str, dict[str, Any]] = {}
        self.phases: dict[str, datetime] = {}
        self.first: datetime | None = None
        self.last: datetime | None = None
        self.unstamped = 0
        self._bash_tasks: set[str] = set()
        self._codex_keys: dict[str, str] = {}
        self._agent_text = ""

    def feed(self, at: datetime | None, event: Mapping[str, Any]) -> None:
        if at is None:
            self.unstamped += 1
        else:
            self.first = self.first or at
            self.last = at
        if "payload_type" in event:
            self._feed_muse(at, event)
        else:
            self._feed_codex(at, event)

    def _start(
        self, key: str, at: datetime | None, command: str | None, *, observed: bool = True
    ) -> None:
        entry = self.commands.setdefault(
            key, {"command": command, "started": at, "completed": None, "start_seen": False}
        )
        entry["start_seen"] = entry["start_seen"] or observed

    def _feed_codex(self, at: datetime | None, event: Mapping[str, Any]) -> None:
        item = event.get("item")
        if not isinstance(item, Mapping):
            return
        if item.get("type") == "agent_message" and event.get("type") == "item.completed":
            self._phase_text(at, str(item.get("text") or "") + "\n")
        if item.get("type") != "command_execution":
            return
        item_id = str(item.get("id"))
        command = item.get("command") if isinstance(item.get("command"), str) else None
        key = self._codex_keys.get(item_id, item_id)
        if event.get("type") == "item.started":
            if key in self.commands:  # a resumed session reuses item ids: a new command
                key = f"{item_id}#{len(self.commands)}"
            self._codex_keys[item_id] = key
            self._start(key, at, command)
        elif event.get("type") == "item.completed":
            self._start(key, None, command, observed=False)
            self.commands[key]["completed"] = at
            self.commands[key]["done"] = True
            if self._on_complete is not None:
                self._on_complete(self.commands[key]["command"], item.get("exit_code"))

    def _feed_muse(self, at: datetime | None, event: Mapping[str, Any]) -> None:
        payload_type, payload = event.get("payload_type"), event.get("payload")
        if not isinstance(payload, Mapping):
            return
        if payload_type == "run.output.delta" and isinstance(payload.get("text"), str):
            self._phase_text(at, payload["text"])
            return
        task_id = str(payload.get("task_id"))
        inner = payload.get("event") if isinstance(payload.get("event"), Mapping) else {}
        if payload_type == "task.lifecycle.proposed" and inner.get("task_kind") == "tool.bash":
            self._bash_tasks.add(task_id)
        if task_id not in self._bash_tasks:
            return
        if payload_type == "task.lifecycle.started":
            self._start(task_id, at, None)
        elif payload_type == "task.lifecycle.output":
            self._start(task_id, None, None, observed=False)
            entry = self.commands[task_id]
            entry["command"] = _muse_command(payload) or entry["command"]
            entry["exit_code"] = _muse_exit_code(payload, entry.get("exit_code"))
        elif payload_type == "task.lifecycle.completed":
            self._start(task_id, None, None, observed=False)
            entry = self.commands[task_id]
            entry["completed"] = at
            entry["done"] = True
            if self._on_complete is not None:
                self._on_complete(entry["command"], entry.get("exit_code"))

    def in_flight(self) -> dict[str, str]:
        """Commands whose start was seen and whose completion was not, by item id."""
        return {
            key: str(entry["command"] or "")
            for key, entry in self.commands.items()
            if entry["start_seen"] and not entry.get("done")
        }

    def _phase_text(self, at: datetime | None, text: str) -> None:
        self._agent_text += text
        complete, _, self._agent_text = self._agent_text.rpartition("\n")
        for line in complete.splitlines():
            marker = line.strip()
            if marker in _LANE_PHASES and marker not in self.phases and at is not None:
                self.phases[marker] = at


def _seconds(start: datetime | None, end: datetime | None) -> float | None:
    return None if start is None or end is None else round((end - start).total_seconds(), 3)


def command_timing(events_text: str, *, top: int = 10) -> dict[str, Any]:
    """Longest commands, starts per family, and phase durations from one events log."""
    timeline = _Timeline()
    for at, event in _stamped_events(events_text):
        timeline.feed(at, event)
    rows = [
        {
            "command": entry["command"],
            "duration_seconds": _seconds(entry["started"], entry["completed"]),
            "families": command_families(entry["command"] or ""),
        }
        for entry in timeline.commands.values()
        if entry["start_seen"]
    ]
    families = {name: 0 for name, _ in COMMAND_FAMILIES}
    for row in rows:
        for name in row["families"]:
            families[name] += 1
    timed = sorted(
        (row for row in rows if row["duration_seconds"] is not None),
        key=lambda row: row["duration_seconds"],
        reverse=True,
    )
    order = sorted(timeline.phases.items(), key=lambda item: item[1])
    phases = [
        {
            "phase": name,
            "entered_at": at.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "seconds": _seconds(at, order[index + 1][1] if index + 1 < len(order) else timeline.last),
        }
        for index, (name, at) in enumerate(order)
    ]
    return {
        "stamped": timeline.unstamped == 0 and timeline.first is not None,
        "unstamped_events": timeline.unstamped,
        "span_seconds": _seconds(timeline.first, timeline.last),
        "command_starts": len(rows),
        "starts_by_family": families,
        "untimed_commands": len(rows) - len(timed),
        "longest_commands": timed[:top],
        "phases": phases,
    }
