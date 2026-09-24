from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.gates_support import runtime_root_retention as retention
from scripts.task_run import task_run_runtime, task_run_stale_exec


def test_stale_exec_direct_entrypoint_bootstraps_from_real_script_path(
    tmp_path: Path,
) -> None:
    script = Path(task_run_stale_exec.__file__).resolve()
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "terminalize-stale-exec" in completed.stdout


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


def _stale_runtime(tmp_path: Path, *, phase: str = "exec", age_days: int = 2):
    runtime = tmp_path / "runtime"
    payload = {
        "task_id": "orphan-lane",
        "status": "running",
        "phase": phase,
        "runner_pid": 901,
        "keep_worktree": True,
    }
    result_path = task_run_runtime.write_task_result(runtime, payload)
    now = 1_800_000_000.0
    os.utime(result_path, (now - age_days * 86400, now - age_days * 86400))
    return runtime, result_path, now


def _pid_table(monkeypatch, table: dict) -> None:
    monkeypatch.setattr(
        task_run_stale_exec._support,
        "runner_liveness",
        lambda record: {
            "runner_pid": record.get("runner_pid"),
            "alive": table.get(record.get("runner_pid")),
        },
    )


def test_terminalize_rejects_missing_record(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir()

    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime, "nope", stale_before=1_700_000_000.0
    )

    assert outcome == {"transitioned": False, "reason": "record-missing"}


def test_terminalize_rejects_nonfinite_cutoff(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="stale_before must be finite"):
        task_run_stale_exec.terminalize_stale_exec(
            tmp_path, "x", stale_before=float("nan")
        )


def test_terminalize_skips_terminal_records(tmp_path: Path) -> None:
    runtime, _path, now = _stale_runtime(tmp_path, phase="terminal")

    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime, "orphan-lane", stale_before=now - 86400
    )

    assert outcome == {"transitioned": False, "reason": "already-terminal"}


def test_terminalize_treats_unstatable_record_as_missing(
    tmp_path: Path, monkeypatch
) -> None:
    runtime, result_path, now = _stale_runtime(tmp_path)
    _pid_table(monkeypatch, {901: False})
    payload = task_run_runtime.read_task_result(runtime, "orphan-lane")
    assert payload is not None
    # `read_task_result` probes `is_file` (a stat) before the guarded `stat`
    # below; serve the payload directly so only the guarded call can fail.
    monkeypatch.setattr(
        task_run_stale_exec._support, "read_task_result", lambda _r, _t: payload
    )
    real_stat = Path.stat

    def _fail(self: Path):
        if self == result_path:
            raise OSError("gone")
        return real_stat(self)

    monkeypatch.setattr(Path, "stat", _fail)
    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime, "orphan-lane", stale_before=now - 86400
    )

    assert outcome == {"transitioned": False, "reason": "record-missing"}


def test_terminalize_skips_fresh_records(tmp_path: Path, monkeypatch) -> None:
    runtime, _path, now = _stale_runtime(tmp_path, age_days=0)
    _pid_table(monkeypatch, {901: False})

    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime, "orphan-lane", stale_before=now - 86400
    )

    assert outcome == {"transitioned": False, "reason": "record-fresh"}


def test_terminalize_skips_live_runners(tmp_path: Path, monkeypatch) -> None:
    runtime, _path, now = _stale_runtime(tmp_path)
    _pid_table(monkeypatch, {901: True})

    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime, "orphan-lane", stale_before=now - 86400
    )

    assert outcome == {"transitioned": False, "reason": "runner-not-confirmed-dead"}


def test_terminalize_dry_run_reports_without_writing(
    tmp_path: Path, monkeypatch
) -> None:
    runtime, result_path, now = _stale_runtime(tmp_path)
    _pid_table(monkeypatch, {901: False})
    before = result_path.read_bytes()

    outcome = task_run_stale_exec.terminalize_stale_exec(
        runtime, "orphan-lane", stale_before=now - 86400, dry_run=True
    )

    assert outcome["transitioned"] is False
    assert outcome["would_transition"] is True
    assert outcome["status"] == "interrupted"
    assert result_path.read_bytes() == before


def _main_with(monkeypatch, capsys, outcome: dict) -> dict:
    import yaml

    monkeypatch.setattr(
        task_run_stale_exec, "terminalize_stale_exec", lambda *a, **k: dict(outcome)
    )
    argv = [
        "terminalize-stale-exec",
        "--runtime-root",
        "rt",
        "--task-id",
        "t",
        "--stale-before",
        "1.0",
    ]
    assert task_run_stale_exec.main(argv) == 0
    return yaml.safe_load(capsys.readouterr().out)


def test_main_reports_terminalized_transition(tmp_path, monkeypatch, capsys) -> None:
    printed = _main_with(monkeypatch, capsys, {"transitioned": True})

    assert printed["log_entry"]["action"] == "terminalized"


def test_main_reports_would_transition(tmp_path, monkeypatch, capsys) -> None:
    printed = _main_with(
        monkeypatch, capsys, {"transitioned": False, "would_transition": True}
    )

    assert printed["log_entry"]["action"] == "would-terminalize"


def test_main_reports_live_skip(tmp_path, monkeypatch, capsys) -> None:
    printed = _main_with(
        monkeypatch,
        capsys,
        {"transitioned": False, "reason": "runner-not-confirmed-dead"},
    )

    assert printed["log_entry"]["action"] == "skipped"


def test_main_reports_fresh_skip(tmp_path, monkeypatch, capsys) -> None:
    printed = _main_with(
        monkeypatch, capsys, {"transitioned": False, "reason": "record-fresh"}
    )

    assert printed["log_entry"]["action"] == "skipped"


def test_main_reports_plain_outcome_without_log_entry(
    tmp_path, monkeypatch, capsys
) -> None:
    printed = _main_with(
        monkeypatch, capsys, {"transitioned": False, "reason": "record-missing"}
    )

    assert "log_entry" not in printed
