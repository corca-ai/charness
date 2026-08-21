#!/usr/bin/env python3
"""Portable process and result runtime for :mod:`reviewer_worker`.

The CLI module owns argument parsing and terminal receipt emission. This module
owns the backend boundary: path preflight, process-group cleanup, schema
validation, and atomic result publication.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from reviewer_process import terminate_process_group
except ImportError:
    from skills.shared.scripts.reviewer_process import terminate_process_group

SCHEMA_VERSION = "charness.reviewer_worker.v1"
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
    }
)


class WorkerError(ValueError):
    """A typed, terminal worker failure that the CLI can serialize."""

    def __init__(self, status: str, message: str, *, exit_code: int | None = None) -> None:
        if status not in STATUSES or status == SUCCESS:
            raise ValueError(f"invalid worker failure status: {status}")
        super().__init__(message)
        self.status = status
        self.exit_code = exit_code


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve(path_value: str, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value.strip():
        raise WorkerError("input-invalid", f"{label} must be a non-empty path")
    return Path(path_value).expanduser().resolve()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
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


def _schema_validator(schema_path: Path) -> tuple[Any, dict[str, Any]]:
    try:
        import jsonschema
    except ImportError as exc:
        raise WorkerError("schema-validator-unavailable", "jsonschema is not installed") from exc
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkerError("invalid-schema", f"cannot read JSON schema: {exc}") from exc
    try:
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        return validator_class(schema), schema
    except Exception as exc:
        raise WorkerError("invalid-schema", f"invalid JSON schema: {exc}") from exc


def _validate_result(path: Path, validator: Any) -> dict[str, Any]:
    if not path.exists():
        raise WorkerError("result-missing", f"backend did not write a result: {path}")
    if path.stat().st_size == 0:
        raise WorkerError("result-empty", f"backend wrote an empty result: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkerError("result-invalid-json", f"backend result is not valid JSON: {exc}") from exc
    try:
        validator.validate(payload)
    except Exception as exc:
        raise WorkerError("schema-invalid", f"backend result failed JSON Schema validation: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkerError("schema-invalid", "review result must be a JSON object")
    return payload


def preflight(args: Any) -> dict[str, Path | float | str]:
    workspace = resolve(args.workspace, "workspace")
    prompt = resolve(args.prompt_file, "prompt_file")
    schema = resolve(args.schema_file, "schema_file")
    output = resolve(args.output_file, "output_file")
    receipt = resolve(args.receipt_file, "receipt_file")
    stdout = resolve(args.stdout_file or f"{output}.stdout", "stdout_file")
    stderr = resolve(args.stderr_file or f"{output}.stderr", "stderr_file")
    if not workspace.is_dir():
        raise WorkerError("input-invalid", f"workspace is not a directory: {workspace}")
    for path, label in ((prompt, "prompt_file"), (schema, "schema_file")):
        if not path.is_file():
            raise WorkerError("input-invalid", f"{label} is not a file: {path}")
    if not isinstance(args.timeout_seconds, (int, float)) or not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= 0:
        raise WorkerError("input-invalid", "timeout_seconds must be finite and greater than zero")
    artifact_paths = (output, receipt, stdout, stderr)
    if len({str(path) for path in artifact_paths}) != len(artifact_paths):
        raise WorkerError("input-invalid", "worker artifact paths must resolve to distinct files")
    existing = [path for path in artifact_paths if path.exists()]
    if existing:
        rendered = ", ".join(str(path) for path in existing)
        raise WorkerError("stale-artifact-refused", f"refusing pre-existing worker artifact(s): {rendered}")
    return {
        "workspace": workspace,
        "prompt": prompt,
        "schema": schema,
        "output": output,
        "receipt": receipt,
        "stdout": stdout,
        "stderr": stderr,
        "timeout_seconds": float(args.timeout_seconds),
    }


def _command(backend: str, workspace: Path, schema: Path, pending_output: Path) -> list[str]:
    if backend == "codex_exec":
        return [
            "codex", "exec", "-C", str(workspace), "--sandbox", "read-only", "--ephemeral",
            "--output-schema", str(schema), "-o", str(pending_output), "-",
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


def run(args: Any, paths: dict[str, Path | float | str], run_id: str, started_at: str) -> dict[str, Any]:
    workspace = paths["workspace"]
    prompt = paths["prompt"]
    schema = paths["schema"]
    output = paths["output"]
    stdout = paths["stdout"]
    stderr = paths["stderr"]
    assert isinstance(workspace, Path)
    assert isinstance(prompt, Path)
    assert isinstance(schema, Path)
    assert isinstance(output, Path)
    assert isinstance(stdout, Path)
    assert isinstance(stderr, Path)
    validator, _ = _schema_validator(schema)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.{run_id}.", suffix=".pending", dir=output.parent)
    os.close(temp_fd)
    temp_output = Path(temp_name)
    temp_output.unlink()
    raw_output = temp_output.with_suffix(".raw.pending")
    exit_code: int | None = None
    status = SUCCESS
    error: str | None = None
    process: subprocess.Popen[Any] | None = None
    try:
        command = _command(args.backend, workspace, schema, temp_output)
        raw_handle = None
        with prompt.open("rb") as prompt_handle, stdout.open("wb") as stdout_handle, stderr.open("wb") as stderr_handle:
            try:
                if args.backend == "claude_p":
                    raw_handle = raw_output.open("wb")
                process = subprocess.Popen(
                    command,
                    cwd=workspace,
                    stdin=prompt_handle,
                    stdout=stdout_handle if args.backend == "codex_exec" else raw_handle,
                    stderr=stderr_handle,
                    start_new_session=(os.name == "posix"),
                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0,
                )
                try:
                    exit_code = process.wait(timeout=float(paths["timeout_seconds"]))
                except subprocess.TimeoutExpired as exc:
                    terminate_process_group(process)
                    exit_code = 124
                    raise WorkerError("timed-out", f"backend exceeded {paths['timeout_seconds']} seconds") from exc
            except FileNotFoundError as exc:
                raise WorkerError("backend-unavailable", f"backend executable unavailable: {exc}") from exc
            finally:
                if raw_handle is not None:
                    raw_handle.close()
        if exit_code != 0:
            raise WorkerError("backend-failed", f"backend exited with code {exit_code}", exit_code=exit_code)
        if args.backend == "claude_p":
            _normalize_claude(raw_output, temp_output)
        _validate_result(temp_output, validator)
        os.replace(temp_output, output)
    except WorkerError as exc:
        status = exc.status
        error = str(exc)
        if exc.exit_code is not None:
            exit_code = exc.exit_code
    finally:
        if process is not None and process.poll() is None:
            terminate_process_group(process)
        for path in (temp_output, raw_output):
            try:
                path.unlink()
            except OSError:
                pass
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "backend": args.backend,
        "workspace": str(workspace),
        "prompt_file": str(prompt),
        "schema_file": str(schema),
        "output_file": str(output),
        "stdout_file": str(stdout),
        "stderr_file": str(stderr),
        "started_at": started_at,
        "finished_at": now(),
        "timeout_seconds": float(paths["timeout_seconds"]),
        "status": status,
        "terminal": True,
        "exit_code": exit_code,
        "output_fresh": status == SUCCESS and output.exists(),
        "attempt_id": args.attempt_id,
        "scope": args.scope,
        "packet_identity": args.packet_identity,
        "reviewed_input_identity": args.reviewed_input_identity,
        "execution_mode": args.execution_mode,
        "prompt_sha256": sha256(prompt),
        "schema_sha256": sha256(schema),
    }
    if output.exists():
        receipt["output_size"] = output.stat().st_size
        receipt["output_sha256"] = sha256(output)
    if error:
        receipt["error"] = error
    return receipt
