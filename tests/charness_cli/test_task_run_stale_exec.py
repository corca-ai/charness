from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.gates_support import runtime_root_retention as retention
from scripts.task_run import task_run_runtime, task_run_stale_exec


def test_stale_exec_with_dead_runner_uses_the_canonical_terminal_writer(
    tmp_path: Path, monkeypatch
) -> None:
    runtime = tmp_path / "runtime"
    task_id = "orphan-lane"
    payload = {
        "task_id": task_id,
        "status": "running",
        "phase": "exec",
        "runner_pid": 901,
        "keep_worktree": True,
    }
    result_path = task_run_runtime.write_task_result(runtime, payload)
    now = 1_800_000_000.0
    os.utime(result_path, (now - 2 * 86400, now - 2 * 86400))
    pid_table = {901: False}
    monkeypatch.setattr(
        task_run_stale_exec._support,
        "runner_liveness",
        lambda record: {"runner_pid": record.get("runner_pid"), "alive": pid_table.get(record.get("runner_pid"))},
    )
    terminal_calls: list[dict[str, object]] = []
    canonical_terminal = task_run_stale_exec._terminal

    def observe_terminal(*args, **kwargs):
        terminal_calls.append(dict(kwargs))
        return canonical_terminal(*args, **kwargs)

    monkeypatch.setattr(task_run_stale_exec, "_terminal", observe_terminal)

    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime,
        task_id,
        stale_before=now - retention.ACTIVE_WINDOW_DAYS * 86400,
    )

    saved = task_run_runtime.read_task_result(runtime, task_id)
    assert outcome["transitioned"] is True
    assert terminal_calls == [
        {
            "status": "interrupted",
            "error": "The task-run runner exited before writing a terminal receipt.",
            "next_step": (
                "The exec runner is no longer present and its lane record is outside the "
                "active window; inspect the retained worktree before retrying."
            ),
        }
    ]
    assert saved is not None
    assert saved["phase"] == "terminal"
    assert saved["status"] == "interrupted"
    assert saved["result_kind"] == "failed"


@pytest.mark.parametrize(
    ("runner_alive", "record_age", "expected_reason"),
    [
        (True, 2 * 86400, "runner-not-confirmed-dead"),
        (False, 60, "record-fresh"),
    ],
)
def test_stale_exec_reaper_leaves_live_or_fresh_records_untouched(
    tmp_path: Path,
    monkeypatch,
    runner_alive: bool,
    record_age: float,
    expected_reason: str,
) -> None:
    runtime = tmp_path / "runtime"
    task_id = "untouched-lane"
    payload = {
        "task_id": task_id,
        "status": "running",
        "phase": "exec",
        "runner_pid": 902,
    }
    result_path = task_run_runtime.write_task_result(runtime, payload)
    now = 1_800_000_000.0
    os.utime(result_path, (now - record_age, now - record_age))
    pid_table = {902: runner_alive}
    monkeypatch.setattr(
        task_run_stale_exec._support,
        "runner_liveness",
        lambda record: {"runner_pid": record.get("runner_pid"), "alive": pid_table.get(record.get("runner_pid"))},
    )
    before = result_path.read_bytes()
    monkeypatch.setattr(
        task_run_stale_exec,
        "_terminal",
        lambda *_args, **_kwargs: pytest.fail("ineligible stale exec reached _terminal"),
    )

    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime,
        task_id,
        stale_before=now - retention.ACTIVE_WINDOW_DAYS * 86400,
    )

    assert outcome == {"transitioned": False, "reason": expected_reason}
    assert result_path.read_bytes() == before
