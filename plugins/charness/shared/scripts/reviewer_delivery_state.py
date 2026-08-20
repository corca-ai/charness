"""Pure parent-side state and provenance rules for reviewer delivery."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "charness.reviewer_delivery.v1"
SPAWN_ACCEPTED = "spawn-accepted"
RUNNING = "running"
FINDINGS_RECEIVED = "findings-received"
INTERRUPTED = "interrupted"
TIMED_OUT = "timed-out"
HOST_CHANNEL_UNREADABLE = "host-channel-unreadable"
HOST_CAPACITY_BLOCKED = "host-capacity-blocked"
SPAWN_ACCEPTED_NO_DELIVERY = "spawn-accepted-no-delivery"
NON_DELIVERY_UNKNOWN = "non-delivery-unknown"
RECOVERED_FROM_TRANSCRIPT = "findings-recovered-from-transcript"

CANONICAL_STATES = (
    SPAWN_ACCEPTED,
    RUNNING,
    FINDINGS_RECEIVED,
    INTERRUPTED,
    TIMED_OUT,
    HOST_CHANNEL_UNREADABLE,
    HOST_CAPACITY_BLOCKED,
    SPAWN_ACCEPTED_NO_DELIVERY,
    NON_DELIVERY_UNKNOWN,
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
    }
)
APPROVAL_STATE = FINDINGS_RECEIVED
_ALLOWED_TRANSITIONS = {
    SPAWN_ACCEPTED: frozenset(CANONICAL_STATES[1:]),
    RUNNING: frozenset(CANONICAL_STATES[2:]),
}


class DeliveryError(ValueError):
    """An impossible or malformed delivery observation."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _is_terminal(state: str) -> bool:
    return state in TERMINAL_STATES


def _event(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict) or not _text(event.get("event_id"), "event_id"):
        raise DeliveryError("history and observations require event_id")
    return event


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
        retry_of: str | None = None,
        retry_count: int = 0,
    ) -> "DeliveryAttempt":
        when = _text(recorded_at, "recorded_at")
        attempt = cls(
            attempt_id=_attempt_id(attempt_id),
            scope=_text(scope, "scope"),
            packet_identity=_text(packet_identity, "packet_identity"),
            parent_receipt_identity=_text(parent_receipt_identity, "parent_receipt_identity"),
            boundary_fingerprint=_text(boundary_fingerprint, "boundary_fingerprint"),
            state=SPAWN_ACCEPTED,
            observed_signal="spawn accepted; parent delivery not yet proven",
            terminal=False,
            recorded_at=when,
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
        if not isinstance(terminal, bool) or terminal != _is_terminal(state):
            raise DeliveryError(f"terminal flag does not match state `{state}`")
        history = payload.get("history", [])
        observations = payload.get("observations", [])
        if not isinstance(history, list) or not isinstance(observations, list):
            raise DeliveryError("history and observations must be lists")
        for item in [*history, *observations]:
            _event(item)
        findings = payload.get("findings_identity")
        retry_of = payload.get("retry_of")
        retry_count = payload.get("retry_count", 0)
        if findings is not None:
            findings = _text(findings, "findings_identity")
        if retry_of is not None:
            retry_of = _attempt_id(retry_of)
        if not isinstance(retry_count, int) or retry_count < 0:
            raise DeliveryError("retry_count must be a non-negative integer")
        return cls(
            attempt_id=_attempt_id(payload["attempt_id"]),
            scope=_text(payload["scope"], "scope"),
            packet_identity=_text(payload["packet_identity"], "packet_identity"),
            parent_receipt_identity=_text(payload["parent_receipt_identity"], "parent_receipt_identity"),
            boundary_fingerprint=_text(payload["boundary_fingerprint"], "boundary_fingerprint"),
            state=state,
            observed_signal=_text(payload["observed_signal"], "observed_signal"),
            terminal=terminal,
            recorded_at=_text(payload["recorded_at"], "recorded_at"),
            findings_identity=findings,
            retry_of=retry_of,
            retry_count=retry_count,
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
        if self.findings_identity is not None:
            payload["findings_identity"] = self.findings_identity
        if self.retry_of is not None:
            payload["retry_of"] = self.retry_of
        return payload

    @property
    def approval_eligible(self) -> bool:
        return self.state == APPROVAL_STATE and self.terminal and self.findings_identity is not None

    def _apply_transition(self, state: str, signal: str, recorded_at: str) -> None:
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
        self.terminal = _is_terminal(state)
        self.recorded_at = recorded_at
        self.history.append(
            {
                "event_id": _event_id(),
                "state": state,
                "signal": signal,
                "terminal": self.terminal,
                "recorded_at": recorded_at,
            }
        )

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
            "parent_receipt_identity": _text(parent_receipt_identity, "parent_receipt_identity"),
            "findings_identity": _text(findings_identity, "findings_identity"),
        }
        if self.state in TERMINAL_STATES:
            self.observations.append(
                {
                    "event_id": _event_id(),
                    "state": "late-or-duplicate-findings",
                    "signal": "findings arrived after the attempt was terminal",
                    "recorded_at": when,
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
                {"event_id": _event_id(), "state": "foreign-findings", "recorded_at": when, **supplied}
            )
            return False
        self.findings_identity = supplied["findings_identity"]
        self._apply_transition(FINDINGS_RECEIVED, "findings received in parent context", when)
        return True

    def record_recovery(self, signal: str, recorded_at: str) -> None:
        self.observations.append(
            {
                "event_id": _event_id(),
                "state": RECOVERED_FROM_TRANSCRIPT,
                "signal": _text(signal, "signal"),
                "recorded_at": _text(recorded_at, "recorded_at"),
                "approval_eligible": False,
            }
        )
