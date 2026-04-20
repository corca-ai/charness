from __future__ import annotations

import os
import signal
import sys
from collections.abc import Callable

DEFAULT_SCRIPT_TIMEOUT_SECONDS = 10
TIMEOUT_ENV_VAR = "CHARNESS_SCRIPT_TIMEOUT_SECONDS"


def resolve_timeout_seconds(
    *,
    default_seconds: int = DEFAULT_SCRIPT_TIMEOUT_SECONDS,
    env_var: str = TIMEOUT_ENV_VAR,
) -> int:
    raw = os.environ.get(env_var)
    if raw is None or raw == "":
        return default_seconds
    try:
        seconds = int(raw)
    except ValueError:
        return default_seconds
    return max(seconds, 0)


def arm_cli_timeout(
    *,
    label: str,
    default_seconds: int = DEFAULT_SCRIPT_TIMEOUT_SECONDS,
    env_var: str = TIMEOUT_ENV_VAR,
) -> Callable[[], None]:
    seconds = resolve_timeout_seconds(default_seconds=default_seconds, env_var=env_var)
    if seconds == 0 or sys.platform == "win32" or not hasattr(signal, "SIGALRM"):
        return lambda: None

    previous_handler = signal.getsignal(signal.SIGALRM)

    def _on_timeout(_signum: int, _frame: object) -> None:
        raise SystemExit(f"{label} timed out after {seconds}s")

    signal.signal(signal.SIGALRM, _on_timeout)
    signal.alarm(seconds)

    def _cancel() -> None:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)

    return _cancel
