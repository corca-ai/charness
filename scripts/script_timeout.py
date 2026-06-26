from __future__ import annotations

import math
import os
import signal
import sys
from collections.abc import Callable

DEFAULT_SCRIPT_TIMEOUT_SECONDS = 10
TIMEOUT_ENV_VAR = "CHARNESS_SCRIPT_TIMEOUT_SECONDS"


def resolve_timeout_seconds(
    *,
    default_seconds: float = DEFAULT_SCRIPT_TIMEOUT_SECONDS,
    env_var: str = TIMEOUT_ENV_VAR,
) -> float:
    raw = os.environ.get(env_var)
    if raw is None or raw == "":
        return default_seconds
    try:
        seconds = float(raw)
    except ValueError:
        return float(default_seconds)
    return max(seconds, 0.0)


def arm_cli_timeout(
    *,
    label: str,
    default_seconds: float = DEFAULT_SCRIPT_TIMEOUT_SECONDS,
    env_var: str = TIMEOUT_ENV_VAR,
) -> Callable[[], None]:
    seconds = resolve_timeout_seconds(default_seconds=default_seconds, env_var=env_var)
    if seconds <= 0 or sys.platform == "win32" or not hasattr(signal, "SIGALRM"):
        return lambda: None

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer: tuple[float, float] | None = None

    def _on_timeout(_signum: int, _frame: object) -> None:
        raise SystemExit(f"{label} timed out after {seconds:g}s")

    signal.signal(signal.SIGALRM, _on_timeout)
    if hasattr(signal, "setitimer"):
        previous_timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    else:
        signal.alarm(math.ceil(seconds))

    def _cancel() -> None:
        if previous_timer is not None:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        else:
            signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)

    return _cancel
