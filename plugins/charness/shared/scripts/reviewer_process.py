#!/usr/bin/env python3
"""Process-group lifecycle primitives for bounded reviewer workers."""

from __future__ import annotations

import os
import signal
import subprocess
from typing import Any

PROCESS_CLEANUP_TIMEOUT_SECONDS = 5.0

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
                timeout=PROCESS_CLEANUP_TIMEOUT_SECONDS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            try:
                process.kill()
            except ProcessLookupError:
                pass
    try:
        process.wait(timeout=PROCESS_CLEANUP_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=PROCESS_CLEANUP_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            # The OS has not reaped the child yet. Do not turn cleanup into an
            # unbounded second timeout; the typed receipt still records the
            # original worker result and the caller can diagnose the orphan.
            pass
