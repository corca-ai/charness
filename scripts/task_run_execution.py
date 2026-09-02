"""Codex process control and result-delivery parsing."""

from __future__ import annotations

import json
import os
import shutil
import signal
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from scripts.subprocess_guard import render_display, run_monitored_phase

_DESCENDANT_CLEANUP_SHELL = (
    'printf "%s\\n" "$$" > "$1"; shift; exec 3<&0; "$@" <&3 & '
    'child=$!; wait "$child"; status=$?; exit "$status"'
)


def _command_with_normal_completion_cleanup(
    command: Sequence[str], configured_env: Mapping[str, str], group_path: Path
) -> Sequence[str]:
    """Keep the task runner's old whole-group cleanup after a clean child exit."""
    if not command:
        return command
    executable = os.fspath(command[0])
    if "/" in executable:
        available = os.access(executable, os.X_OK)
    else:
        available = (
            shutil.which(executable, path=configured_env.get("PATH", os.defpath)) is not None
        )
    if not available:
        # Keep the guard's FileNotFoundError path for a missing Codex executable.
        return command
    return [
        "sh",
        "-c",
        _DESCENDANT_CLEANUP_SHELL,
        "charness-task-run",
        str(group_path),
        *command,
    ]


def _kill_recorded_process_group(group_path: Path) -> None:
    try:
        group_id = int(group_path.read_text(encoding="ascii").strip())
    except (OSError, ValueError):
        return
    try:
        os.killpg(group_id, signal.SIGKILL)
    except ProcessLookupError:
        pass
    finally:
        group_path.unlink(missing_ok=True)


@contextmanager
def _redirect_stdio(stdin_handle, stdout_handle, stderr_handle):  # noqa: ANN001
    saved = [os.dup(fd) for fd in (0, 1, 2)]
    try:
        for fd, handle in zip((0, 1, 2), (stdin_handle, stdout_handle, stderr_handle)):
            os.dup2(handle.fileno(), fd)
        yield
    finally:
        for fd, saved_fd in zip((0, 1, 2), saved):
            os.dup2(saved_fd, fd)
            os.close(saved_fd)


def _execute_codex(
    command: Sequence[str],
    *,
    prompt: str,
    target_path: Path,
    configured_env: Mapping[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    result: dict[str, Any] = {"exit_code": None, "timed_out": False, "interrupted": False}
    group_path = stdout_log.with_suffix(".pgid")
    group_path.unlink(missing_ok=True)

    try:
        with (
            stdout_log.open("w", encoding="utf-8") as stdout_handle,
            stderr_log.open("w", encoding="utf-8") as stderr_handle,
        ):
            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as prompt_handle:
                prompt_handle.write(prompt)
                prompt_handle.flush()
                prompt_handle.seek(0)
                terminal_stderr = os.fdopen(os.dup(2), "w", buffering=1, closefd=True)
                outcome = None
                try:
                    with _redirect_stdio(prompt_handle, stdout_handle, stderr_handle):
                        outcome = run_monitored_phase(
                            _command_with_normal_completion_cleanup(
                                command, configured_env, group_path
                            ),
                            cwd=target_path,
                            phase="codex",
                            timeout_seconds=timeout_seconds,
                            display=render_display(command),
                            env=dict(configured_env),
                            capture=False,
                            stream=terminal_stderr,
                        )
                except KeyboardInterrupt:
                    result["interrupted"] = True
                finally:
                    terminal_stderr.close()
                    _kill_recorded_process_group(group_path)
                if outcome is not None:
                    result["timed_out"] = outcome.timed_out
                    result["exit_code"] = None if outcome.timed_out else outcome.returncode
    except OSError as exc:
        result["exec_error"] = str(exc)
    return result


_MAX_RESULT_TEXT_BYTES = 1024 * 1024


def _result_delivery(stdout_log: Path) -> dict[str, Any]:
    raw = stdout_log.read_bytes() if stdout_log.is_file() else b""
    delivered = bool(raw.strip())
    clipped = raw[:_MAX_RESULT_TEXT_BYTES]
    text = clipped.decode("utf-8", errors="replace")
    result: dict[str, Any] = {
        "status": "delivered" if delivered else "non-delivery",
        "bytes": len(raw),
        "truncated": len(raw) > len(clipped),
        "text": text,
        "log": str(stdout_log),
    }
    result["structured_status"] = "not-applicable"
    if delivered and not result["truncated"]:
        try:
            structured = yaml.safe_load(text)
        except yaml.YAMLError:
            if "schema_version" in text:
                result["structured_status"] = "invalid"
        else:
            if isinstance(structured, Mapping) and "schema_version" in structured:
                try:
                    json.dumps(structured)
                except (TypeError, ValueError):
                    result["structured_status"] = "invalid"
                else:
                    result["structured_status"] = "valid"
                    result["structured"] = dict(structured)
    return result
