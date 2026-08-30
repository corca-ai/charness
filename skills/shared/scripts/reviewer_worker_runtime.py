#!/usr/bin/env python3
"""Portable lifecycle, validation, and receipt runtime for reviewer_worker.

The CLI module owns argument parsing and terminal receipt emission. Backend
command construction, process execution, and raw-output normalization live in
reviewer_worker_backend.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from reviewer_result_contract import write_model_authored_schema
    from reviewer_worker_backend import (
        SUCCESS,
        WorkerError,
        execute_backend,
    )
    from reviewer_worker_capability import (
        CapabilityLifecycleError,
        WorkerCapability,
        adapt_failure,
        collect,
        join_result_non_claims,
        launch,
        receipt_fields,
        validate_result_non_claims,
    )
except ImportError:
    from skills.shared.scripts.reviewer_result_contract import write_model_authored_schema
    from skills.shared.scripts.reviewer_worker_backend import (
        SUCCESS,
        WorkerError,
        execute_backend,
    )
    from skills.shared.scripts.reviewer_worker_capability import (
        CapabilityLifecycleError,
        WorkerCapability,
        adapt_failure,
        collect,
        join_result_non_claims,
        launch,
        receipt_fields,
        validate_result_non_claims,
    )

SCHEMA_VERSION = "charness.reviewer_worker.v1"


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


def _validate_result(
    path: Path,
    validator: Any,
    *,
    packet_identity: str,
    reviewed_input_identity: str,
    join: Any,
) -> dict[str, Any]:
    if not path.exists():
        raise WorkerError("result-missing", f"backend did not write a result: {path}")
    if path.stat().st_size == 0:
        raise WorkerError("result-empty", f"backend wrote an empty result: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkerError("result-invalid-json", f"backend result is not valid JSON: {exc}") from exc
    # The object check precedes both the join and schema validation: `join` reads
    # the payload as a mapping, and a bare list here would raise TypeError inside
    # the joiner instead of this module's typed refusal.
    if not isinstance(payload, dict):
        raise WorkerError("schema-invalid", "review result must be a JSON object")
    # Runner-owned provenance lands BEFORE schema validation because the canonical
    # schema requires those fields; validating first would fail every model-authored
    # result on the very fields the model must not author.
    payload = join(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        validator.validate(payload)
    except Exception as exc:
        raise WorkerError("schema-invalid", f"backend result failed JSON Schema validation: {exc}") from exc
    if payload.get("packet_sha256") != packet_identity:
        raise WorkerError(
            "schema-invalid",
            "review result packet_sha256 does not match the invocation packet identity",
        )
    if payload.get("reviewed_input_identity_sha256") != reviewed_input_identity:
        raise WorkerError(
            "schema-invalid",
            "review result reviewed_input_identity_sha256 does not match the invocation input identity",
        )
    return payload


def preflight(args: Any) -> dict[str, Any]:
    workspace = resolve(args.workspace, "workspace")
    prompt = resolve(args.prompt_file, "prompt_file")
    schema = resolve(args.schema_file, "schema_file")
    output = resolve(args.output_file, "output_file")
    receipt = resolve(args.receipt_file, "receipt_file")
    stdout = resolve(args.stdout_file or f"{output}.stdout", "stdout_file")
    stderr = resolve(args.stderr_file or f"{output}.stderr", "stderr_file")
    capability_file = resolve(args.capability_file, "capability_file")
    if not workspace.is_dir():
        raise WorkerError("input-invalid", f"workspace is not a directory: {workspace}")
    for path, label in (
        (prompt, "prompt_file"),
        (schema, "schema_file"),
        (capability_file, "capability_file"),
    ):
        if not path.is_file():
            raise WorkerError("input-invalid", f"{label} is not a file: {path}")
    if not isinstance(args.timeout_seconds, (int, float)) or not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= 0:
        raise WorkerError("input-invalid", "timeout_seconds must be finite and greater than zero")
    all_paths = (prompt, schema, capability_file, output, receipt, stdout, stderr)
    if len({str(path) for path in all_paths}) != len(all_paths):
        raise WorkerError("input-invalid", "worker input and artifact paths must resolve to distinct files")
    artifact_paths = (output, receipt, stdout, stderr)
    existing = [path for path in artifact_paths if path.exists()]
    if existing:
        rendered = ", ".join(str(path) for path in existing)
        raise WorkerError("stale-artifact-refused", f"refusing pre-existing worker artifact(s): {rendered}")
    try:
        capability = launch(capability_file, attempt_id=args.attempt_id)
    except CapabilityLifecycleError as exc:
        raise WorkerError(exc.status, str(exc), capability=exc.payload) from exc
    return {
        "workspace": workspace,
        "prompt": prompt,
        "schema": schema,
        "output": output,
        "receipt": receipt,
        "stdout": stdout,
        "stderr": stderr,
        "capability_file": capability_file,
        "capability": capability,
        "timeout_seconds": float(args.timeout_seconds),
    }


def run(args: Any, paths: dict[str, Any], run_id: str, started_at: str) -> dict[str, Any]:
    workspace = paths["workspace"]
    prompt = paths["prompt"]
    schema = paths["schema"]
    output = paths["output"]
    stdout = paths["stdout"]
    stderr = paths["stderr"]
    capability_file = paths["capability_file"]
    capability: WorkerCapability = paths["capability"]
    validator, canonical_schema = _schema_validator(schema)
    for path in (output, stdout, stderr):
        path.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.{run_id}.", suffix=".pending", dir=output.parent)
    os.close(temp_fd)
    temp_output = Path(temp_name)
    temp_output.unlink()
    raw_output = temp_output.with_suffix(".raw.pending")
    # #755: the backend generates against the model-authored projection.
    pending_schema = temp_output.with_suffix(".model-schema.pending")
    model_schema = write_model_authored_schema(canonical_schema, pending_schema)
    exit_code: int | None = None
    status = SUCCESS
    error: str | None = None
    try:
        exit_code = execute_backend(
            args.backend,
            workspace=workspace,
            prompt=prompt,
            schema=model_schema,
            stdout=stdout,
            stderr=stderr,
            pending_output=temp_output,
            raw_output=raw_output,
            timeout_seconds=float(paths["timeout_seconds"]),
        )
        capability = collect(capability, capability_file, attempt_id=args.attempt_id)
        result = _validate_result(
            temp_output,
            validator,
            packet_identity=args.packet_identity,
            reviewed_input_identity=args.reviewed_input_identity,
            join=lambda payload: join_result_non_claims(payload, capability),
        )
        # Retained as the invariant, not as the thing that catches model error: after
        # the join this can only fail if the joiner and the validator disagree about
        # the envelope, which is a Charness defect rather than a reviewer one.
        validate_result_non_claims(result, capability)
        os.replace(temp_output, output)
    except CapabilityLifecycleError as exc:
        if exc.adapt_capability:
            capability = adapt_failure(capability, exc)
        status = exc.status
        error = str(exc)
    except WorkerError as exc:
        status = exc.status
        error = str(exc)
        if exc.exit_code is not None:
            exit_code = exc.exit_code
    finally:
        for path in (temp_output, raw_output, model_schema):
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
        "capability_file": str(capability_file),
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
        "parent_receipt_identity": args.parent_receipt_identity,
        "boundary_mode": args.boundary_mode,
        "boundary_fingerprint": args.boundary_fingerprint,
        "execution_mode": args.execution_mode,
        "prompt_sha256": sha256(prompt),
        "schema_sha256": sha256(schema),
        # An auditor reading the result cannot otherwise tell that these two fields
        # were joined by the runner rather than authored by the reviewer.
        "capability_non_claims_provenance": "runner-joined-from-launch-envelope",
        **receipt_fields(capability),
    }
    if output.exists():
        receipt["output_size"] = output.stat().st_size
        receipt["output_sha256"] = sha256(output)
    if error:
        receipt["error"] = error
    return receipt
