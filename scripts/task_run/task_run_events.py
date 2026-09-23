"""Frozen v1 envelope shared by task-run decision and friction event producers.

Producer-specific event facts live inside ``facts``. Version 1 keeps the
envelope, producer names, and event-kind vocabulary stable while allowing each
producer to own the detail schema it writes there.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any

EVENT_SCHEMA_VERSION = 1
EVENT_FIELDS = frozenset(
    {"schema_version", "event_id", "occurred_at", "source", "event_kind", "facts"}
)
EVENT_KINDS_BY_SOURCE = {
    "decision-ledger": frozenset(
        {"contract-amendment", "vocabulary-closure", "design-approval"}
    ),
    "friction-log": frozenset(
        {"block", "relaunch", "conflict-resolution", "premise-failure"}
    ),
}


class EventSchemaError(ValueError):
    """An event does not conform to the shared task-run v1 envelope."""


def _json_value(value: object) -> bool:
    if value is None or isinstance(value, (str, bool, int)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _json_value(item) for key, item in value.items())
    return False


def validate_event(event: object) -> dict[str, Any]:
    """Validate and return a JSON-normalized event envelope or raise an error."""
    if not isinstance(event, Mapping):
        raise EventSchemaError("event must be an object")
    if set(event) != EVENT_FIELDS:
        missing = sorted(EVENT_FIELDS - set(event))
        extra = sorted(set(event) - EVENT_FIELDS)
        raise EventSchemaError(f"event fields mismatch: missing={missing}, extra={extra}")
    version = event.get("schema_version")
    if (
        isinstance(version, bool)
        or not isinstance(version, int)
        or version != EVENT_SCHEMA_VERSION
    ):
        raise EventSchemaError(f"schema_version must be {EVENT_SCHEMA_VERSION}")
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id.strip():
        raise EventSchemaError("event_id must be a non-empty string")
    occurred_at = event.get("occurred_at")
    if not isinstance(occurred_at, str) or not occurred_at.strip():
        raise EventSchemaError("occurred_at must be a UTC timestamp")
    try:
        timestamp = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventSchemaError("occurred_at must be a UTC timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() != timedelta(0):
        raise EventSchemaError("occurred_at must include a UTC offset")
    source = event.get("source")
    if not isinstance(source, str) or source not in EVENT_KINDS_BY_SOURCE:
        raise EventSchemaError(f"source must be one of {sorted(EVENT_KINDS_BY_SOURCE)}")
    event_kind = event.get("event_kind")
    if not isinstance(event_kind, str) or event_kind not in EVENT_KINDS_BY_SOURCE[source]:
        raise EventSchemaError(f"event_kind is not valid for source {source!r}")
    facts = event.get("facts")
    if not isinstance(facts, Mapping) or not _json_value(dict(facts)):
        raise EventSchemaError("facts must be an object")
    try:
        normalized_facts = json.loads(json.dumps(dict(facts), allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise EventSchemaError("facts must contain only JSON values") from exc
    if not isinstance(normalized_facts, dict):
        raise EventSchemaError("facts must be an object")
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": event_id.strip(),
        "occurred_at": occurred_at,
        "source": source,
        "event_kind": event_kind,
        "facts": normalized_facts,
    }
