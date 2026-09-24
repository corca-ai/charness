"""Typed task steering and same-candidate scope amendment.

The fake executor owns a lower-level orchestration claim: its transcript marker
is written before the resumed invocation's simulated edit. It does not claim
live Codex or Muse behavior.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from scripts.task_run import (
    task_run_execution,
    task_run_lane_runner,
    task_run_progress,
    task_run_runtime,
    task_run_scope,
)
from tests.charness_cli.support import CLI, load_cli_module
from tests.charness_cli.test_task_run_fixtures import _git, _repo


def test_guard_queue_delivery_precedes_resumed_fake_executor_edit(tmp_path: Path) -> None:
    """The lower-level harness sees transcript-before-next-invocation-edit."""
    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    stdout_log = runtime / "codex.stdout.log"
    stderr_log = runtime / "codex.stderr.log"
    queue = runtime / "steer.queue.jsonl"
    order_log = tmp_path / "order.log"
    fake = tmp_path / "fake-codex"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output = pathlib.Path(args[args.index('--output-last-message') + 1])\n"
        "if 'resume' not in args:\n"
        f"    queue = pathlib.Path({str(queue)!r})\n"
        "    print(json.dumps({'type': 'thread.started', 'thread_id': 'session-1'}), flush=True)\n"
        "    queue.write_text(json.dumps({'kind': 'charness.task_steer.v1', "
        "'message_id': 'message-1', 'task_id': 'lane-1', 'message': 'Keep the public API stable.', "
        "'queued_at': '2026-09-24T00:00:00Z', 'delivered_at': None, "
        "'disposition': 'accepted', 'reason': None, 'resume_path': None}) + '\\n')\n"
        "    output.write_text('first turn\\n')\n"
        "else:\n"
        "    prompt = sys.stdin.read()\n"
        f"    transcript = pathlib.Path({str(stderr_log)!r}).read_text()\n"
        "    pathlib.Path(os.environ['ORDER_LOG']).write_text("
        "('transcript-before-edit\\n' if 'STEER [message-1]' in transcript else 'missing-steer\\n') + prompt)\n"
        f"    pathlib.Path({str(repo / 'module.py')!r}).write_text('VALUE = 2\\n')\n"
        "    print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'TESTING'}}), flush=True)\n"
        "    output.write_text('resumed turn\\n')\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    command = task_run_lane_runner.lane_command(
        executor="codex",
        executable=str(fake),
        effort="medium",
        prompt="Implement the lane request.",
        execution_runtime_path=runtime,
        writable_dirs=(),
        worktree=repo,
    )
    watch = task_run_progress.build_progress_watch(
        require_change=False,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=repo,
        base_sha=base_sha,
        scope_specs=[],
    )
    execution = task_run_execution._execute_codex(
        command,
        prompt="Implement the lane request.",
        target_path=repo,
        configured_env={**os.environ, "ORDER_LOG": str(order_log)},
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=5,
        lane_watch=watch,
        executor="codex",
    )

    assert execution["exit_code"] == 0
    assert (repo / "module.py").read_text(encoding="utf-8") == "VALUE = 2\n"
    order = order_log.read_text(encoding="utf-8")
    assert order.startswith("transcript-before-edit\n")
    assert "Keep the public API stable." in order
    messages = execution["steer_messages"]
    assert len(messages) == 1
    assert messages[0]["queued_at"] and messages[0]["delivered_at"]
    assert messages[0]["disposition"] == "accepted"
    assert messages[0]["resume_path"] == "session-resume"


def test_progress_poll_records_timestamped_typed_envelopes(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    queue = runtime / "steer.queue.jsonl"
    entry = task_run_lane_runner.enqueue_steer(queue, "lane-2", "Check the migration path.")
    watch = task_run_progress.LaneProgressWatch(
        stdout_log=runtime / "codex.stdout.log",
        stderr_log=runtime / "codex.stderr.log",
        worktree=tmp_path,
        base_sha="base",
        scope_specs=[],
        budget_seconds=0,
        poll_seconds=0.1,
    )

    watch.tick(1.0)
    pending = watch.pending_steers()
    watch.record_steer_delivery(pending, resume_path="relaunch-in-place")
    message = pending[0]

    assert message["message_id"] == entry["message_id"]
    assert message["queued_at"]
    assert message["delivered_at"]
    assert message["disposition"] == "accepted"
    assert task_run_lane_runner.read_steer_queue(queue)[0]["resume_path"] == "relaunch-in-place"


def test_task_steer_cli_returns_typed_accept_and_nack(tmp_path: Path, monkeypatch) -> None:
    cli = load_cli_module("charness_task_run_steer_accept", CLI)
    runtime = tmp_path / "runtime"
    record = {"task_id": "lane-3", "status": "running", "runner_pid": os.getpid()}
    monkeypatch.setattr(cli, "_load_task_run_lib", lambda _args: object())
    monkeypatch.setattr(task_run_runtime, "task_runtime_root", lambda _root: runtime)
    monkeypatch.setattr(task_run_runtime, "read_task_result", lambda *_args: dict(record))
    monkeypatch.setattr(
        task_run_runtime,
        "task_execution_runtime_root",
        lambda _root, _task_id: runtime / "lane-3" / "runtime",
    )
    emitted: list[dict[str, object]] = []
    monkeypatch.setattr(cli, "emit_yaml", emitted.append)

    code = cli.cmd_task_steer(
        argparse.Namespace(
            repo_root=tmp_path, task_id="lane-3", message="Narrow the retry.", amend_scope=None
        )
    )

    assert code == 0
    assert emitted[-1]["result_kind"] == "success"
    assert emitted[-1]["disposition"] == "accepted"
    assert emitted[-1]["queued_at"]
    assert task_run_lane_runner.read_steer_queue(
        runtime / "lane-3" / "runtime" / "steer.queue.jsonl"
    )

    monkeypatch.setattr(
        task_run_runtime, "read_task_result", lambda *_args: {**record, "status": "completed"}
    )
    code = cli.cmd_task_steer(
        argparse.Namespace(
            repo_root=tmp_path, task_id="lane-3", message="Too late.", amend_scope=None
        )
    )
    assert code == 1
    assert emitted[-1]["disposition"] == "nacked"
    assert emitted[-1]["result_kind"] == "failed"


def test_scope_amend_revalidates_same_candidate_without_relaunch(
    tmp_path: Path, monkeypatch
) -> None:
    cli = load_cli_module("charness_task_run_steer_amend", CLI)
    repo = _repo(tmp_path)
    base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "stray.py").write_text("VALUE = 3\n", encoding="utf-8")
    specs = task_run_scope.resolve_scope_specs(repo, ["module.py"], base_sha)
    result = {
        "task_id": "lane-4",
        "status": "completed-needs-review",
        "worktree_path": str(repo),
        "base_sha": base_sha,
        "target_sha": base_sha,
        "target_branch": "task/lane-4",
        "scope_specs": specs,
        "require_change": True,
        "candidate": {
            "status": "invalid",
            "changed_paths": ["stray.py"],
            "disallowed_paths": ["stray.py"],
        },
        "timestamps": {},
    }
    writes: list[dict[str, object]] = []
    monkeypatch.setattr(cli, "_load_task_run_lib", lambda _args: object())
    monkeypatch.setattr(task_run_runtime, "task_runtime_root", lambda _root: tmp_path / "runtime")
    monkeypatch.setattr(task_run_runtime, "read_task_result", lambda *_args: result)
    monkeypatch.setattr(
        task_run_runtime, "write_task_result", lambda _root, value: writes.append(value)
    )
    emitted: list[dict[str, object]] = []
    monkeypatch.setattr(cli, "emit_yaml", emitted.append)

    code = cli.cmd_task_steer(
        argparse.Namespace(
            repo_root=tmp_path,
            task_id="lane-4",
            message=None,
            amend_scope=["stray.py"],
        )
    )

    assert code == 0
    amendment = emitted[-1]
    assert amendment["disposition"] == "accepted"
    assert amendment["same_candidate"] is True
    assert amendment["executor_relaunched"] is False
    assert amendment["target_sha"] == base_sha
    assert writes and result["scope"]["verdict"] == task_run_scope.PASS
    assert result["candidate"]["disallowed_paths"] == []
    assert result["scope_amendments"][0]["result_kind"] == "success"


def test_steered_invocation_uses_resume_when_available_and_falls_back_in_place() -> None:
    initial = ["codex", "exec", "--output-last-message", "/tmp/last.txt", "-"]
    message = {
        "message_id": "m-1",
        "queued_at": "2026-09-24T00:00:00Z",
        "message": "Keep names stable.",
    }

    resumed, prompt, path = task_run_lane_runner.steered_lane_invocation(
        "codex", initial, "Original prompt.", [message], "session-1"
    )
    assert resumed[2:4] == ["resume", "session-1"]
    assert "Keep names stable." in prompt
    assert path == "session-resume"

    relaunched, _prompt, path = task_run_lane_runner.steered_lane_invocation(
        "codex", initial, "Original prompt.", [message], None
    )
    assert relaunched == initial
    assert path == "relaunch-in-place"
