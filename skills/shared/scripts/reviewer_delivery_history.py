"""Validation of the append-only event history in a reviewer delivery attempt."""

from __future__ import annotations

from typing import Any

try:
    from reviewer_delivery_fields import partial_output
except ImportError:
    from skills.shared.scripts.reviewer_delivery_fields import partial_output


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _event(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict) or not _text(event.get("event_id"), "event_id"):
        raise ValueError("history and observations require event_id")
    return event


def _validate_event_collection(items: list[dict[str, Any]], attempt_id: str) -> None:
    event_ids: set[str] = set()
    for item in items:
        _event(item)
        if not _text(item.get("signal"), "event signal"):
            raise ValueError("history and observations require a non-empty signal")
        if not _text(item.get("recorded_at"), "event recorded_at"):
            raise ValueError("history and observations require recorded_at")
        if item.get("attempt_id") != attempt_id:
            raise ValueError("history and observations must bind to their parent attempt_id")
        if item["event_id"] in event_ids:
            raise ValueError(f"duplicate event_id: {item['event_id']}")
        event_ids.add(item["event_id"])
        if item.get("partial_output") is not None:
            partial_output(item["partial_output"])


def _validate_transitions(
    history: list[dict[str, Any]],
    state: str,
    canonical_states: tuple[str, ...],
    terminal_states: frozenset[str],
    allowed_transitions: dict[str, frozenset[str]],
) -> None:
    prior_state = history[0]["state"]
    for item in history[1:]:
        event_state = item.get("state")
        if event_state not in canonical_states:
            raise ValueError(f"history contains unknown canonical state: {event_state}")
        if item.get("terminal") != (event_state in terminal_states):
            raise ValueError(f"history terminal flag does not match state `{event_state}`")
        if event_state not in allowed_transitions.get(prior_state, frozenset()):
            raise ValueError(f"history contains invalid transition `{prior_state}` -> `{event_state}`")
        prior_state = event_state
    if prior_state != state:
        raise ValueError("history final state does not match attempt state")


def validate_history(
    history: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    state: str,
    attempt_id: str,
    findings_identity: str | None,
    *,
    spawn_accepted: str,
    canonical_states: tuple[str, ...],
    terminal_states: frozenset[str],
    allowed_transitions: dict[str, frozenset[str]],
    partial_state: str = "partial",
    partial_output_descriptor: dict[str, Any] | None = None,
) -> None:
    """Reject detached, state-valid, or independently edited event histories."""
    if not history:
        raise ValueError("history must contain the initial spawn-accepted event")
    if history[0].get("state") != spawn_accepted:
        raise ValueError("history must begin with spawn-accepted")
    _validate_event_collection([*history, *observations], attempt_id)
    _validate_transitions(history, state, canonical_states, terminal_states, allowed_transitions)
    for item in history:
        if item.get("partial_output") is not None and item.get("state") != partial_state:
            raise ValueError("partial_output is only valid on a partial history event")
    partial_events = [
        item.get("partial_output")
        for item in history
        if item.get("partial_output") is not None
    ]
    if partial_output_descriptor is not None and partial_output_descriptor not in partial_events:
        raise ValueError("partial_output must be bound by a partial history event")
    if state == partial_state:
        if not partial_events:
            raise ValueError("partial history must bind partial_output")
        if partial_output_descriptor != partial_events[-1]:
            raise ValueError("partial state must retain the latest partial_output")
    if state == "findings-received":
        if history[-1].get("findings_identity") != findings_identity:
            raise ValueError("findings-received history must bind its findings_identity")
    elif any(item.get("findings_identity") is not None for item in history):
        raise ValueError("non-findings history cannot carry findings_identity")
