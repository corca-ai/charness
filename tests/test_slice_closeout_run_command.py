from __future__ import annotations

import sys
from pathlib import Path

import scripts.slice_closeout_run_command as closeout_run


def test_progress_interval_ignores_invalid_env(monkeypatch) -> None:
    monkeypatch.setenv("CHARNESS_CLOSEOUT_PROGRESS_INTERVAL_SECONDS", "bad")
    assert closeout_run._progress_interval_seconds() == closeout_run.PROGRESS_INTERVAL_SECONDS
    monkeypatch.setenv("CHARNESS_CLOSEOUT_PROGRESS_INTERVAL_SECONDS", "0.01")
    assert closeout_run._progress_interval_seconds() == 0.1


def test_run_command_times_out_and_reports_progress(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(closeout_run, "COMMAND_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(closeout_run, "_progress_interval_seconds", lambda: 0.01)

    result = closeout_run.run_command(
        tmp_path,
        "python3 -c 'import time; time.sleep(1)'",
        "timeout-probe",
    )

    assert result["returncode"] == 124
    assert "timed out after 0.05s" in result["stderr"]
    assert "HEARTBEAT [timeout-probe] elapsed=" in capsys.readouterr().err


def test_run_command_emits_structured_heartbeats(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(closeout_run, "_progress_interval_seconds", lambda: 0.01)

    result = closeout_run.run_command(tmp_path, "python3 -c 'import time; time.sleep(0.2)'", "progress-wrap")

    assert result["returncode"] == 0
    stderr = capsys.readouterr().err
    assert "RUN [progress-wrap]" in stderr
    # `>= 2`, not merely present: a regression that beats once and then stops
    # beating (the emit moving out of the wait loop) satisfies "at least one".
    assert stderr.count("HEARTBEAT [progress-wrap] elapsed=") >= 2, stderr
    assert "PASS [progress-wrap]" in stderr


def test_run_command_reports_the_operator_command_not_the_path_wrapper(tmp_path: Path, capsys) -> None:
    """The PATH wrapper is this runner's plumbing; it must not reach the operator.

    `run_command` prepends `export PATH=<temp wrapper dir>:...` so `python3` and
    `pytest` resolve to the running interpreter. That prefix is longer than the
    lifecycle display budget, so leaking it would truncate away the command the
    operator is actually waiting on.
    """
    result = closeout_run.run_command(tmp_path, "python3 -c 'pass'", "wrapper-probe")

    assert result["command"] == "python3 -c 'pass'"
    assert result["returncode"] == 0
    assert isinstance(result["elapsed_seconds"], float)
    stderr = capsys.readouterr().err
    assert "RUN [wrapper-probe] python3 -c 'pass'" in stderr
    assert "export PATH=" not in stderr


def test_run_command_routes_python_through_the_running_interpreter(tmp_path: Path) -> None:
    """The wrapper seam itself: `python3` in a phase command must be `sys.executable`."""
    result = closeout_run.run_command(tmp_path, "python3 -c 'import sys; print(sys.executable)'", "interpreter")

    assert result["returncode"] == 0
    assert result["stdout"].strip() == sys.executable
