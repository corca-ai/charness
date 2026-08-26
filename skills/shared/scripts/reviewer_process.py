#!/usr/bin/env python3
"""Process-group lifecycle primitives for bounded reviewer workers."""

from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path
from typing import Any

PROCESS_CLEANUP_TIMEOUT_SECONDS = 5.0


class ReviewerProcessError(ValueError):
    """Typed backend launch/timeout failure for the worker receipt adapter."""

    def __init__(self, status: str, message: str, *, exit_code: int | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.exit_code = exit_code


def _install_interrupt_handlers(process: subprocess.Popen[Any]) -> dict[int, Any]:
    """Turn parent termination into backend-tree cleanup and a typed status."""
    previous: dict[int, Any] = {}

    def interrupt(signum: int, _frame: Any) -> None:
        terminate_process_group(process)
        raise ReviewerProcessError(
            "interrupted",
            f"backend interrupted by signal {signum}; process group terminated",
            exit_code=130,
        )

    for signum in (signal.SIGTERM, signal.SIGINT):
        try:
            previous[signum] = signal.signal(signum, interrupt)
        except (ValueError, OSError):
            # Python only permits signal installation in the main thread. The
            # worker still retains its normal timeout cleanup in other hosts.
            continue
    return previous


def _restore_interrupt_handlers(previous: dict[int, Any]) -> None:
    for signum, handler in previous.items():
        try:
            signal.signal(signum, handler)
        except (ValueError, OSError):
            pass


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


def run_bounded_process(
    command: list[str],
    *,
    cwd: Path,
    stdin_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    timeout_seconds: float,
) -> int:
    """Run one backend with file streams and bounded process-group cleanup."""
    process: subprocess.Popen[Any] | None = None
    previous_handlers: dict[int, Any] = {}
    try:
        with (
            stdin_path.open("rb") as stdin_handle,
            stdout_path.open("wb") as stdout_handle,
            stderr_path.open("wb") as stderr_handle,
        ):
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdin=stdin_handle,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=(os.name == "posix"),
                creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0,
            )
            previous_handlers = _install_interrupt_handlers(process)
            try:
                return process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired as exc:
                terminate_process_group(process)
                raise ReviewerProcessError(
                    "timed-out",
                    f"backend exceeded {timeout_seconds} seconds",
                    exit_code=124,
                ) from exc
    except FileNotFoundError as exc:
        raise ReviewerProcessError("backend-unavailable", f"backend executable unavailable: {exc}") from exc
    finally:
        _restore_interrupt_handlers(previous_handlers)
        if process is not None and process.poll() is None:
            terminate_process_group(process)
