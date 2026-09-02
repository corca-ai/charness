"""Explicit in-process runner for generated parser fixtures.

The documented-subcommand tests create tiny Python CLIs whose only observable
contract is argparse's help payload.  Running each fixture as a child repeats
the same interpreter/bootstrap cost without proving a process boundary.  This
runner keeps non-Python commands on the real subprocess path and is injected
only by those tests; production ``HelpProbe`` callers retain their default.
"""

from __future__ import annotations

import contextlib
import io
import os
import runpy
import subprocess
import sys
import traceback
from collections.abc import Sequence
from pathlib import Path

from scripts.core.subprocess_guard import run_process


def _python_script(command: Sequence[str], cwd: Path) -> Path | None:
    if len(command) < 2 or Path(command[0]).name not in {
        "python",
        "python3",
        Path(sys.executable).name,
    }:
        return None
    script = Path(command[1])
    if script.is_absolute():
        return script if script.is_file() else None
    script = cwd / script
    return script if script.is_file() else None


def _run_python_script(
    command: Sequence[str],
    *,
    script: Path,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    output, errors = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    saved_env = os.environ.copy()
    previous_cwd = Path.cwd()
    returncode = 0
    try:
        sys.argv = [str(script), *command[2:]]
        os.environ.clear()
        os.environ.update(env)
        os.chdir(cwd)
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            try:
                runpy.run_path(str(script), run_name="__main__")
            except SystemExit as exc:
                if isinstance(exc.code, int):
                    returncode = exc.code
                elif exc.code is not None:
                    returncode = 1
                    print(str(exc.code), file=errors)
            except Exception:
                returncode = 1
                traceback.print_exc(file=errors)
    finally:
        os.chdir(previous_cwd)
        sys.argv = saved_argv
        os.environ.clear()
        os.environ.update(saved_env)
    return subprocess.CompletedProcess(command, returncode, output.getvalue(), errors.getvalue())


def run_help_commands_in_process(
    commands: Sequence[Sequence[str]],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: float,
) -> list[subprocess.CompletedProcess[str]]:
    """Run generated Python parser fixtures in-process, with explicit fallback."""
    results = []
    for command in commands:
        script = _python_script(command, cwd)
        if script is None:
            results.append(
                run_process(
                    command,
                    cwd=cwd,
                    env=env,
                    timeout_seconds=timeout_seconds,
                )
            )
        else:
            results.append(_run_python_script(command, script=script, cwd=cwd, env=env))
    return results
