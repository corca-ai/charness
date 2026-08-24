"""Validation of identity and optional execution fields on a delivery attempt."""

from __future__ import annotations

import re
from typing import Any, Callable

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PARENT_RECEIPT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _sha256(value: object, label: str) -> str:
    text = _text(value, label).lower()
    if not _SHA256_RE.fullmatch(text):
        raise ValueError(f"{label} must be a lowercase SHA-256 identity")
    return text


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


def bound_fields(
    payload: dict[str, Any],
    state: str,
    *,
    findings_received: str,
    execution_modes: frozenset[str],
    attempt_id: Callable[[object | None], str],
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
    retry_of = attempt_id(payload["retry_of"]) if payload.get("retry_of") is not None else None
    retry_count = payload.get("retry_count", 0)
    if not isinstance(retry_count, int) or retry_count < 0:
        raise ValueError("retry_count must be a non-negative integer")
    return {
        "findings_identity": findings,
        "reviewed_input_identity": reviewed_input_identity,
        "execution_mode": execution_mode,
        "backend": _text(payload["backend"], "backend") if payload.get("backend") is not None else None,
        "prompt_sha256": prompt_sha256,
        "schema_sha256": schema_sha256,
        "capability_launch_envelope_sha256": capability_launch_envelope_sha256,
        "retry_of": retry_of,
        "retry_count": retry_count,
    }
