"""Codex process control and result-delivery parsing."""

from __future__ import annotations

import json
import os
import signal
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


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

    # Takes the process rather than closing over an Optional one. Every call site is
    # inside the `with` block, after Popen has returned; a Popen that raises goes to
    # the outer OSError handler and never reaches here. The former `if process is
    # None: return` guard was therefore unreachable -- it existed to narrow the type
    # of a variable that only needed to be Optional because of the closure.
    def stop_process_group(process: subprocess.Popen[str]) -> None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    try:
        with (
            stdout_log.open("w", encoding="utf-8") as stdout_handle,
            stderr_log.open("w", encoding="utf-8") as stderr_handle,
        ):
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                cwd=target_path,
                env=dict(configured_env),
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                start_new_session=True,
            )
            try:
                process.communicate(input=prompt, timeout=timeout_seconds)
                result["exit_code"] = process.returncode
            except subprocess.TimeoutExpired:
                result["timed_out"] = True
                stop_process_group(process)
                process.communicate()
            except KeyboardInterrupt:
                result["interrupted"] = True
                stop_process_group(process)
                process.communicate()
            else:
                stop_process_group(process)
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
