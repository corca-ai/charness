"""The delivery-attempt state machine used by the parent-side ledger."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from reviewer_delivery_schema import (
        _ALLOWED_TRANSITIONS,
        _EXECUTION_MODES,
        APPROVAL_STATE,
        CANONICAL_STATES,
        FINDINGS_RECEIVED,
        NON_DELIVERY_UNKNOWN,
        RECOVERED_FROM_TRANSCRIPT,
        SPAWN_ACCEPTED,
        TERMINAL_STATES,
        DeliveryError,
        _attempt_id,
        _event_context,
        _event_id,
        _text,
        _validated_parent_receipt_identity,
    )
except ImportError:
    from skills.shared.scripts.reviewer_delivery_schema import (
        _ALLOWED_TRANSITIONS,
        _EXECUTION_MODES,
        APPROVAL_STATE,
        CANONICAL_STATES,
        FINDINGS_RECEIVED,
        NON_DELIVERY_UNKNOWN,
        RECOVERED_FROM_TRANSCRIPT,
        SPAWN_ACCEPTED,
        TERMINAL_STATES,
        DeliveryError,
        _attempt_id,
        _event_context,
        _event_id,
        _text,
        _validated_parent_receipt_identity,
    )

try:
    from reviewer_delivery_fields import _sha256, bound_fields
    from reviewer_delivery_history import validate_history
except ImportError:
    from skills.shared.scripts.reviewer_delivery_fields import _sha256, bound_fields
    from skills.shared.scripts.reviewer_delivery_history import validate_history


@dataclass
class DeliveryAttempt:
    attempt_id: str
    scope: str
    packet_identity: str
    parent_receipt_identity: str
    boundary_fingerprint: str
    state: str
    observed_signal: str
    terminal: bool
    recorded_at: str
    reviewed_input_identity: str | None = None
    execution_mode: str | None = None
    backend: str | None = None
    prompt_sha256: str | None = None
    schema_sha256: str | None = None
    capability_launch_envelope_sha256: str | None = None
    findings_identity: str | None = None
    retry_of: str | None = None
    retry_count: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    observations: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def start(
        cls,
        *,
        attempt_id: str | None,
        scope: str,
        packet_identity: str,
        parent_receipt_identity: str,
        boundary_fingerprint: str,
        recorded_at: str,
        reviewed_input_identity: str | None = None,
        execution_mode: str | None = None,
        backend: str | None = None,
        prompt_sha256: str | None = None,
        schema_sha256: str | None = None,
        capability_launch_envelope_sha256: str | None = None,
        retry_of: str | None = None,
        retry_count: int = 0,
    ) -> "DeliveryAttempt":
        when = _text(recorded_at, "recorded_at")
        attempt = cls(
            attempt_id=_attempt_id(attempt_id),
            scope=_text(scope, "scope"),
            packet_identity=_text(packet_identity, "packet_identity"),
            parent_receipt_identity=_validated_parent_receipt_identity(parent_receipt_identity),
            boundary_fingerprint=_text(boundary_fingerprint, "boundary_fingerprint"),
            state=SPAWN_ACCEPTED,
            observed_signal="spawn accepted; parent delivery not yet proven",
            terminal=False,
            recorded_at=when,
            reviewed_input_identity=(
                _sha256(reviewed_input_identity, "reviewed_input_identity")
                if reviewed_input_identity is not None
                else None
            ),
            execution_mode=_text(execution_mode, "execution_mode") if execution_mode is not None else None,
            backend=_text(backend, "backend") if backend is not None else None,
            prompt_sha256=_sha256(prompt_sha256, "prompt_sha256") if prompt_sha256 is not None else None,
            schema_sha256=_sha256(schema_sha256, "schema_sha256") if schema_sha256 is not None else None,
            capability_launch_envelope_sha256=(
                _sha256(capability_launch_envelope_sha256, "capability_launch_envelope_sha256")
                if capability_launch_envelope_sha256 is not None
                else None
            ),
            retry_of=retry_of,
            retry_count=retry_count,
        )
        attempt.history.append(
            {
                "event_id": _event_id(),
                "state": SPAWN_ACCEPTED,
                "signal": attempt.observed_signal,
                "terminal": False,
                "recorded_at": when,
                **_event_context(attempt),
            }
        )
        return attempt

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DeliveryAttempt":
        if not isinstance(payload, dict):
            raise DeliveryError("attempt must be an object")
        required = (
            "attempt_id",
            "scope",
            "packet_identity",
            "parent_receipt_identity",
            "boundary_fingerprint",
            "state",
            "observed_signal",
            "terminal",
            "recorded_at",
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
                payload,
                state,
                findings_received=FINDINGS_RECEIVED,
                execution_modes=_EXECUTION_MODES,
                attempt_id=_attempt_id,
            )
            normalized_attempt_id = _attempt_id(payload["attempt_id"])
            validate_history(
                history,
                observations,
                state,
                normalized_attempt_id,
                fields["findings_identity"],
                spawn_accepted=SPAWN_ACCEPTED,
                canonical_states=CANONICAL_STATES,
                terminal_states=TERMINAL_STATES,
                allowed_transitions=_ALLOWED_TRANSITIONS,
            )
        except ValueError as exc:
            raise DeliveryError(str(exc)) from exc
        return cls(
            attempt_id=normalized_attempt_id,
            scope=_text(payload["scope"], "scope"),
            packet_identity=_text(payload["packet_identity"], "packet_identity"),
            parent_receipt_identity=_validated_parent_receipt_identity(payload["parent_receipt_identity"]),
            boundary_fingerprint=_text(payload["boundary_fingerprint"], "boundary_fingerprint"),
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
            findings_identity=fields["findings_identity"],
            retry_of=fields["retry_of"],
            retry_count=fields["retry_count"],
            history=history,
            observations=observations,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "attempt_id": self.attempt_id,
            "scope": self.scope,
            "packet_identity": self.packet_identity,
            "parent_receipt_identity": self.parent_receipt_identity,
            "boundary_fingerprint": self.boundary_fingerprint,
            "state": self.state,
            "observed_signal": self.observed_signal,
            "terminal": self.terminal,
            "recorded_at": self.recorded_at,
            "history": self.history,
            "observations": self.observations,
            "retry_count": self.retry_count,
        }
        payload.update(
            {
                key: value
                for key in (
                    "reviewed_input_identity",
                    "execution_mode",
                    "backend",
                    "prompt_sha256",
                    "schema_sha256",
                    "capability_launch_envelope_sha256",
                )
                if (value := getattr(self, key)) is not None
            }
        )
        if self.findings_identity is not None:
            payload["findings_identity"] = self.findings_identity
        if self.retry_of is not None:
            payload["retry_of"] = self.retry_of
        return payload

    @property
    def delivery_complete(self) -> bool:
        return self.state == APPROVAL_STATE and self.terminal and self.findings_identity is not None

    def _apply_transition(
        self,
        state: str,
        signal: str,
        recorded_at: str,
        *,
        event_fields: dict[str, Any] | None = None,
    ) -> None:
        state = _text(state, "state")
        signal = _text(signal, "signal")
        recorded_at = _text(recorded_at, "recorded_at")
        if state not in CANONICAL_STATES:
            raise DeliveryError(f"unknown delivery state: {state}")
        if state == self.state:
            raise DeliveryError(f"duplicate canonical state `{state}`; record it as an observation")
        if self.state in TERMINAL_STATES:
            raise DeliveryError(f"terminal attempt `{self.attempt_id}` cannot transition from `{self.state}`")
        if state not in _ALLOWED_TRANSITIONS.get(self.state, frozenset()):
            raise DeliveryError(f"invalid transition `{self.state}` -> `{state}`")
        self.state = state
        self.observed_signal = signal
        self.terminal = state in TERMINAL_STATES
        self.recorded_at = recorded_at
        event = {
            "event_id": _event_id(),
            "state": state,
            "signal": signal,
            "terminal": self.terminal,
            "recorded_at": recorded_at,
            **_event_context(self),
        }
        if event_fields:
            event.update(event_fields)
        self.history.append(event)

    def transition(self, state: str, signal: str, recorded_at: str) -> None:
        if state == FINDINGS_RECEIVED:
            raise DeliveryError("findings-received requires record_findings provenance checks")
        self._apply_transition(state, signal, recorded_at)

    def record_findings(
        self,
        *,
        scope: str,
        packet_identity: str,
        parent_receipt_identity: str,
        findings_identity: str,
        recorded_at: str,
    ) -> bool:
        when = _text(recorded_at, "recorded_at")
        supplied = {
            "scope": _text(scope, "scope"),
            "packet_identity": _text(packet_identity, "packet_identity"),
            "parent_receipt_identity": _validated_parent_receipt_identity(parent_receipt_identity),
            "findings_identity": _sha256(findings_identity, "findings_identity"),
        }
        if self.state in TERMINAL_STATES:
            self.observations.append(
                {
                    "event_id": _event_id(),
                    "state": "late-or-duplicate-findings",
                    "signal": "findings arrived after the attempt was terminal",
                    "recorded_at": when,
                    **_event_context(self),
                    **supplied,
                }
            )
            return False
        expected = {
            "scope": self.scope,
            "packet_identity": self.packet_identity,
            "parent_receipt_identity": self.parent_receipt_identity,
        }
        mismatches = [key for key, value in expected.items() if supplied[key] != value]
        if mismatches:
            self._apply_transition(
                NON_DELIVERY_UNKNOWN,
                "findings provenance mismatch: " + ", ".join(mismatches),
                when,
            )
            self.observations.append(
                {
                    "event_id": _event_id(),
                    "state": "foreign-findings",
                    "signal": "findings provenance did not match the attempt",
                    "recorded_at": when,
                    **_event_context(self),
                    **supplied,
                }
            )
            return False
        self.findings_identity = supplied["findings_identity"]
        self._apply_transition(
            FINDINGS_RECEIVED,
            "findings received in parent context",
            when,
            event_fields={"findings_identity": self.findings_identity},
        )
        return True

    def record_recovery(self, signal: str, recorded_at: str) -> None:
        self.observations.append(
            {
                "event_id": _event_id(),
                "state": RECOVERED_FROM_TRANSCRIPT,
                "signal": _text(signal, "signal"),
                "recorded_at": _text(recorded_at, "recorded_at"),
                "delivery_complete": False,
                **_event_context(self),
            }
        )
