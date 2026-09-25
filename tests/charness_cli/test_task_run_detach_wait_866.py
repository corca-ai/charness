"""Detached lane launch and lane waiting (#866)."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from scripts.task_run import task_run_detach, task_run_runtime
from tests.charness_cli.support import CLI, build_test_path, load_cli_module, run_cli
from tests.charness_cli.test_task_run_fixtures import _git, _repo


class _StubChild:
    def __init__(self, code: int | None) -> None:
        self.returncode = code

    def poll(self) -> int | None:
        return self.returncode


def _seed_record(runtime: Path, task_id: str, **fields) -> Path:
    directory = runtime / "task-run" / task_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "result.json"
    record = {"task_id": task_id, "phase": "running", "status": "running"}
    record.update(fields)
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def _no_sleep(_seconds: float) -> None:
    raise AssertionError("waited although a terminal record was already present")


def test_wait_returns_already_terminal_lane_immediately(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    _seed_record(runtime, "lane-a", phase="terminal", status="premise-blocked")

    outcome = task_run_detach.wait_for_tasks(
        runtime, ["lane-a"], sleep=_no_sleep
    )

    assert outcome["finished"] == [
        {"task_id": "lane-a", "status": "premise-blocked", "exit_code": 2}
    ]
    assert outcome["pending"] == []
    assert outcome["exit_code"] == 2


def test_wait_any_returns_first_finished_lane(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    _seed_record(runtime, "lane-a", phase="terminal", status="failed")

    outcome = task_run_detach.wait_for_tasks(
        runtime, ["lane-a", "lane-b"], wait_any=True, sleep=_no_sleep
    )

    assert [entry["task_id"] for entry in outcome["finished"]] == ["lane-a"]
    assert outcome["pending"] == ["lane-b"]
    assert outcome["exit_code"] == 1


def test_wait_all_reports_first_non_success_in_cli_order(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    _seed_record(runtime, "lane-a", phase="terminal", status="completed")
    _seed_record(runtime, "lane-b", phase="terminal", status="premise-blocked")

    outcome = task_run_detach.wait_for_tasks(
        runtime, ["lane-a", "lane-b"], sleep=_no_sleep
    )

    assert outcome["exit_code"] == 2
    assert [entry["status"] for entry in outcome["finished"]] == [
        "completed",
        "premise-blocked",
    ]


def test_wait_times_out_on_missing_record(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"

    outcome = task_run_detach.wait_for_tasks(
        runtime, ["lane-ghost"], timeout_seconds=0.05, poll_seconds=0.01
    )

    assert outcome["exit_code"] == 1
    assert outcome["pending"] == ["lane-ghost"]
    assert "lane-ghost" in outcome["error"]


def test_wait_picks_up_a_lane_that_ends_mid_wait(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"

    def finish_lane() -> None:
        _seed_record(runtime, "lane-slow", phase="terminal", status="completed")

    timer = threading.Timer(0.05, finish_lane)
    timer.start()
    try:
        outcome = task_run_detach.wait_for_tasks(
            runtime, ["lane-slow"], poll_seconds=0.01
        )
    finally:
        timer.join()

    assert outcome["finished"] == [
        {"task_id": "lane-slow", "status": "completed", "exit_code": 0}
    ]
    assert outcome["exit_code"] == 0


def test_launch_reports_terminal_refusal_with_its_exit_code(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    _seed_record(runtime, "lane-a", phase="terminal", status="premise-blocked")

    outcome = task_run_detach.wait_for_launch(
        runtime, "lane-a", _StubChild(2), sleep=_no_sleep
    )

    assert outcome == {
        "launched": False,
        "task_id": "lane-a",
        "status": "premise-blocked",
        "result_path": str(runtime / "task-run" / "lane-a" / "result.json"),
        "exit_code": 2,
    }


def test_launch_returns_zero_only_after_carrier_start(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    log = runtime / "task-run" / "lane-a" / "codex.stdout.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("", encoding="utf-8")
    _seed_record(
        runtime,
        "lane-a",
        phase="running",
        status="running",
        logs={"stdout": str(log), "stderr": str(log.parent / "codex.stderr.log")},
    )

    outcome = task_run_detach.wait_for_launch(
        runtime, "lane-a", _StubChild(None), sleep=_no_sleep
    )

    assert outcome["launched"] is True
    assert outcome["exit_code"] == 0
    assert outcome["task_id"] == "lane-a"


def test_launch_running_record_without_logs_is_not_a_start(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    _seed_record(runtime, "lane-a", phase="running", status="running")

    outcome = task_run_detach.wait_for_launch(
        runtime, "lane-a", _StubChild(1), settle_seconds=0, sleep=lambda s: None
    )

    assert outcome["launched"] is False
    assert outcome["exit_code"] == 1


def test_launch_dead_child_without_record_is_never_zero(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"

    outcome = task_run_detach.wait_for_launch(
        runtime, "lane-ghost", _StubChild(1), settle_seconds=0, sleep=lambda s: None
    )

    assert outcome["launched"] is False
    assert outcome["exit_code"] == 1


def test_child_argv_drops_detach_and_forwards_repeats() -> None:
    args = argparse.Namespace(
        repo_root=Path("/repo"),
        lane="feature",
        path=None,
        branch=None,
        base=None,
        scope=["pkg", "other.py"],
        prompt="do it",
        prompt_file=None,
        executor="codex",
        effort="xhigh",
        task_id=None,
        prepare=True,
        skip_prepare=False,
        allow_no_change=False,
        report_only=False,
        self_review_policy="auto",
        critical_lane=False,
        acceptance_skeleton=None,
        premise_check=[["p1", "premise one", "decide one"]],
        timeout_seconds=3600,
        no_progress_seconds=None,
        rules_file=[Path("/rules/a.md")],
        grant_writable=[],
        charness_checkout=None,
        home_root=Path("/home-root"),
        detach=True,
        dry_run=False,
    )

    argv = task_run_detach.child_argv(["charness"], args)

    assert "--detach" not in argv
    assert argv[:3] == ["charness", "task", "run"]
    assert argv.count("--scope") == 2
    assert ["--premise-check", "p1", "premise one", "decide one"] == argv[
        argv.index("--premise-check") : argv.index("--premise-check") + 4
    ]
    assert "--rules-file" in argv
    assert "--prepare" in argv


def test_preview_task_id_derives_explicit_branch_id() -> None:
    assert task_run_detach.preview_task_id("lane-1", None, None) == "lane-1"
    derived = task_run_detach.preview_task_id(None, "lane/thing", None)
    assert derived.startswith("lane-thing-")
    with pytest.raises(ValueError, match="--branch"):
        task_run_detach.preview_task_id(None, None, None)
    with pytest.raises(task_run_detach._runtime.TaskRunError, match="--lane"):
        task_run_detach.preview_task_id("not valid!!", None, None)


def test_task_wait_cli_names_id_and_status(tmp_path: Path, monkeypatch) -> None:
    cli = load_cli_module("charness_task_wait_cli", CLI)
    runtime = tmp_path / "runtime"
    _seed_record(runtime, "lane-a", phase="terminal", status="premise-blocked")
    monkeypatch.setattr(cli, "_load_task_run_lib", lambda _args: object())
    monkeypatch.setattr(
        task_run_runtime, "task_runtime_root", lambda _root: runtime
    )
    emitted: list[dict] = []
    monkeypatch.setattr(cli, "emit_yaml", emitted.append)

    code = cli.cmd_task_wait(
        argparse.Namespace(
            repo_root=tmp_path, task_ids=["lane-a"], any=False, timeout_seconds=0
        )
    )

    assert code == 2
    assert emitted[-1]["finished"][0]["task_id"] == "lane-a"
    assert emitted[-1]["finished"][0]["status"] == "premise-blocked"


def test_detach_end_to_end_returns_zero_then_wait_times_out(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    codex = bin_dir / "codex"
    # The read-only brief-critique probe answers fast (advisory path); the
    # lane executor itself stays slow so the carrier-start signal precedes
    # the terminal receipt.
    codex.write_text(
        "#!/bin/sh\ncase \"$*\" in\n*read-only*) exit 1;;\n*) sleep 25;;\nesac\n",
        encoding="utf-8",
    )
    codex.chmod(0o755)
    env = dict(os.environ, PATH=build_test_path(bin_dir))

    launched = run_cli(
        "task",
        "run",
        "--repo-root",
        str(repo),
        "--lane",
        "e2e-detach",
        "--scope",
        "module.py",
        "--prompt",
        "inspect the selected base",
        "--effort",
        "medium",
        "--skip-prepare",
        "--detach",
        env=env,
    )

    assert launched.returncode == 0, launched.stderr
    assert "e2e-detach" in launched.stdout
    try:
        waited = run_cli(
            "task",
            "wait",
            "--repo-root",
            str(repo),
            "e2e-detach",
            "--timeout-seconds",
            "4",
            env=env,
        )
        assert waited.returncode == 1
        assert "e2e-detach" in waited.stdout
    finally:
        runtime = task_run_runtime.task_runtime_root(repo)
        record = task_run_runtime.read_task_result(runtime, "e2e-detach")
        if record is not None and record.get("phase") != "terminal":
            pid = record.get("runner_pid")
            if isinstance(pid, int) and pid > 0:
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass


def test_result_paths_refuses_invalid_task_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invalid task id"):
        task_run_detach.result_paths(tmp_path, "NOT A TASK ID!")


def test_carrier_started_accepts_terminal_payload() -> None:
    assert task_run_detach.carrier_started({"phase": "terminal"}) is True
    assert task_run_detach.carrier_started(None) is False
    assert task_run_detach.carrier_started({"phase": "planned"}) is False


def test_entry_command_prefers_path_lookup(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["python3"])
    entry = task_run_detach.entry_command()
    assert entry == [str(Path(shutil.which("python3")))]


def test_target_argv_spells_explicit_selection() -> None:
    args = argparse.Namespace(
        lane=None, path="/tmp/x", branch="lane-b", base="main", task_id="lane-b"
    )
    assert task_run_detach._target_argv(args) == [
        "--path",
        "/tmp/x",
        "--branch",
        "lane-b",
        "--base",
        "main",
        "--task-id",
        "lane-b",
    ]
    bare = argparse.Namespace(lane=None, path="/tmp/x", branch="lane-b", base=None, task_id=None)
    assert task_run_detach._target_argv(bare) == ["--path", "/tmp/x", "--branch", "lane-b"]
    assert task_run_detach._target_argv(argparse.Namespace(lane="a")) == ["--lane", "a"]


def test_prompt_argv_spells_prompt_file_branch() -> None:
    args = argparse.Namespace(
        prompt=None,
        prompt_file="/tmp/p.md",
        scope=[],
        executor="codex",
        effort="high",
    )
    assert task_run_detach._prompt_argv(args) == [
        "--prompt-file",
        "/tmp/p.md",
        "--executor",
        "codex",
        "--effort",
        "high",
    ]


def test_mode_and_option_argv_spell_every_flag() -> None:
    mode = argparse.Namespace(
        prepare=True,
        skip_prepare=False,
        allow_no_change=True,
        report_only=False,
        critical_lane=True,
        self_review_policy="always",
        acceptance_skeleton="accept.json",
        premise_check=[["check-one"]],
        timeout_seconds=60,
        no_progress_seconds=5,
    )
    assert task_run_detach._mode_argv(mode) == [
        "--prepare",
        "--allow-no-change",
        "--critical-lane",
        "--self-review",
        "--acceptance-skeleton",
        "accept.json",
        "--premise-check",
        "check-one",
        "--timeout-seconds",
        "60",
        "--no-progress-seconds",
        "5",
    ]
    options = argparse.Namespace(
        rules_file=["rules.md"],
        grant_writable=["/tmp/g"],
        charness_checkout="/tmp/c",
        home_root="/tmp/h",
    )
    assert task_run_detach._option_argv(options) == [
        "--rules-file",
        "rules.md",
        "--grant-writable",
        "/tmp/g",
        "--charness-checkout",
        "/tmp/c",
        "--home-root",
        "/tmp/h",
    ]


def test_read_record_fails_open_on_missing_result(tmp_path: Path, monkeypatch) -> None:
    assert task_run_detach.read_record(tmp_path / "runtime", "lane-a") is None
    monkeypatch.setattr(
        task_run_detach._runtime,
        "read_task_result",
        lambda _runtime_path, _task_id: (_ for _ in ()).throw(OSError("gone")),
    )
    assert task_run_detach.read_record(tmp_path / "runtime", "lane-a") is None


def test_launch_dead_child_then_terminal_record_reports_refusal(
    tmp_path: Path, monkeypatch
) -> None:
    runtime = tmp_path / "runtime"
    reads = iter(
        [
            {"task_id": "lane-a", "phase": "planned", "status": "planned"},
            {"task_id": "lane-a", "phase": "terminal", "status": "premise-blocked"},
        ]
    )
    monkeypatch.setattr(
        task_run_detach._runtime,
        "read_task_result",
        lambda _runtime_path, _task_id: next(reads),
    )
    outcome = task_run_detach.wait_for_launch(
        runtime, "lane-a", _StubChild(2), settle_seconds=0, sleep=lambda s: None
    )
    assert outcome["launched"] is False
    assert outcome["status"] == "premise-blocked"
    assert outcome["exit_code"] == 2


def test_launch_dead_child_then_start_signal_reports_launched(tmp_path: Path, monkeypatch) -> None:
    runtime = tmp_path / "runtime"
    reads = iter(
        [
            {"task_id": "lane-a", "phase": "planned", "status": "planned"},
            {"task_id": "lane-a", "phase": "executing", "status": "running"},
        ]
    )
    monkeypatch.setattr(
        task_run_detach._runtime,
        "read_task_result",
        lambda _runtime_path, _task_id: next(reads),
    )
    outcome = task_run_detach.wait_for_launch(
        runtime, "lane-a", _StubChild(2), settle_seconds=0, sleep=lambda s: None
    )
    assert outcome["launched"] is True
    assert outcome["exit_code"] == 0


def test_launch_wait_times_out_without_start_signal(tmp_path: Path, monkeypatch) -> None:
    runtime = tmp_path / "runtime"
    monkeypatch.setattr(
        task_run_detach._runtime,
        "read_task_result",
        lambda _runtime_path, _task_id: {
            "task_id": "lane-a",
            "phase": "planned",
            "status": "planned",
        },
    )
    outcome = task_run_detach.wait_for_launch(
        runtime,
        "lane-a",
        _StubChild(None),
        timeout_seconds=0,
        now=lambda: 100.0,
        sleep=lambda s: None,
    )
    assert outcome["launched"] is False
    assert outcome["exit_code"] == 1
    assert "task wait" in outcome["error"]


def test_launch_detached_command_refuses_lane_with_task_id() -> None:
    from scripts.task_run.task_run_contract import TaskRunError

    with pytest.raises(TaskRunError, match="derived from --lane"):
        task_run_detach.launch_detached_command(
            argparse.Namespace(dry_run=False, lane="lane-a", task_id="lane-a")
        )


def test_launch_detached_command_wraps_preview_errors() -> None:
    from scripts.task_run.task_run_contract import TaskRunError

    with pytest.raises(TaskRunError, match="--branch"):
        task_run_detach.launch_detached_command(
            argparse.Namespace(dry_run=False, lane=None, branch=None, task_id=None)
        )


def test_fresh_exec_runs_detach_bootstrap_without_repo_root() -> None:
    import importlib.util

    from tests.module_eviction import evict_new_modules

    path = Path(task_run_detach.__file__)
    spec = importlib.util.spec_from_file_location("fresh_detach_bootstrap", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    saved = sys.path[:]
    root = str(Path(path).resolve().parents[2])
    sys.path[:] = [entry for entry in saved if os.path.abspath(entry) != root]
    before = set(sys.modules)
    try:
        sys.modules["fresh_detach_bootstrap"] = module
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved
        evict_new_modules(before)
    assert module.TERMINAL_PHASE == "terminal"
