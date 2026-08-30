"""Compatibility surface for the reviewer delivery state machine.

Schema/identity rules live in ``reviewer_delivery_schema`` and the transition
model lives in ``reviewer_delivery_attempt``.  This module remains the stable
import path used by the rest of the harness and installed plugin.
"""

from __future__ import annotations

try:
    from reviewer_delivery_attempt import DeliveryAttempt
    from reviewer_delivery_schema import (
        APPROVAL_STATE,
        CANONICAL_STATES,
        COLLECTION_FAILED,
        FINDINGS_RECEIVED,
        HOST_CAPACITY_BLOCKED,
        HOST_CHANNEL_UNREADABLE,
        INTERRUPTED,
        NON_DELIVERY_UNKNOWN,
        PARTIAL,
        RECOVERED_FROM_TRANSCRIPT,
        RETRYABLE_STATES,
        RUNNING,
        SCHEMA_VERSION,
        SPAWN_ACCEPTED,
        SPAWN_ACCEPTED_NO_DELIVERY,
        TERMINAL_STATES,
        TIMED_OUT,
        DeliveryError,
        utc_now,
    )
except ImportError:
    from skills.shared.scripts.reviewer_delivery_attempt import DeliveryAttempt
    from skills.shared.scripts.reviewer_delivery_schema import (
        APPROVAL_STATE,
        CANONICAL_STATES,
        COLLECTION_FAILED,
        FINDINGS_RECEIVED,
        HOST_CAPACITY_BLOCKED,
        HOST_CHANNEL_UNREADABLE,
        INTERRUPTED,
        NON_DELIVERY_UNKNOWN,
        PARTIAL,
        RECOVERED_FROM_TRANSCRIPT,
        RETRYABLE_STATES,
        RUNNING,
        SCHEMA_VERSION,
        SPAWN_ACCEPTED,
        SPAWN_ACCEPTED_NO_DELIVERY,
        TERMINAL_STATES,
        TIMED_OUT,
        DeliveryError,
        utc_now,
    )

__all__ = [
    "APPROVAL_STATE",
    "CANONICAL_STATES",
    "COLLECTION_FAILED",
    "DeliveryAttempt",
    "DeliveryError",
    "FINDINGS_RECEIVED",
    "HOST_CAPACITY_BLOCKED",
    "HOST_CHANNEL_UNREADABLE",
    "INTERRUPTED",
    "NON_DELIVERY_UNKNOWN",
    "PARTIAL",
    "RECOVERED_FROM_TRANSCRIPT",
    "RUNNING",
    "SCHEMA_VERSION",
    "SPAWN_ACCEPTED",
    "SPAWN_ACCEPTED_NO_DELIVERY",
    "TERMINAL_STATES",
    "RETRYABLE_STATES",
    "TIMED_OUT",
    "utc_now",
]
