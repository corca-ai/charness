"""Serialization and validation for a reviewer delivery attempt."""

from __future__ import annotations

from typing import Any

try:
    from reviewer_delivery_fields import bound_fields
    from reviewer_delivery_history import validate_history
    from reviewer_delivery_schema import (
        _ALLOWED_TRANSITIONS,
        _EXECUTION_MODES,
        CANONICAL_STATES,
        FINDINGS_RECEIVED,
        PARTIAL,
        SPAWN_ACCEPTED,
        TERMINAL_STATES,
        DeliveryError,
        _attempt_id,
        _text,
        _validated_parent_receipt_identity,
    )
except ImportError:
    from skills.shared.scripts.reviewer_delivery_fields import bound_fields
    from skills.shared.scripts.reviewer_delivery_history import validate_history
    from skills.shared.scripts.reviewer_delivery_schema import (
        _ALLOWED_TRANSITIONS,
        _EXECUTION_MODES,
        CANONICAL_STATES,
        FINDINGS_RECEIVED,
        PARTIAL,
        SPAWN_ACCEPTED,
        TERMINAL_STATES,
        DeliveryError,
        _attempt_id,
        _text,
        _validated_parent_receipt_identity,
    )


def from_dict(cls: type, payload: dict[str, Any]):
    if not isinstance(payload, dict):
        raise DeliveryError("attempt must be an object")
    required = (
        "attempt_id", "scope", "packet_identity", "parent_receipt_identity",
        "state", "observed_signal", "terminal", "recorded_at",
    )
    missing = [key for key in required if key not in payload]
    if missing:
        raise DeliveryError(f"attempt missing fields: {', '.join(missing)}")
    state = _text(payload["state"], "state")
    if state not in CANONICAL_STATES:
        raise DeliveryError(f"unknown delivery state: {state}")
    terminal = payload["terminal"]
    if not isinstance(terminal, bool) or terminal != (state in TERMINAL_STATES):
        raise DeliveryError(f"terminal flag does not match state `{state}`")
    history = payload.get("history", [])
    observations = payload.get("observations", [])
    if not isinstance(history, list) or not isinstance(observations, list):
        raise DeliveryError("history and observations must be lists")
    try:
        fields = bound_fields(
            payload, state, findings_received=FINDINGS_RECEIVED,
            execution_modes=_EXECUTION_MODES, attempt_id=_attempt_id,
            partial_state=PARTIAL,
        )
        normalized_attempt_id = _attempt_id(payload["attempt_id"])
        validate_history(
            history, observations, state, normalized_attempt_id,
            fields["findings_identity"], spawn_accepted=SPAWN_ACCEPTED,
            canonical_states=CANONICAL_STATES, terminal_states=TERMINAL_STATES,
            allowed_transitions=_ALLOWED_TRANSITIONS,
            partial_state=PARTIAL,
            partial_output_descriptor=fields["partial_output"],
        )
    except ValueError as exc:
        raise DeliveryError(str(exc)) from exc
    return cls(
        attempt_id=normalized_attempt_id,
        scope=_text(payload["scope"], "scope"),
        packet_identity=_text(payload["packet_identity"], "packet_identity"),
        parent_receipt_identity=_validated_parent_receipt_identity(payload["parent_receipt_identity"]),
        boundary_fingerprint=fields["boundary_fingerprint"],
        boundary_mode=fields["boundary_mode"],
        state=state,
        observed_signal=_text(payload["observed_signal"], "observed_signal"),
        terminal=terminal,
        recorded_at=_text(payload["recorded_at"], "recorded_at"),
        reviewed_input_identity=fields["reviewed_input_identity"],
        execution_mode=fields["execution_mode"],
        backend=fields["backend"],
        prompt_sha256=fields["prompt_sha256"],
        schema_sha256=fields["schema_sha256"],
        capability_launch_envelope_sha256=fields["capability_launch_envelope_sha256"],
        output_file=fields["output_file"],
        receipt_file=fields["receipt_file"],
        producer_run_id=fields["producer_run_id"],
        findings_identity=fields["findings_identity"],
        partial_output=fields["partial_output"],
        retry_of=fields["retry_of"],
        retry_count=fields["retry_count"],
        history=history,
        observations=observations,
    )


def to_dict(attempt) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "attempt_id": attempt.attempt_id,
        "scope": attempt.scope,
        "packet_identity": attempt.packet_identity,
        "parent_receipt_identity": attempt.parent_receipt_identity,
        "boundary_mode": attempt.boundary_mode,
        "state": attempt.state,
        "observed_signal": attempt.observed_signal,
        "terminal": attempt.terminal,
        "recorded_at": attempt.recorded_at,
        "history": attempt.history,
        "observations": attempt.observations,
        "retry_count": attempt.retry_count,
    }
    if attempt.boundary_fingerprint is not None:
        payload["boundary_fingerprint"] = attempt.boundary_fingerprint
    for key in (
        "reviewed_input_identity", "execution_mode", "backend", "prompt_sha256",
        "schema_sha256", "capability_launch_envelope_sha256", "output_file",
        "receipt_file", "producer_run_id", "findings_identity", "partial_output", "retry_of",
    ):
        value = getattr(attempt, key)
        if value is not None:
            payload[key] = value
    return payload
