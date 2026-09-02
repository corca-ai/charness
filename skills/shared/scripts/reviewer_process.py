#!/usr/bin/env python3
"""Process-group lifecycle primitives for bounded reviewer workers."""

from __future__ import annotations

import shlex
import shutil
import signal
import sys
from pathlib import Path

try:
    from scripts.subprocess_guard import run_monitored_phase
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from subprocess_guard import run_monitored_phase


class ReviewerProcessError(ValueError):
    """Typed backend launch/timeout failure for the worker receipt adapter."""

    def __init__(self, status: str, message: str, *, exit_code: int | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.exit_code = exit_code


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
    if not command or (not Path(command[0]).is_file() and shutil.which(command[0]) is None):
        executable = command[0] if command else "<empty command>"
        raise ReviewerProcessError(
            "backend-unavailable", f"backend executable unavailable: {executable}"
        )

    # The guard owns the process group and timeout lifecycle. Shell redirection
    # supplies the same file-backed stdin contract that the old Popen call had;
    # shlex keeps every adapter-provided argument one shell word.
    command_line = f"exec {shlex.join(command)} < {shlex.quote(str(stdin_path))}"
    previous: dict[int, object] = {}

    def interrupt(_signum: int, _frame: object) -> None:
        raise KeyboardInterrupt

    try:
        for signum in (signal.SIGTERM, signal.SIGINT):
            try:
                previous[signum] = signal.signal(signum, interrupt)
            except (ValueError, OSError):
                continue
        outcome = run_monitored_phase(
            command_line,
            cwd=cwd,
            phase="reviewer-backend",
            timeout_seconds=timeout_seconds,
            shell=True,
        )
    except KeyboardInterrupt as exc:
        raise ReviewerProcessError(
            "interrupted",
            "backend interrupted; process group terminated",
            exit_code=130,
        ) from exc
    except FileNotFoundError as exc:
        raise ReviewerProcessError(
            "backend-unavailable", f"backend executable unavailable: {exc}"
        ) from exc
    finally:
        for signum, handler in previous.items():
            try:
                signal.signal(signum, handler)
            except (ValueError, OSError):
                pass

    stdout_path.write_text(outcome.stdout, encoding="utf-8")
    stderr_path.write_text(outcome.stderr, encoding="utf-8")
    if outcome.timed_out:
        raise ReviewerProcessError(
            "timed-out",
            f"backend exceeded {timeout_seconds} seconds",
            exit_code=124,
        )
    return outcome.returncode
