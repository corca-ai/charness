from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

import scripts.script_timeout as script_timeout
from scripts.script_timeout import resolve_timeout_seconds

ROOT = Path(__file__).resolve().parents[1]


def test_resolve_timeout_seconds_ignores_invalid_env(monkeypatch) -> None:
    monkeypatch.setenv("CHARNESS_SCRIPT_TIMEOUT_SECONDS", "bad")
    assert resolve_timeout_seconds(default_seconds=7) == 7


def test_arm_cli_timeout_exits_in_subprocess(tmp_path: Path) -> None:
    script = tmp_path / "slow.py"
    script.write_text(
        "\n".join(
            [
                "import sys",
                "import time",
                f"sys.path.insert(0, {str(ROOT)!r})",
                "from runtime_bootstrap import arm_cli_timeout",
                "cancel_timeout = arm_cli_timeout(label='slow-script', default_seconds=5)",
                "try:",
                "    time.sleep(0.2)",
                "finally:",
                "    cancel_timeout()",
                "",
            ]
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["CHARNESS_SCRIPT_TIMEOUT_SECONDS"] = "0.05"
    result = subprocess.run(
        [sys.executable, str(script)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "slow-script timed out after 0.05s" in result.stderr


def test_arm_cli_timeout_uses_alarm_without_setitimer(monkeypatch) -> None:
    alarms: list[int] = []
    monkeypatch.delattr(script_timeout.signal, "setitimer", raising=False)
    monkeypatch.setattr(script_timeout.signal, "alarm", lambda seconds: alarms.append(seconds))
    monkeypatch.setattr(script_timeout.signal, "signal", lambda *_args: None)
    monkeypatch.setattr(script_timeout.signal, "getsignal", lambda _sig: signal.SIG_DFL)

    cancel = script_timeout.arm_cli_timeout(label="demo", default_seconds=0.05)
    cancel()

    assert alarms == [1, 0]
