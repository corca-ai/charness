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
        # A plain ``process.kill`` only reaches the direct child on Windows.
        # Use the platform process-tree primitive when available so a timed-out
        # or interrupted host cannot leave its backend descendants running.
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            process.kill()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
