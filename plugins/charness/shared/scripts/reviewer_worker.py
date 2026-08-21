#!/usr/bin/env python3
"""Run a bounded review backend and publish only a fresh, schema-valid result.

This is a backend-neutral Charness worker. It intentionally knows only the
portable CLI shapes declared here; host-specific adapters may choose which
backend to invoke, but they do not get to weaken the artifact and receipt
contract.

The worker refuses a pre-existing output/receipt/stdout/stderr path, resolves
every path before changing cwd, uses a finite Python subprocess timeout, and
publishes the result only after JSON Schema validation. A non-zero process,
timeout, empty output, stale artifact, invalid JSON, or schema failure receives
a typed receipt and never looks like success because a file happens to exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from reviewer_output import emit_yaml
except ImportError:
    from skills.shared.scripts.reviewer_output import emit_yaml

try:
    from reviewer_process import terminate_process_group
except ImportError:
    from skills.shared.scripts.reviewer_process import terminate_process_group

SCHEMA_VERSION = "charness.reviewer_worker.v1"
DEFAULT_TIMEOUT_SECONDS = 900.0
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
    }
)


class WorkerError(ValueError):
    def __init__(self, status: str, message: str, *, exit_code: int | None = None) -> None:
        if status not in STATUSES or status == SUCCESS:
            raise ValueError(f"invalid worker failure status: {status}")
        super().__init__(message)
        self.status = status
        self.exit_code = exit_code


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve(path_value: str, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value.strip():
        raise WorkerError("input-invalid", f"{label} must be a non-empty path")
    return Path(path_value).expanduser().resolve()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
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


def _schema_validator(schema_path: Path):
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


def _preflight(args: argparse.Namespace) -> dict[str, Path | float | str]:
    workspace = _resolve(args.workspace, "workspace")
    prompt = _resolve(args.prompt_file, "prompt_file")
    schema = _resolve(args.schema_file, "schema_file")
    output = _resolve(args.output_file, "output_file")
    receipt = _resolve(args.receipt_file, "receipt_file")
    stdout = _resolve(args.stdout_file or f"{output}.stdout", "stdout_file")
    stderr = _resolve(args.stderr_file or f"{output}.stderr", "stderr_file")
    if not workspace.is_dir():
        raise WorkerError("input-invalid", f"workspace is not a directory: {workspace}")
    for path, label in ((prompt, "prompt_file"), (schema, "schema_file")):
        if not path.is_file():
            raise WorkerError("input-invalid", f"{label} is not a file: {path}")
    if not isinstance(args.timeout_seconds, (int, float)) or not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= 0:
        raise WorkerError("input-invalid", "timeout_seconds must be finite and greater than zero")
    existing = [path for path in (output, receipt, stdout, stderr) if path.exists()]
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


def _command(backend: str, workspace: Path, prompt: Path, schema: Path, pending_output: Path) -> list[str]:
    if backend == "codex_exec":
        return [
            "codex",
            "exec",
            "-C",
            str(workspace),
            "--sandbox",
            "read-only",
            "--ephemeral",
            "--output-schema",
            str(schema),
            "-o",
            str(pending_output),
            "-",
        ]
    if backend == "claude_p":
        try:
            schema_payload = json.loads(schema.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkerError("invalid-schema", f"cannot load Claude JSON schema: {exc}") from exc
        return [
            "claude",
            "-p",
            "--no-session-persistence",
            "--tools",
            "",
            "--output-format",
            "json",
            "--json-schema",
            json.dumps(schema_payload, ensure_ascii=False, separators=(",", ":")),
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
    normalized = structured if isinstance(structured, dict) else payload
    _atomic_write_json(pending_output, normalized)


def _run(args: argparse.Namespace, paths: dict[str, Path | float | str], run_id: str, started_at: str) -> dict[str, Any]:
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
    try:
        command = _command(args.backend, workspace, prompt, schema, temp_output)
        raw_handle = None
        process: subprocess.Popen[Any] | None = None
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
        for path in (temp_output, raw_output):
            try:
                path.unlink()
            except OSError:
                pass
    finished_at = _now()
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
        "finished_at": finished_at,
        "timeout_seconds": float(paths["timeout_seconds"]),
        "status": status,
        "terminal": True,
        "exit_code": exit_code,
        "output_fresh": status == SUCCESS and output.exists(),
    }
    if output.exists():
        receipt["output_size"] = output.stat().st_size
        receipt["output_sha256"] = _sha256(output)
    if error:
        receipt["error"] = error
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded typed review worker.")
    parser.add_argument("--backend", choices=("codex_exec", "claude_p"), required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--schema-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--receipt-file", required=True)
    parser.add_argument("--stdout-file")
    parser.add_argument("--stderr-file")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--run-id", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    run_id = args.run_id or uuid.uuid4().hex
    started_at = _now()
    receipt_path: Path | None = None
    try:
        receipt_path = _resolve(args.receipt_file, "receipt_file")
        paths = _preflight(args)
        receipt = _run(args, paths, run_id, started_at)
    except WorkerError as exc:
        receipt = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "backend": args.backend,
            "started_at": started_at,
            "finished_at": _now(),
            "status": exc.status,
            "terminal": True,
            "exit_code": exc.exit_code,
            "output_fresh": False,
            "error": str(exc),
        }
    except Exception as exc:  # pragma: no cover - last-resort typed failure boundary
        receipt = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "backend": args.backend,
            "started_at": started_at,
            "finished_at": _now(),
            "status": "input-invalid",
            "terminal": True,
            "exit_code": None,
            "output_fresh": False,
            "error": f"unexpected worker error: {exc}",
        }
    if receipt_path is not None and not receipt_path.exists():
        _atomic_write_json(receipt_path, receipt)
    emit_yaml(receipt)
    return 0 if receipt.get("status") == SUCCESS else 1


if __name__ == "__main__":
    raise SystemExit(main())
