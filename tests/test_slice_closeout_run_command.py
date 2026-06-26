from __future__ import annotations

import subprocess
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
    assert "." in capsys.readouterr().err


def test_run_command_wraps_progress_dots_every_eighty(monkeypatch, tmp_path: Path, capsys) -> None:
    class FakeProcess:
        returncode = 0

        def __init__(self) -> None:
            self.calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls <= 80:
                raise subprocess.TimeoutExpired(["fake"], timeout)
            return "", ""

    monkeypatch.setattr(closeout_run.subprocess, "Popen", lambda *_args, **_kwargs: FakeProcess())
    monkeypatch.setattr(closeout_run, "_progress_interval_seconds", lambda: 0.01)
    monkeypatch.setattr(closeout_run.time, "monotonic", lambda: 0.0)

    result = closeout_run.run_command(tmp_path, "python3 -c 'pass'", "progress-wrap")

    assert result["returncode"] == 0
    stderr = capsys.readouterr().err
    assert "." * 80 in stderr
    assert "\nPASS [progress-wrap]" in stderr
