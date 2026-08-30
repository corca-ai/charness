"""Validate a preserved reviewer-output carrier without treating it as delivery."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from typing import Any

try:
    from reviewer_delivery_fields import PARTIAL_OUTPUT_SCHEMA_VERSION, partial_output
except ImportError:
    fields_path = Path(__file__).with_name("reviewer_delivery_fields.py")
    fields_spec = importlib.util.spec_from_file_location(
        "charness_reviewer_delivery_fields", fields_path
    )
    if fields_spec is None or fields_spec.loader is None:
        raise RuntimeError(f"cannot load reviewer delivery fields: {fields_path}")
    fields = importlib.util.module_from_spec(fields_spec)
    fields_spec.loader.exec_module(fields)
    PARTIAL_OUTPUT_SCHEMA_VERSION = fields.PARTIAL_OUTPUT_SCHEMA_VERSION
    partial_output = fields.partial_output


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def descriptor(path: Path, *, kind: str = "backend-output") -> dict[str, Any]:
    """Describe existing bytes as diagnostic partial output."""
    return {
        "schema_version": PARTIAL_OUTPUT_SCHEMA_VERSION,
        "kind": kind,
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def collect_run_logs(root: Path, paths: dict[str, Path]) -> list[dict[str, Any]]:
    """Describe non-empty runner logs without treating them as delivery."""
    outputs: list[dict[str, Any]] = []
    for key, kind in (
        ("runner_stdout", "runner-stdout"),
        ("runner_stderr", "runner-stderr"),
        ("backend_stdout", "backend-stdout"),
        ("backend_stderr", "backend-stderr"),
    ):
        path = paths[key]
        if not path.is_file() or path.stat().st_size == 0:
            continue
        value = descriptor(path, kind=kind)
        value["path"] = path.resolve().relative_to(root.resolve()).as_posix()
        outputs.append(value)
    return outputs


def validate_receipt_output(
    receipt: dict[str, Any], *, attempt: Any
) -> tuple[dict[str, Any] | None, str]:
    """Validate the receipt descriptor and its binding to the producer output."""
    value = receipt.get("partial_output")
    if value is None:
        return None, "worker did not preserve partial output bytes"
    try:
        candidate = partial_output(value)
    except ValueError as exc:
        return None, str(exc)
    path = Path(candidate["path"]).expanduser().resolve()
    expected = (
        Path(f"{attempt.output_file}.partial").expanduser().resolve()
        if attempt.output_file is not None
        else None
    )
    if expected is None or path != expected:
        return None, "partial output path does not match the producer output binding"
    if not path.is_file():
        return None, "partial output file is missing"
    if path.stat().st_size != candidate["bytes"] or _sha256(path) != candidate["sha256"]:
        return None, "partial output bytes do not match the typed descriptor"
    return candidate, "typed partial output is preserved and identity-bound"
