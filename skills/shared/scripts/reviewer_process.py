#!/usr/bin/env python3
"""Process-group lifecycle primitives for bounded reviewer workers."""

from __future__ import annotations

import os
import signal
import subprocess
from typing import Any


def terminate_process_group(process: subprocess.Popen[Any]) -> None:
    """Hard-stop a backend and descendants when a bounded run expires."""
    if os.name == "posix":
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()
    process.wait()
