from __future__ import annotations

import os
import shlex
import sys
import tempfile
from pathlib import Path

from runtime_bootstrap import import_repo_module

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_monitored_phase = _subprocess_guard.run_monitored_phase
render_display = _subprocess_guard.render_display
heartbeat_interval_from_env = _subprocess_guard.heartbeat_interval_from_env

COMMAND_TIMEOUT_SECONDS = 1800
PROGRESS_INTERVAL_SECONDS = _subprocess_guard.DEFAULT_HEARTBEAT_SECONDS
PROGRESS_INTERVAL_ENV = "CHARNESS_CLOSEOUT_PROGRESS_INTERVAL_SECONDS"


def _progress_interval_seconds() -> float:
    return heartbeat_interval_from_env(PROGRESS_INTERVAL_ENV, PROGRESS_INTERVAL_SECONDS)


def run_command(repo_root: Path, command: str, phase: str) -> dict[str, object]:
    python_executable = shlex.quote(sys.executable)
    with tempfile.TemporaryDirectory(prefix="charness-closeout-bin-") as wrapper_dir:
        wrapper_path = Path(wrapper_dir)
        wrappers = {
            "python3": f"#!/usr/bin/env bash\nexec {python_executable} \"$@\"\n",
            "pytest": f"#!/usr/bin/env bash\nexec {python_executable} -m pytest \"$@\"\n",
        }
        for name, body in wrappers.items():
            script = wrapper_path / name
            script.write_text(body, encoding="utf-8")
            script.chmod(0o755)
        inherited_path = os.environ.get("PATH", "")
        path = f"{wrapper_path}:{inherited_path}" if inherited_path else str(wrapper_path)
        wrapped_command = f"export PATH={shlex.quote(path)}; {command}"
        outcome = run_monitored_phase(
            ["/bin/bash", "-lc", wrapped_command],
            cwd=repo_root,
            phase=phase,
            timeout_seconds=COMMAND_TIMEOUT_SECONDS,
            # The OPERATOR's command, not the PATH-wrapped one: the wrapper prefix is
            # this runner's implementation detail and would eat the whole display
            # budget before the command an operator is waiting on ever appears.
            display=render_display(command),
            heartbeat_seconds=_progress_interval_seconds(),
        )
    return {
        "phase": phase,
        "command": command,
        "returncode": outcome.returncode,
        "stdout": outcome.stdout,
        "stderr": outcome.stderr,
        "elapsed_seconds": outcome.elapsed_seconds,
    }
