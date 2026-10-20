"""Receive-time stamps on lane events logs, and the command-timing reader.

Codex items and Muse envelopes carry no wall time, so the carrier stamps each
JSON line as it arrives on the executor's stdout pipe. Every clock here is
injected; no test reads wall time or waits on a deadline.
"""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path

import pytest

from scripts.cli import cmd_task as task_payload
from scripts.task_run import task_run, task_run_runtime
from scripts.task_run import task_run_event_timing as timing

FIELD = timing.RECEIVED_AT_FIELD


def _codex(at: str, kind: str, item: dict[str, object]) -> str:
    return json.dumps({FIELD: at, "type": kind, "item": item})


def _muse(at: str, payload_type: str, payload: dict[str, object]) -> str:
    return json.dumps({FIELD: at, "payload_type": payload_type, "payload": payload})


def test_stamp_inserts_field_first_and_keeps_event_bytes() -> None:
    line = b'{"type":"item.started","item":{"id":"item_1"}}\n'
    stamped = timing.stamp_event_line(line, "2026-10-20T08:00:00.000Z")

    assert stamped == (
        b'{"charness_received_at":"2026-10-20T08:00:00.000Z",'
        b'"type":"item.started","item":{"id":"item_1"}}\n'
    )
    assert timing.stamp_event_line(b"{}\n", "t") == b'{"charness_received_at":"t"}\n'
    for untouched in (b"plain agent text\n", b"[1, 2]\n", b"{not json\n", stamped):
        assert timing.stamp_event_line(untouched, "t") == untouched


def test_stamping_pipe_stamps_each_line_with_the_injected_clock() -> None:
    sink = io.BytesIO()
    # One clock read per received line; the plain-text line passes through.
    stamps = iter(
        ["2026-10-20T08:00:00.000Z", "2026-10-20T08:00:00.700Z", "2026-10-20T08:00:01.500Z"]
    )
    pipe = timing.StampingPipe(sink, clock=lambda: next(stamps))
    os.write(pipe.fileno(), b'{"type":"thread.started"}\nCONTRACT-READ\n{"type":"turn.started"}')
    pipe.close()

    assert sink.getvalue() == (
        b'{"charness_received_at":"2026-10-20T08:00:00.000Z","type":"thread.started"}\n'
        b"CONTRACT-READ\n"
        b'{"charness_received_at":"2026-10-20T08:00:01.500Z","type":"turn.started"}'
    )


def test_codex_command_timing_reports_durations_families_and_phases() -> None:
    test_cmd = "/usr/bin/zsh -lc 'pnpm run test:changed'"
    lint_cmd = "/usr/bin/zsh -lc 'pnpm run lint && pnpm run check:types'"
    lines = [
        _codex("2026-10-20T08:00:00.000Z", "item.completed",
               {"id": "m1", "type": "agent_message", "text": "CONTRACT-READ"}),
        _codex("2026-10-20T08:01:00.000Z", "item.started",
               {"id": "c1", "type": "command_execution", "command": "cat gateway/test/a.ts"}),
        _codex("2026-10-20T08:01:02.000Z", "item.completed",
               {"id": "c1", "type": "command_execution", "command": "cat gateway/test/a.ts"}),
        _codex("2026-10-20T08:02:00.000Z", "item.completed",
               {"id": "m2", "type": "agent_message", "text": "EDITING"}),
        _codex("2026-10-20T08:05:00.000Z", "item.completed",
               {"id": "m3", "type": "agent_message", "text": "TESTING"}),
        _codex("2026-10-20T08:05:00.000Z", "item.started",
               {"id": "c2", "type": "command_execution", "command": test_cmd}),
        _codex("2026-10-20T08:17:30.250Z", "item.completed",
               {"id": "c2", "type": "command_execution", "command": test_cmd}),
        _codex("2026-10-20T08:18:00.000Z", "item.started",
               {"id": "c3", "type": "command_execution", "command": lint_cmd}),
    ]

    report = timing.command_timing("\n".join(lines) + "\n")

    assert report["stamped"] is True
    assert report["span_seconds"] == 1080.0
    assert report["command_starts"] == 3
    assert report["starts_by_family"] == {"test": 1, "lint": 1, "typecheck": 1, "merge": 0}
    assert report["untimed_commands"] == 1
    assert report["longest_commands"] == [
        {"command": test_cmd, "duration_seconds": 750.25, "families": ["test"]},
        {"command": "cat gateway/test/a.ts", "duration_seconds": 2.0, "families": []},
    ]
    assert [(p["phase"], p["seconds"]) for p in report["phases"]] == [
        ("CONTRACT-READ", 120.0),
        ("EDITING", 180.0),
        ("TESTING", 780.0),
    ]


def test_muse_command_timing_pairs_bash_task_lifecycle() -> None:
    def task(at: str, kind: str, task_id: str, **event: object) -> str:
        return _muse(at, f"task.lifecycle.{kind}", {"task_id": task_id, "event": event})

    chunk = json.dumps({"command": "git merge main", "exit_code": 0})
    lines = [
        _muse("2026-10-20T08:00:00.000Z", "run.output.delta", {"text": "CONTRACT-"}),
        _muse("2026-10-20T08:00:01.000Z", "run.output.delta", {"text": "READ\n"}),
        task("2026-10-20T08:00:02.000Z", "proposed", "t1", task_kind="tool.bash"),
        task("2026-10-20T08:00:03.000Z", "started", "t1"),
        task("2026-10-20T08:00:09.000Z", "output", "t1", chunk=chunk),
        task("2026-10-20T08:00:09.000Z", "completed", "t1"),
        task("2026-10-20T08:00:10.000Z", "proposed", "r1", task_kind="model.meta.response"),
        task("2026-10-20T08:00:10.000Z", "started", "r1"),
    ]

    report = timing.command_timing("\n".join(lines))

    assert report["command_starts"] == 1
    assert report["starts_by_family"]["merge"] == 1
    assert report["longest_commands"] == [
        {"command": "git merge main", "duration_seconds": 6.0, "families": ["merge"]}
    ]
    assert report["phases"] == [
        {"phase": "CONTRACT-READ", "entered_at": "2026-10-20T08:00:01.000Z", "seconds": 9.0}
    ]


def test_unstamped_log_reports_starts_without_durations() -> None:
    line = json.dumps(
        {"type": "item.started", "item": {"id": "c1", "type": "command_execution",
                                         "command": "python3 -m pytest tests"}}
    )
    report = timing.command_timing(line)

    assert report["stamped"] is False
    assert report["unstamped_events"] == 1
    assert report["starts_by_family"]["test"] == 1
    assert report["untimed_commands"] == 1
    assert report["longest_commands"] == []


@pytest.mark.parametrize(
    ("command", "families"),
    [
        ("pnpm --filter gateway run test:unit", ["test"]),
        ("go test ./... && gofmt -l cli", ["test", "lint"]),
        ("pnpm run typecheck", ["typecheck"]),
        ("git rebase main", ["merge"]),
        ("grep -rn foo gateway/test/a.test.ts", []),
    ],
)
def test_command_families_match_runners_not_mentions(command: str, families: list[str]) -> None:
    assert timing.command_families(command) == families


def test_cmd_status_commands_reads_the_lanes_events_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lane = tmp_path / "task-run" / "lane-a"
    lane.mkdir(parents=True)
    record = {
        "task_id": "lane-a",
        "status": "completed",
        "executor": {"kind": "codex"},
        "logs": {"stdout": str(lane / "codex.stdout.log")},
    }
    (lane / "result.json").write_text(json.dumps(record), encoding="utf-8")
    (lane / "codex.events.log").write_text(
        _codex("2026-10-20T08:00:00.000Z", "item.started",
               {"id": "c1", "type": "command_execution", "command": "pnpm run lint"})
        + "\n"
        + _codex("2026-10-20T08:00:04.000Z", "item.completed",
                 {"id": "c1", "type": "command_execution", "command": "pnpm run lint"})
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(task_payload, "_load_task_run_lib", lambda _args: task_run)
    monkeypatch.setattr(task_run_runtime, "task_runtime_root", lambda _root: tmp_path)
    monkeypatch.setattr(
        task_run_runtime._git_owner, "_require_git_root", lambda root: Path(root).resolve()
    )
    emitted: list[dict[str, object]] = []
    monkeypatch.setattr(task_payload, "emit_yaml", emitted.append)

    code = task_payload.cmd_task_status(
        argparse.Namespace(repo_root=tmp_path, task_id="lane-a", all_repos=False, commands=True)
    )

    assert code == 0
    assert emitted[-1]["event"] == "task-command-timing"
    assert emitted[-1]["events_log"] == str(lane / "codex.events.log")
    assert emitted[-1]["longest_commands"] == [
        {"command": "pnpm run lint", "duration_seconds": 4.0, "families": ["lint"]}
    ]


def test_naive_or_malformed_stamps_count_as_unstamped_in_a_mixed_log() -> None:
    """A naive stamp cannot be ordered against UTC ones; it must not crash timing."""
    started = {"id": "c1", "type": "command_execution", "command": "pnpm run lint"}
    lines = [
        _codex("2026-10-20T08:00:00.000Z", "item.started", started),
        _codex("2026-10-20T08:00:04", "item.completed", started),
        _codex("not-a-time", "item.started", {**started, "id": "c2"}),
        _codex("2026-10-20T08:00:09.000+00:00", "item.completed", {**started, "id": "c2"}),
    ]

    report = timing.command_timing("\n".join(lines))

    assert report["stamped"] is False
    assert report["unstamped_events"] == 2
    assert report["command_starts"] == 2
    assert report["untimed_commands"] == 2
    assert report["span_seconds"] == 9.0


def test_timing_reader_skips_lines_it_cannot_read() -> None:
    """Agent text, broken JSON, and shapeless events are skipped, not fatal."""
    bad_chunk = {"task_id": "t1", "event": {"chunk": "{not json"}}
    lines = [
        "plain agent text",
        "{not json",
        "[1, 2]",
        json.dumps({FIELD: "2026-10-20T08:00:00.000Z", "type": "turn.started"}),
        json.dumps({FIELD: "2026-10-20T08:00:01.000Z", "payload_type": "x", "payload": []}),
        _muse("2026-10-20T08:00:02.000Z", "task.lifecycle.proposed",
              {"task_id": "t1", "event": {"task_kind": "tool.bash"}}),
        _muse("2026-10-20T08:00:03.000Z", "task.lifecycle.started", {"task_id": "t1"}),
        _muse("2026-10-20T08:00:04.000Z", "task.lifecycle.output", bad_chunk),
        _muse("2026-10-20T08:00:05.000Z", "task.lifecycle.completed", {"task_id": "t1"}),
    ]

    report = timing.command_timing("\n".join(lines))

    assert report["stamped"] is True
    assert report["command_starts"] == 1
    assert report["longest_commands"] == [
        {"command": None, "duration_seconds": 2.0, "families": []}
    ]


def test_cmd_status_commands_without_a_task_id_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.task_run import task_run_inventory

    monkeypatch.setattr(task_payload, "_load_task_run_lib", lambda _args: task_run)
    monkeypatch.setattr(
        task_run_inventory, "task_status", lambda *_args, **_kwargs: {"tasks": []}
    )

    with pytest.raises(task_payload.CharnessError, match="--commands needs a task id"):
        task_payload.cmd_task_status(
            argparse.Namespace(repo_root=tmp_path, task_id=None, all_repos=False, commands=True)
        )
