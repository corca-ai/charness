"""Shared schema, scalar validation, and event helpers for delivery attempts."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from reviewer_delivery_fields import parent_receipt_identity as _parent_receipt_identity
except ImportError:
    from skills.shared.scripts.reviewer_delivery_fields import (
        parent_receipt_identity as _parent_receipt_identity,
    )

SCHEMA_VERSION = "charness.reviewer_delivery.v1"
SPAWN_ACCEPTED = "spawn-accepted"
RUNNING = "running"
PARTIAL = "partial"
FINDINGS_RECEIVED = "findings-received"
INTERRUPTED = "interrupted"
TIMED_OUT = "timed-out"
HOST_CHANNEL_UNREADABLE = "host-channel-unreadable"
HOST_CAPACITY_BLOCKED = "host-capacity-blocked"
SPAWN_ACCEPTED_NO_DELIVERY = "spawn-accepted-no-delivery"
NON_DELIVERY_UNKNOWN = "non-delivery-unknown"
COLLECTION_FAILED = "collection-failed"
RECOVERED_FROM_TRANSCRIPT = "findings-recovered-from-transcript"
CANONICAL_STATES = (
    SPAWN_ACCEPTED,
    RUNNING,
    PARTIAL,
    FINDINGS_RECEIVED,
    INTERRUPTED,
    TIMED_OUT,
    HOST_CHANNEL_UNREADABLE,
    HOST_CAPACITY_BLOCKED,
    SPAWN_ACCEPTED_NO_DELIVERY,
    NON_DELIVERY_UNKNOWN,
    COLLECTION_FAILED,
)
TERMINAL_STATES = frozenset(
    {
        FINDINGS_RECEIVED,
        INTERRUPTED,
        TIMED_OUT,
        HOST_CHANNEL_UNREADABLE,
        HOST_CAPACITY_BLOCKED,
        SPAWN_ACCEPTED_NO_DELIVERY,
        NON_DELIVERY_UNKNOWN,
        COLLECTION_FAILED,
    }
)
RETRYABLE_STATES = frozenset(
    {
        INTERRUPTED,
        TIMED_OUT,
        HOST_CHANNEL_UNREADABLE,
        HOST_CAPACITY_BLOCKED,
        SPAWN_ACCEPTED_NO_DELIVERY,
        NON_DELIVERY_UNKNOWN,
        COLLECTION_FAILED,
    }
)
APPROVAL_STATE = FINDINGS_RECEIVED
_ALLOWED_TRANSITIONS = {
    SPAWN_ACCEPTED: frozenset(CANONICAL_STATES[1:]),
    RUNNING: frozenset(CANONICAL_STATES[2:]),
    PARTIAL: frozenset(CANONICAL_STATES[3:]),
}
_EXECUTION_MODES = frozenset({"file-backed-worker", "typed-subagent"})


class DeliveryError(ValueError):
    """An impossible or malformed delivery observation."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validated_parent_receipt_identity(value: object) -> str:
    try:
        return _parent_receipt_identity(value)
    except ValueError as exc:
        raise DeliveryError(str(exc)) from exc


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DeliveryError(f"{label} must be a non-empty string")
    return value.strip()


def _attempt_id(value: object | None = None) -> str:
    candidate = uuid.uuid4().hex if value is None else _text(value, "attempt_id")
    if len(candidate) > 128 or any(char.isspace() for char in candidate):
        raise DeliveryError("attempt_id must be a short, whitespace-free identifier")
    return candidate


def _event_id() -> str:
    return uuid.uuid4().hex


def _event_context(attempt: Any) -> dict[str, Any]:
    return {
        "attempt_id": attempt.attempt_id,
        "scope": attempt.scope,
        "packet_identity": attempt.packet_identity,
        "parent_receipt_identity": attempt.parent_receipt_identity,
        "capability_launch_envelope_sha256": attempt.capability_launch_envelope_sha256,
    }
