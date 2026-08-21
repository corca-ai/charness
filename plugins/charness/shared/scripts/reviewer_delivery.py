#!/usr/bin/env python3
"""CLI and durable persistence for the reviewer delivery state machine."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import reviewer_delivery_state as _state
except ImportError:
    from skills.shared.scripts import reviewer_delivery_state as _state

try:
    from reviewer_output import emit_yaml
except ImportError:
    from skills.shared.scripts.reviewer_output import emit_yaml

CANONICAL_STATES = _state.CANONICAL_STATES
FINDINGS_RECEIVED = _state.FINDINGS_RECEIVED
DeliveryAttempt = _state.DeliveryAttempt
DeliveryError = _state.DeliveryError
utc_now = _state.utc_now
for _state_name in (
    "APPROVAL_STATE",
    "HOST_CAPACITY_BLOCKED",
    "HOST_CHANNEL_UNREADABLE",
    "INTERRUPTED",
    "NON_DELIVERY_UNKNOWN",
    "RECOVERED_FROM_TRANSCRIPT",
    "RUNNING",
    "SPAWN_ACCEPTED",
    "SPAWN_ACCEPTED_NO_DELIVERY",
    "TIMED_OUT",
):
    globals()[_state_name] = getattr(_state, _state_name)

SCHEMA_VERSION = "charness.reviewer_delivery.v1"


@dataclass
class DeliveryLedger:
    attempts: dict[str, DeliveryAttempt] = field(default_factory=dict)

    @classmethod
    def empty(cls) -> "DeliveryLedger":
        return cls()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DeliveryLedger":
        if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
            raise DeliveryError(f"expected schema_version {SCHEMA_VERSION}")
        raw_attempts = payload.get("attempts")
        if not isinstance(raw_attempts, list):
            raise DeliveryError("ledger attempts must be a list")
        attempts: dict[str, DeliveryAttempt] = {}
        for raw in raw_attempts:
            attempt = DeliveryAttempt.from_dict(raw)
            if attempt.attempt_id in attempts:
                raise DeliveryError(f"duplicate attempt_id: {attempt.attempt_id}")
            attempts[attempt.attempt_id] = attempt
        return cls(attempts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "approval_rule": "only findings-received with matching provenance is approval-eligible",
            "attempts": [attempt.to_dict() for attempt in self.attempts.values()],
        }

    def start(
        self,
        *,
        scope: str,
        packet_identity: str,
        parent_receipt_identity: str,
        boundary_fingerprint: str,
        attempt_id: str | None = None,
        recorded_at: str | None = None,
    ) -> DeliveryAttempt:
        attempt = DeliveryAttempt.start(
            attempt_id=attempt_id,
            scope=scope,
            packet_identity=packet_identity,
            parent_receipt_identity=parent_receipt_identity,
            boundary_fingerprint=boundary_fingerprint,
            recorded_at=recorded_at or utc_now(),
        )
        if attempt.attempt_id in self.attempts:
            raise DeliveryError(f"attempt_id already exists: {attempt.attempt_id}")
        self.attempts[attempt.attempt_id] = attempt
        return attempt

    def require(self, attempt_id: str) -> DeliveryAttempt:
        for key, attempt in self.attempts.items():
            if key == attempt_id:
                return attempt
        raise DeliveryError(f"unknown attempt_id: {attempt_id}")

    def retry(
        self,
        attempt_id: str,
        *,
        new_attempt_id: str | None = None,
        recorded_at: str | None = None,
    ) -> DeliveryAttempt:
        old = self.require(attempt_id)
        if old.approval_eligible:
            raise DeliveryError("cannot retry an approval-eligible attempt")
        if old.retry_count >= 1:
            raise DeliveryError("recovery is bounded to one retry per delivery attempt")
        attempt = DeliveryAttempt.start(
            attempt_id=new_attempt_id,
            scope=old.scope,
            packet_identity=old.packet_identity,
            parent_receipt_identity=old.parent_receipt_identity,
            boundary_fingerprint=old.boundary_fingerprint,
            recorded_at=recorded_at or utc_now(),
            retry_of=old.attempt_id,
            retry_count=old.retry_count + 1,
        )
        if attempt.attempt_id in self.attempts:
            raise DeliveryError(f"attempt_id already exists: {attempt.attempt_id}")
        self.attempts[attempt.attempt_id] = attempt
        return attempt


def _read(path: Path) -> DeliveryLedger:
    if not path.exists():
        return DeliveryLedger.empty()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DeliveryError(f"cannot read ledger {path}: {exc}") from exc
    return DeliveryLedger.from_dict(payload)


def _write(path: Path, ledger: DeliveryLedger) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(ledger.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _emit(payload: dict[str, Any]) -> None:
    emit_yaml(payload)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record fail-closed bounded reviewer delivery state.")
    parser.add_argument("--ledger", required=True, help="JSON state packet path")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="record spawn acceptance")
    start.add_argument("--scope", required=True)
    start.add_argument("--packet-identity", required=True)
    start.add_argument("--parent-receipt-identity", required=True)
    start.add_argument("--boundary-fingerprint", required=True)
    start.add_argument("--attempt-id")
    start.add_argument("--recorded-at")

    transition = sub.add_parser("transition", help="record a canonical host observation")
    transition.add_argument("--attempt-id", required=True)
    transition.add_argument(
        "--state",
        choices=tuple(state for state in CANONICAL_STATES if state not in {"spawn-accepted", FINDINGS_RECEIVED}),
        required=True,
    )
    transition.add_argument("--signal", required=True)
    transition.add_argument("--recorded-at")

    findings = sub.add_parser("findings", help="record parent-context findings after provenance checks")
    findings.add_argument("--attempt-id", required=True)
    findings.add_argument("--scope", required=True)
    findings.add_argument("--packet-identity", required=True)
    findings.add_argument("--parent-receipt-identity", required=True)
    findings.add_argument("--findings-identity", required=True)
    findings.add_argument("--recorded-at")

    recovered = sub.add_parser("recover", help="record transcript recovery without approval")
    recovered.add_argument("--attempt-id", required=True)
    recovered.add_argument("--signal", required=True)
    recovered.add_argument("--recorded-at")

    retry = sub.add_parser("retry", help="start a new attempt without overwriting the original")
    retry.add_argument("--from-attempt", required=True)
    retry.add_argument("--attempt-id")
    retry.add_argument("--recorded-at")

    show = sub.add_parser("show", help="read the state packet")
    show.add_argument("--attempt-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    path = Path(args.ledger)
    try:
        ledger = _read(path)
        if args.command == "start":
            attempt = ledger.start(
                scope=args.scope,
                packet_identity=args.packet_identity,
                parent_receipt_identity=args.parent_receipt_identity,
                boundary_fingerprint=args.boundary_fingerprint,
                attempt_id=args.attempt_id,
                recorded_at=args.recorded_at,
            )
            _write(path, ledger)
            _emit({"ok": True, "attempt": attempt.to_dict(), "approval_eligible": False})
            return 0
        if args.command == "transition":
            attempt = ledger.require(args.attempt_id)
            attempt.transition(args.state, args.signal, args.recorded_at or utc_now())
            _write(path, ledger)
            _emit({"ok": True, "attempt": attempt.to_dict(), "approval_eligible": attempt.approval_eligible})
            return 0
        if args.command == "findings":
            attempt = ledger.require(args.attempt_id)
            accepted = attempt.record_findings(
                scope=args.scope,
                packet_identity=args.packet_identity,
                parent_receipt_identity=args.parent_receipt_identity,
                findings_identity=args.findings_identity,
                recorded_at=args.recorded_at or utc_now(),
            )
            _write(path, ledger)
            _emit({"ok": accepted, "attempt": attempt.to_dict(), "approval_eligible": attempt.approval_eligible})
            return 0 if accepted else 1
        if args.command == "recover":
            attempt = ledger.require(args.attempt_id)
            attempt.record_recovery(args.signal, args.recorded_at or utc_now())
            _write(path, ledger)
            _emit({"ok": True, "attempt": attempt.to_dict(), "approval_eligible": False})
            return 0
        if args.command == "retry":
            attempt = ledger.retry(args.from_attempt, new_attempt_id=args.attempt_id, recorded_at=args.recorded_at)
            _write(path, ledger)
            _emit({"ok": True, "attempt": attempt.to_dict(), "approval_eligible": False})
            return 0
        if args.command == "show":
            if args.attempt_id:
                attempt = ledger.require(args.attempt_id)
                _emit({"ok": True, "attempt": attempt.to_dict(), "approval_eligible": attempt.approval_eligible})
            else:
                _emit({"ok": True, "ledger": ledger.to_dict()})
            return 0
        raise DeliveryError(f"unsupported command: {args.command}")
    except DeliveryError as exc:
        _emit({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
