"""The delivery-attempt state machine used by the parent-side ledger."""
# ruff: noqa: I001

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from reviewer_delivery_schema import (
        _ALLOWED_TRANSITIONS,
        APPROVAL_STATE,
        CANONICAL_STATES,
        FINDINGS_RECEIVED,
        NON_DELIVERY_UNKNOWN,
        PARTIAL,
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
        APPROVAL_STATE,
        CANONICAL_STATES,
        FINDINGS_RECEIVED,
        NON_DELIVERY_UNKNOWN,
        PARTIAL,
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
    from reviewer_delivery_attempt_codec import from_dict as _from_dict, to_dict as _to_dict
    from reviewer_delivery_fields import _sha256, boundary_binding, partial_output as _partial_output
except ImportError:
    from skills.shared.scripts.reviewer_delivery_attempt_codec import from_dict as _from_dict, to_dict as _to_dict
    from skills.shared.scripts.reviewer_delivery_fields import (
        _sha256,
        boundary_binding,
        partial_output as _partial_output,
    )


@dataclass
class DeliveryAttempt:
    attempt_id: str
    scope: str
    packet_identity: str
    parent_receipt_identity: str
    boundary_fingerprint: str | None
    boundary_mode: str
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
    output_file: str | None = None
    receipt_file: str | None = None
    producer_run_id: str | None = None
    findings_identity: str | None = None
    partial_output: dict[str, Any] | None = None
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
        recorded_at: str,
        boundary_fingerprint: str | None = None,
        boundary_mode: str | None = None,
        reviewed_input_identity: str | None = None,
        execution_mode: str | None = None,
        backend: str | None = None,
        prompt_sha256: str | None = None,
        schema_sha256: str | None = None,
        capability_launch_envelope_sha256: str | None = None,
        output_file: str | None = None, receipt_file: str | None = None, producer_run_id: str | None = None,
        retry_of: str | None = None,
        retry_count: int = 0,
    ) -> "DeliveryAttempt":
        if type(retry_count) is not int or retry_count < 0:
            raise DeliveryError("retry_count must be a non-negative integer")
        if retry_count == 0 and retry_of is not None:
            raise DeliveryError("retry_of requires a positive retry_count")
        if retry_count > 0 and retry_of is None:
            raise DeliveryError("positive retry_count requires retry_of")
        when = _text(recorded_at, "recorded_at")
        normalized_boundary_mode, normalized_boundary_fingerprint = boundary_binding(
            boundary_mode, boundary_fingerprint
        )
        attempt = cls(
            attempt_id=_attempt_id(attempt_id),
            scope=_text(scope, "scope"),
            packet_identity=_text(packet_identity, "packet_identity"),
            parent_receipt_identity=_validated_parent_receipt_identity(parent_receipt_identity),
            boundary_fingerprint=normalized_boundary_fingerprint,
            boundary_mode=normalized_boundary_mode,
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
            output_file=_text(output_file, "output_file") if output_file is not None else None, receipt_file=_text(receipt_file, "receipt_file") if receipt_file is not None else None, producer_run_id=_text(producer_run_id, "producer_run_id") if producer_run_id is not None else None,
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
        return _from_dict(cls, payload)

    def to_dict(self) -> dict[str, Any]:
        return _to_dict(self)

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
        if state == PARTIAL:
            raise DeliveryError("partial requires record_partial output binding")
        self._apply_transition(state, signal, recorded_at)

    def record_partial(
        self,
        *,
        partial_output: dict[str, Any],
        recorded_at: str,
        signal: str = "typed partial reviewer output preserved",
    ) -> bool:
        """Record useful output without making it a terminal delivery."""
        when = _text(recorded_at, "recorded_at")
        descriptor = _partial_output(partial_output)
        if self.state in TERMINAL_STATES:
            self.observations.append(
                {
                    "event_id": _event_id(),
                    "state": "late-or-duplicate-partial",
                    "signal": "partial output arrived after the attempt was terminal",
                    "recorded_at": when,
                    **_event_context(self),
                    "partial_output": descriptor,
                }
            )
            return False
        if self.state == PARTIAL:
            self.observations.append(
                {
                    "event_id": _event_id(),
                    "state": "duplicate-partial",
                    "signal": "partial output was already recorded for the attempt",
                    "recorded_at": when,
                    **_event_context(self),
                    "partial_output": descriptor,
                }
            )
            return False
        self.partial_output = descriptor
        self._apply_transition(
            PARTIAL,
            signal,
            when,
            event_fields={"partial_output": descriptor},
        )
        return True

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
