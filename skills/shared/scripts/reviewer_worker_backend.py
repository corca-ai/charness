#!/usr/bin/env python3
"""Backend command, process, and raw-result normalization for the reviewer worker."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

try:
    from reviewer_process import ReviewerProcessError, run_bounded_process
except ImportError:
    from skills.shared.scripts.reviewer_process import ReviewerProcessError, run_bounded_process

SUCCESS = "succeeded"
STATUSES = frozenset(
    {
        SUCCESS,
        "input-invalid",
        "stale-artifact-refused",
        "backend-unavailable",
        "backend-failed",
        "timed-out",
        "result-missing",
        "result-empty",
        "result-invalid-json",
        "invalid-schema",
        "schema-validator-unavailable",
        "schema-invalid",
        "interrupted",
        "transport-unestablished",
        "credential-invalid",
        "authorization-insufficient",
        "provider-unavailable",
        "probe-invalid",
    }
)


class WorkerError(ValueError):
    """A typed, terminal worker failure that the CLI can serialize."""

    def __init__(
        self,
        status: str,
        message: str,
        *,
        exit_code: int | None = None,
        capability: dict[str, Any] | None = None,
    ) -> None:
        if status not in STATUSES or status == SUCCESS:
            raise ValueError(f"invalid worker failure status: {status}")
        super().__init__(message)
        self.status = status
        self.exit_code = exit_code
        self.capability = capability


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write one JSON object without exposing a partial artifact to readers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _command(backend: str, workspace: Path, schema: Path, raw_output: Path) -> list[str]:
    if backend == "codex_exec":
        return [
            "codex", "exec", "-C", str(workspace), "--sandbox", "read-only", "--ephemeral",
            "--output-schema", str(schema), "-o", str(raw_output), "-",
        ]
    if backend == "claude_p":
        try:
            schema_payload = json.loads(schema.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkerError("invalid-schema", f"cannot load Claude JSON schema: {exc}") from exc
        return [
            "claude", "-p", "--no-session-persistence", "--tools", "", "--output-format", "json",
            "--json-schema", json.dumps(schema_payload, ensure_ascii=False, separators=(",", ":")),
        ]
    raise WorkerError("input-invalid", f"unsupported backend: {backend}")


def _normalize_codex(raw_path: Path, pending_output: Path) -> None:
    """Promote Codex's already-structured file through the same boundary."""
    if raw_path.exists():
        os.replace(raw_path, pending_output)


def _normalize_claude(raw_path: Path, pending_output: Path) -> None:
    try:
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkerError("result-invalid-json", f"Claude wrapper result is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkerError("result-invalid-json", "Claude wrapper result must be a JSON object")
    if payload.get("is_error"):
        raise WorkerError("backend-failed", str(payload.get("result") or "claude reported is_error"))
    structured = payload.get("structured_output")
    atomic_write_json(pending_output, structured if isinstance(structured, dict) else payload)


def _normalize(backend: str, raw_output: Path, pending_output: Path) -> None:
    if backend == "codex_exec":
        _normalize_codex(raw_output, pending_output)
    elif backend == "claude_p":
        _normalize_claude(raw_output, pending_output)
    else:
        raise WorkerError("input-invalid", f"unsupported backend: {backend}")


def execute_backend(
    backend: str,
    *,
    workspace: Path,
    prompt: Path,
    schema: Path,
    stdout: Path,
    stderr: Path,
    pending_output: Path,
    raw_output: Path,
    timeout_seconds: float,
) -> int:
    """Invoke one backend, map process failures, and normalize its output."""
    try:
        exit_code = run_bounded_process(
            _command(backend, workspace, schema, raw_output),
            cwd=workspace,
            stdin_path=prompt,
            stdout_path=stdout if backend == "codex_exec" else raw_output,
            stderr_path=stderr,
            timeout_seconds=timeout_seconds,
        )
    except ReviewerProcessError as exc:
        raise WorkerError(exc.status, str(exc), exit_code=exc.exit_code) from exc
    if exit_code != 0:
        raise WorkerError("backend-failed", f"backend exited with code {exit_code}", exit_code=exit_code)
    _normalize(backend, raw_output, pending_output)
    return exit_code
