from __future__ import annotations

import shlex
import subprocess
from collections.abc import Sequence
from pathlib import Path

TIMEOUT_EXIT_CODE = 124
DEFAULT_COMMAND_TIMEOUT_SECONDS = 30


def _coerce_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def timeout_message(command: Sequence[str] | str, *, timeout_seconds: float) -> str:
    rendered = command if isinstance(command, str) else shlex.join(command)
    seconds_text = f"{timeout_seconds:g}"
    return f"timed out after {seconds_text}s while running `{rendered}`"


def run_process(
    command: Sequence[str] | str,
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_seconds: float = DEFAULT_COMMAND_TIMEOUT_SECONDS,
    shell: bool = False,
    executable: str | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout_seconds,
            shell=shell,
            executable=executable,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            command,
            TIMEOUT_EXIT_CODE,
            _coerce_text(exc.stdout),
            timeout_message(command, timeout_seconds=timeout_seconds),
        )
