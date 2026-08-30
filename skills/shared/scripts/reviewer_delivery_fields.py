"""Validation of identity and optional execution fields on a delivery attempt."""

from __future__ import annotations

import re
from typing import Any, Callable

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PARENT_RECEIPT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
PARTIAL_OUTPUT_SCHEMA_VERSION = "charness.reviewer_partial_output.v1"
_PARTIAL_OUTPUT_KINDS = frozenset({
    "backend-output",
    "backend-stdout",
    "backend-stderr",
    "runner-stdout",
    "runner-stderr",
    "worker-output",
})
BOUNDARY_MODES = frozenset({"read-only-worker", "shared-tree-fingerprint"})
DEFAULT_BOUNDARY_MODE = "read-only-worker"
FINGERPRINT_BOUNDARY_MODE = "shared-tree-fingerprint"


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _sha256(value: object, label: str) -> str:
    text = _text(value, label).lower()
    if not _SHA256_RE.fullmatch(text):
        raise ValueError(f"{label} must be a lowercase SHA-256 identity")
    return text


def partial_output(value: object) -> dict[str, Any]:
    """Validate the small, identity-bound descriptor for preserved output.

    Partial bytes are useful evidence, but they are never a review result.  The
    descriptor therefore binds the bytes and their kind without giving a
    consumer a second approval path.
    """
    if not isinstance(value, dict):
        raise ValueError("partial_output must be an object")
    expected = {"schema_version", "kind", "path", "bytes", "sha256"}
    unknown = sorted(set(value) - expected)
    if unknown:
        raise ValueError(f"partial_output has unknown fields: {', '.join(unknown)}")
    if value.get("schema_version") != PARTIAL_OUTPUT_SCHEMA_VERSION:
        raise ValueError(
            f"partial_output schema_version must be {PARTIAL_OUTPUT_SCHEMA_VERSION}"
        )
    kind = _text(value.get("kind"), "partial_output.kind")
    if kind not in _PARTIAL_OUTPUT_KINDS:
        raise ValueError(f"unknown partial_output.kind: {kind}")
    path = _text(value.get("path"), "partial_output.path")
    size = value.get("bytes")
    if type(size) is not int or size < 1:
        raise ValueError("partial_output.bytes must be a positive integer")
    return {
        "schema_version": PARTIAL_OUTPUT_SCHEMA_VERSION,
        "kind": kind,
        "path": path,
        "bytes": size,
        "sha256": _sha256(value.get("sha256"), "partial_output.sha256"),
    }


def parent_receipt_identity(value: object, label: str = "parent_receipt_identity") -> str:
    """Preserve the caller's receipt identity while enforcing one safe grammar.

    Receipt IDs are correlation keys, not hashes.  They therefore remain
    case-sensitive, but must be single-line path/transport-safe identifiers so
    the producer and every consumer can join the same value exactly.
    """

    text = _text(value, label)
    if not PARENT_RECEIPT_ID_RE.fullmatch(text):
        raise ValueError(
            f"{label} must be a non-empty single-line identifier containing only "
            "letters, digits, `.`, `_`, `:`, or `-`"
        )
    return text


def boundary_binding(
    mode_value: object | None, fingerprint_value: object | None
) -> tuple[str, str | None]:
    """Normalize the execution boundary without inventing a git snapshot.

    Older ledgers only carried ``boundary_fingerprint``. Preserve that shape by
    inferring the shared-tree mode when the field is present. New read-only
    workers carry an explicit mode and no fingerprint because their backend
    envelope already removes write and exec capability.
    """
    if mode_value is None:
        mode = FINGERPRINT_BOUNDARY_MODE if fingerprint_value is not None else DEFAULT_BOUNDARY_MODE
    else:
        mode = _text(mode_value, "boundary_mode")
    if mode not in BOUNDARY_MODES:
        raise ValueError(f"unknown boundary_mode: {mode}")
    fingerprint = (
        _text(fingerprint_value, "boundary_fingerprint")
        if fingerprint_value is not None
        else None
    )
    if mode == FINGERPRINT_BOUNDARY_MODE and fingerprint is None:
        raise ValueError("shared-tree-fingerprint requires boundary_fingerprint")
    if mode == DEFAULT_BOUNDARY_MODE and fingerprint is not None:
        raise ValueError("read-only-worker must not carry a boundary_fingerprint")
    return mode, fingerprint


def bound_fields(
    payload: dict[str, Any],
    state: str,
    *,
    findings_received: str,
    execution_modes: frozenset[str],
    attempt_id: Callable[[object | None], str],
    partial_state: str = "partial",
) -> dict[str, Any]:
    """Normalize optional fields and enforce state/identity invariants."""
    findings = (
        _sha256(payload["findings_identity"], "findings_identity")
        if payload.get("findings_identity") is not None
        else None
    )
    if state == findings_received and findings is None:
        raise ValueError("findings-received history requires findings_identity")
    if state != findings_received and findings is not None:
        raise ValueError("findings_identity is only valid for findings-received")
    partial = (
        partial_output(payload["partial_output"])
        if payload.get("partial_output") is not None
        else None
    )
    if state == partial_state and partial is None:
        raise ValueError("partial state requires partial_output")
    reviewed_input_identity = (
        _sha256(payload["reviewed_input_identity"], "reviewed_input_identity")
        if payload.get("reviewed_input_identity") is not None
        else None
    )
    execution_mode = payload.get("execution_mode")
    if execution_mode is not None:
        execution_mode = _text(execution_mode, "execution_mode")
        if execution_mode not in execution_modes:
            raise ValueError(f"unknown execution_mode: {execution_mode}")
    prompt_sha256 = (
        _sha256(payload["prompt_sha256"], "prompt_sha256")
        if payload.get("prompt_sha256") is not None
        else None
    )
    schema_sha256 = (
        _sha256(payload["schema_sha256"], "schema_sha256")
        if payload.get("schema_sha256") is not None
        else None
    )
    capability_launch_envelope_sha256 = (
        _sha256(
            payload["capability_launch_envelope_sha256"],
            "capability_launch_envelope_sha256",
        )
        if payload.get("capability_launch_envelope_sha256") is not None
        else None
    )
    boundary_mode, boundary_fingerprint = boundary_binding(
        payload.get("boundary_mode"), payload.get("boundary_fingerprint")
    )
    output_file = _text(payload["output_file"], "output_file") if payload.get("output_file") is not None else None
    receipt_file = _text(payload["receipt_file"], "receipt_file") if payload.get("receipt_file") is not None else None
    producer_run_id = _text(payload["producer_run_id"], "producer_run_id") if payload.get("producer_run_id") is not None else None
    retry_of = attempt_id(payload["retry_of"]) if payload.get("retry_of") is not None else None
    retry_count = payload.get("retry_count", 0)
    if not isinstance(retry_count, int) or retry_count < 0:
        raise ValueError("retry_count must be a non-negative integer")
    return {
        "findings_identity": findings,
        "partial_output": partial,
        "reviewed_input_identity": reviewed_input_identity,
        "execution_mode": execution_mode,
        "backend": _text(payload["backend"], "backend") if payload.get("backend") is not None else None,
        "prompt_sha256": prompt_sha256,
        "schema_sha256": schema_sha256,
        "capability_launch_envelope_sha256": capability_launch_envelope_sha256,
        "boundary_mode": boundary_mode,
        "boundary_fingerprint": boundary_fingerprint,
        "output_file": output_file,
        "receipt_file": receipt_file,
        "producer_run_id": producer_run_id,
        "retry_of": retry_of,
        "retry_count": retry_count,
    }
