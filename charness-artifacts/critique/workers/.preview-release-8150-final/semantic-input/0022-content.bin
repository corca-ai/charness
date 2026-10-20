"""The progress rule reaches a running lane: preempt, resume with its message, or stop.

The fake executor owns a lower-level claim: it emits Codex-shaped events and
waits to be killed, and a `resume` invocation records the prompt it was
given. It does not claim live Codex behavior (a SIGKILLed `codex exec`
session resuming with its context was probed by hand on codex-cli 0.163.0;
see charness-artifacts/spec/lane-progress-rule.md).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from scripts.task_run import (
    task_run_execution,
    task_run_lane_runner,
    task_run_progress,
)
from tests.charness_cli.test_task_run_fixtures import _git, _repo

pytestmark = pytest.mark.boundary_contract(
    reason="the claim is that a real executor process is killed and resumed with the rule's message"
)

TEST = "pytest -q tests/test_a.py"


def _event(kind: str, item_id: str) -> str:
    return json.dumps(
        {"type": kind, "item": {"id": item_id, "type": "command_execution",
                                "command": TEST, "exit_code": 1}}
    )


def _fake_codex(tmp_path: Path, first_turn: list[str]) -> Path:
    fake = tmp_path / "fake-codex"
    lines = "".join(f"    print({line!r}, flush=True)\n" for line in first_turn)
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, sys, time\n"
        "args = sys.argv[1:]\n"
        "prompt = sys.stdin.read()\n"
        "log = pathlib.Path(os.environ['INVOCATIONS_LOG'])\n"
        "with log.open('a') as handle:\n"
        "    handle.write(json.dumps({'args': args, 'prompt': prompt}) + '\\n')\n"
        "output = pathlib.Path(args[args.index('--output-last-message') + 1])\n"
        "calls = len(log.read_text().splitlines())\n"
        "if 'resume' not in args:\n"
        "    print(json.dumps({'type': 'thread.started', 'thread_id': 'session-1'}), flush=True)\n"
        f"{lines}"
        "    time.sleep(60)\n"
        "elif os.environ.get('RESUME_HANGS') == '1':\n"
        "    time.sleep(60)\n"
        "else:\n"
        "    output.write_text('resumed and finished\\n')\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake


def _run(tmp_path: Path, fake: Path, **env: str) -> tuple[dict, list[dict], list[dict]]:
    repo = _repo(tmp_path)
    runtime = tmp_path / "runtime" / "lane-1"
    runtime.mkdir(parents=True)
    stdout_log, stderr_log = runtime / "codex.stdout.log", runtime / "codex.stderr.log"
    invocations = tmp_path / "invocations.jsonl"
    command = task_run_lane_runner.lane_command(
        executor="codex",
        executable=str(fake),
        effort="xhigh",
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
        base_sha=_git(repo, "rev-parse", "HEAD").stdout.strip(),
        scope_specs=[],
    )
    execution = task_run_execution._execute_codex(
        command,
        prompt="Implement the lane request.",
        target_path=repo,
        configured_env={**os.environ, "INVOCATIONS_LOG": str(invocations), **env},
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=None,
        lane_watch=watch,
        executor="codex",
    )
    calls = [json.loads(line) for line in invocations.read_text(encoding="utf-8").splitlines()]
    queue = task_run_lane_runner.read_steer_queue(runtime / "steer.queue.jsonl")
    assert watch is not None
    execution["progress_guard"] = watch.receipt()
    return execution, calls, queue


def test_a_third_identical_test_run_preempts_and_resumes_with_the_debug_request(
    tmp_path: Path,
) -> None:
    fake = _fake_codex(
        tmp_path,
        [_event(kind, f"c{n}") for n in range(3) for kind in ("item.started", "item.completed")],
    )

    execution, calls, queue = _run(tmp_path, fake)

    assert execution["exit_code"] == 0
    assert execution["preemptions"] == 1
    assert "progress_stopped" not in execution
    assert len(calls) == 2
    resumed = calls[1]["args"]
    assert resumed[resumed.index("resume") + 1] == "session-1"
    assert "switch to the debug skill" in calls[1]["prompt"].lower()
    (message,) = queue
    assert message["actor"] == "charness-progress-rule"
    assert message["resume_path"] == "session-resume"
    rule = execution["progress_guard"]["progress_rule"]
    assert [item["reason_code"] for item in rule["messages"]] == ["loop-debug"]


def test_a_silent_lane_gets_a_checkpoint_request_then_is_stopped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No wall clock bounds this lane: only the rule's two empty windows do."""
    monkeypatch.setenv("CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS", "0.3")
    monkeypatch.setenv("CHARNESS_TASK_RUN_PROGRESS_POLL_SECONDS", "0.05")
    fake = _fake_codex(tmp_path, [])

    execution, calls, queue = _run(tmp_path, fake, RESUME_HANGS="1")

    assert len(calls) == 2  # the first turn, then the resumed request
    assert "commit it now" in calls[1]["prompt"]
    assert [item["actor"] for item in queue] == ["charness-progress-rule"]
    assert "checkpoint request went unanswered" in execution["progress_stopped"]
    rule = execution["progress_guard"]["progress_rule"]
    assert [check["progress"] for check in rule["checks"]] == [False, False]
    assert [item["reason_code"] for item in rule["messages"]] == ["no-progress"]
    assert rule["messages"][0]["answered"] is False


def test_a_loop_that_ignores_both_requests_is_stopped_from_the_event_reader(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    runtime = tmp_path / "runtime" / "lane-1"
    runtime.mkdir(parents=True)
    watch = task_run_progress.build_progress_watch(
        require_change=False,
        stdout_log=runtime / "codex.stdout.log",
        stderr_log=runtime / "codex.stderr.log",
        worktree=repo,
        base_sha=_git(repo, "rev-parse", "HEAD").stdout.strip(),
        scope_specs=[],
    )
    assert watch is not None
    completed = [json.loads(_event("item.completed", f"c{n}")) for n in range(5)]
    watch.observe_event(completed[0])  # before start: nothing to preempt yet
    kills: list[str] = []
    watch.start(emit=lambda *_args: None, kill=lambda: kills.append("kill"))
    preempted: list[bool] = []
    try:
        for event in completed[1:]:
            watch.observe_event(event)
            preempted.append(watch.take_preempted())  # the loop's per-invocation read
    finally:
        watch.stop()

    # 3rd and 4th runs preempted with messages; the 5th stopped the lane.
    assert preempted == [False, True, True, False]
    assert watch.preemptions == 2
    assert kills == ["kill", "kill", "kill"]
    assert watch.stop_reason is not None and watch.stop_reason.startswith("loop:")
    stderr = (runtime / "codex.stderr.log").read_text(encoding="utf-8")
    assert "NO-PROGRESS-STOP: loop:" in stderr


def _started_watch(tmp_path: Path) -> tuple[task_run_progress.LaneProgressWatch, list[str], Path]:
    repo = _repo(tmp_path)
    runtime = tmp_path / "runtime" / "lane-1"
    runtime.mkdir(parents=True)
    watch = task_run_progress.build_progress_watch(
        require_change=False,
        stdout_log=runtime / "codex.stdout.log",
        stderr_log=runtime / "codex.stderr.log",
        worktree=repo,
        base_sha=_git(repo, "rev-parse", "HEAD").stdout.strip(),
        scope_specs=[],
    )
    assert watch is not None
    kills: list[str] = []
    watch.start(emit=lambda *_args: None, kill=lambda: kills.append("kill"))
    watch.stop()  # drive it by hand; no poll thread
    return watch, kills, runtime / "steer.queue.jsonl"


def test_messages_in_one_invocation_share_one_preemption_and_lose_to_a_stop(
    tmp_path: Path,
) -> None:
    from scripts.task_run.task_run_progress_rule import Action

    watch, kills, queue = _started_watch(tmp_path)
    watch._apply(Action("message", "first", "loop-debug"))
    watch._apply(Action("message", "second", "no-progress"))
    assert (watch.preemptions, kills) == (1, ["kill"])
    assert len(task_run_lane_runner.read_steer_queue(queue)) == 2

    # The stop wins before the resume delivers them: both are superseded and
    # the preemption that never became a resume is not counted.
    watch._stop_now("stopped by the rule")
    queued = task_run_lane_runner.read_steer_queue(queue)
    assert {(item["disposition"], item["reason_code"]) for item in queued} == {
        ("nacked", "superseded-by-stop")
    }
    assert (watch.preemptions, watch.take_preempted()) == (0, False)
    watch._apply(Action("message", "too late", "no-progress"))
    assert watch.suppressed_actions == 3
    assert len(task_run_lane_runner.read_steer_queue(queue)) == 2
    assert watch.receipt()["suppressed_actions"] == 3


def test_a_message_raised_after_the_rule_decided_to_stop_is_suppressed(
    tmp_path: Path,
) -> None:
    from scripts.task_run.task_run_progress_rule import Action

    watch, kills, queue = _started_watch(tmp_path)
    watch._progress_rule.stop_reason = "the rule stopped first"  # watch not yet told
    watch._apply(Action("message", "late", "loop-debug"))

    assert (watch.suppressed_actions, kills) == (1, [])
    assert task_run_lane_runner.read_steer_queue(queue) == []


def test_failing_due_checks_stop_the_lane_even_with_quiet_polls_between(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    watch, _kills, _queue = _started_watch(tmp_path)
    calls = {"n": 0}

    def due_checks_fail(_now: float) -> None:
        calls["n"] += 1
        if calls["n"] % 2 == 0:
            raise RuntimeError("fingerprint exploded")
        return None  # an ordinary poll: no check was due

    monkeypatch.setattr(watch._progress_rule, "on_tick", due_checks_fail)
    reasons = [watch._tick_rule(float(n)) for n in range(2 * task_run_progress.MAX_RULE_FAILURES)]

    assert all(reason is None for reason in reasons[:-1])
    assert reasons[-1] is not None and "cannot be bounded" in reasons[-1]


def test_a_watch_that_cannot_check_stops_the_lane_instead_of_leaving_it_unbounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    watch, _kills, _queue = _started_watch(tmp_path)

    def broken_poll(_now: float) -> None:
        raise RuntimeError("log unreadable")

    def broken_rule(_now: float) -> None:
        raise RuntimeError("fingerprint exploded")

    monkeypatch.setattr(watch, "_poll", broken_poll)
    monkeypatch.setattr(watch._progress_rule, "on_tick", broken_rule)
    reasons = [watch.tick(float(n)) for n in range(task_run_progress.MAX_RULE_FAILURES)]

    assert reasons[:-1] == [None] * (task_run_progress.MAX_RULE_FAILURES - 1)
    assert reasons[-1] is not None and "cannot be bounded" in reasons[-1]


def test_a_stopped_watch_ignores_events_and_a_second_stop_and_its_poll_ends(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CHARNESS_TASK_RUN_PROGRESS_POLL_SECONDS", "0.05")
    repo = _repo(tmp_path)
    runtime = tmp_path / "runtime" / "lane-1"
    runtime.mkdir(parents=True)
    watch = task_run_progress.build_progress_watch(
        require_change=False,
        stdout_log=runtime / "codex.stdout.log",
        stderr_log=runtime / "codex.stderr.log",
        worktree=repo,
        base_sha=_git(repo, "rev-parse", "HEAD").stdout.strip(),
        scope_specs=[],
    )
    assert watch is not None
    kills: list[str] = []
    watch.start(emit=lambda *_args: None, kill=lambda: kills.append("kill"))
    watch._stop_now("first stop")
    watch._stop_now("second stop")  # first wins
    watch.observe_event(json.loads(_event("item.completed", "c1")))  # ignored
    watch._thread.join(timeout=30)  # the poll loop ends on its own once stopped

    assert not watch._thread.is_alive()
    assert (watch.stop_reason, kills) == ("first stop", ["kill"])
    watch.stop()
