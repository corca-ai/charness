from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

COMMAND_TIMEOUT_SECONDS = 1800
PROGRESS_INTERVAL_SECONDS = 30.0


def _progress_interval_seconds() -> float:
    raw = os.environ.get("CHARNESS_CLOSEOUT_PROGRESS_INTERVAL_SECONDS")
    if raw is None:
        return PROGRESS_INTERVAL_SECONDS
    try:
        return max(0.1, float(raw))
    except ValueError:
        return PROGRESS_INTERVAL_SECONDS


def _short_command(command: str, limit: int = 120) -> str:
    collapsed = " ".join(command.split())
    if len(collapsed) <= limit:
        return collapsed
    return f"{collapsed[: limit - 3]}..."


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
        display_command = _short_command(command)
        print(f"RUN [{phase}] {display_command}", file=sys.stderr, flush=True)
        started_at = time.monotonic()
        process = subprocess.Popen(
            ["/bin/bash", "-lc", wrapped_command],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        dot_count = 0
        while True:
            try:
                stdout, stderr = process.communicate(timeout=_progress_interval_seconds())
                result = subprocess.CompletedProcess(
                    ["/bin/bash", "-lc", wrapped_command],
                    process.returncode,
                    stdout or "",
                    stderr or "",
                )
                break
            except subprocess.TimeoutExpired:
                dot_count += 1
                print(".", end="", file=sys.stderr, flush=True)
                if dot_count % 80 == 0:
                    print("", file=sys.stderr, flush=True)
            if time.monotonic() - started_at > COMMAND_TIMEOUT_SECONDS:
                process.kill()
                stdout, stderr = process.communicate()
                stderr = f"{stderr or ''}\ntimed out after {COMMAND_TIMEOUT_SECONDS}s".strip()
                result = subprocess.CompletedProcess(
                    ["/bin/bash", "-lc", wrapped_command],
                    124,
                    stdout or "",
                    stderr,
                )
                break
        if dot_count:
            print("", file=sys.stderr, flush=True)
        elapsed = time.monotonic() - started_at
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"{status} [{phase}] {elapsed:.1f}s {display_command}", file=sys.stderr, flush=True)
    return {
        "phase": phase,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "elapsed_seconds": round(elapsed, 2),
    }
