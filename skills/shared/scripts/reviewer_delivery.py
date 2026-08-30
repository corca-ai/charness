#!/usr/bin/env python3
"""CLI and durable persistence for the reviewer delivery state machine."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from contextlib import contextmanager
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
    "COLLECTION_FAILED",
    "INTERRUPTED",
    "NON_DELIVERY_UNKNOWN",
    "PARTIAL",
    "RECOVERED_FROM_TRANSCRIPT",
    "RUNNING",
    "SPAWN_ACCEPTED",
    "SPAWN_ACCEPTED_NO_DELIVERY",
    "TIMED_OUT",
):
    globals()[_state_name] = getattr(_state, _state_name)

SCHEMA_VERSION = "charness.reviewer_delivery.v1"
LEDGER_LOCK_TIMEOUT_SECONDS = 5.0


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
        ordered = list(attempts.values())
        for index, attempt in enumerate(ordered):
            if attempt.retry_of is None:
                if attempt.retry_count != 0:
                    raise DeliveryError(
                        f"attempt `{attempt.attempt_id}` has retry_count without retry_of"
                    )
                continue
            predecessor = attempts.get(attempt.retry_of)
            if predecessor is None:
                raise DeliveryError(
                    f"attempt `{attempt.attempt_id}` retry_of must reference an existing attempt"
                )
            if index == 0 or ordered[index - 1].attempt_id != predecessor.attempt_id:
                raise DeliveryError(
                    f"attempt `{attempt.attempt_id}` retry_of must reference its immediate predecessor"
                )
            if predecessor.state not in _state.RETRYABLE_STATES or not predecessor.terminal:
                raise DeliveryError(
                    f"attempt `{attempt.attempt_id}` predecessor `{predecessor.attempt_id}` is not terminal retryable"
                )
            if attempt.retry_count != predecessor.retry_count + 1:
                raise DeliveryError(
                    f"attempt `{attempt.attempt_id}` retry_count is incoherent with predecessor"
                )
            if attempt.retry_count > 1:
                raise DeliveryError("recovery is bounded to one retry per delivery attempt")
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
        boundary_fingerprint: str | None = None,
        boundary_mode: str | None = None,
        reviewed_input_identity: str | None = None,
        execution_mode: str | None = None,
        backend: str | None = None,
        prompt_sha256: str | None = None,
        schema_sha256: str | None = None,
        capability_launch_envelope_sha256: str | None = None,
        output_file: str | None = None,
        receipt_file: str | None = None,
        producer_run_id: str | None = None,
        attempt_id: str | None = None,
        recorded_at: str | None = None,
    ) -> DeliveryAttempt:
        attempt = DeliveryAttempt.start(
            attempt_id=attempt_id,
            scope=scope,
            packet_identity=packet_identity,
            parent_receipt_identity=parent_receipt_identity,
            boundary_fingerprint=boundary_fingerprint,
            boundary_mode=boundary_mode,
            reviewed_input_identity=reviewed_input_identity,
            execution_mode=execution_mode,
            backend=backend,
            prompt_sha256=prompt_sha256,
            schema_sha256=schema_sha256,
            capability_launch_envelope_sha256=capability_launch_envelope_sha256,
            output_file=output_file,
            receipt_file=receipt_file,
            producer_run_id=producer_run_id,
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
        if old.retry_count >= 1:
            raise DeliveryError(
                "recovery is bounded to one retry per delivery attempt; "
                "the retry predecessor must remain terminal retryable"
            )
        if old.state not in _state.RETRYABLE_STATES or not old.terminal:
            raise DeliveryError(
                f"cannot retry active or non-retryable attempt `{old.attempt_id}`; "
                "retry requires a terminal retryable state"
            )
        ordered_ids = list(self.attempts)
        if not ordered_ids or ordered_ids[-1] != old.attempt_id:
            raise DeliveryError("retry predecessor must be the immediate predecessor in the ledger")
        attempt = DeliveryAttempt.start(
            attempt_id=new_attempt_id,
            scope=old.scope,
            packet_identity=old.packet_identity,
            parent_receipt_identity=old.parent_receipt_identity,
            boundary_fingerprint=old.boundary_fingerprint,
            boundary_mode=old.boundary_mode,
            reviewed_input_identity=old.reviewed_input_identity,
            execution_mode=old.execution_mode,
            backend=old.backend,
            prompt_sha256=old.prompt_sha256,
            schema_sha256=old.schema_sha256,
            capability_launch_envelope_sha256=old.capability_launch_envelope_sha256,
            output_file=None,
            receipt_file=None,
            producer_run_id=None,
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


@contextmanager
def ledger_lock(path: Path):
    """Serialize ledger read-modify-write operations with a bounded wait."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    started = time.monotonic()
    with lock_path.open("a+b") as handle:
        handle.seek(0)
        if not handle.read(1):
            handle.seek(0)
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        while True:
            try:
                if os.name == "posix":
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                else:
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except (BlockingIOError, OSError) as exc:
                if time.monotonic() - started >= LEDGER_LOCK_TIMEOUT_SECONDS:
                    raise DeliveryError(f"timed out acquiring ledger lock: {lock_path}") from exc
                time.sleep(0.01)
        try:
            yield
        finally:
            if os.name == "posix":
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            else:
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


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
    start.add_argument("--boundary-fingerprint")
    start.add_argument("--boundary-mode", choices=("read-only-worker", "shared-tree-fingerprint"))
    start.add_argument("--reviewed-input-identity")
    start.add_argument("--execution-mode", choices=("file-backed-worker", "typed-subagent"))
    start.add_argument("--backend")
    start.add_argument("--prompt-sha256")
    start.add_argument("--schema-sha256")
    start.add_argument("--capability-launch-envelope-sha256")
    start.add_argument("--attempt-id")
    start.add_argument("--recorded-at")

    transition = sub.add_parser("transition", help="record a canonical host observation")
    transition.add_argument("--attempt-id", required=True)
    transition.add_argument(
        "--state",
        choices=tuple(state for state in CANONICAL_STATES if state not in {"spawn-accepted", "partial", FINDINGS_RECEIVED}),
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
        with ledger_lock(path):
            ledger = _read(path)
            if args.command == "start":
                attempt = ledger.start(
                    scope=args.scope,
                    packet_identity=args.packet_identity,
                    parent_receipt_identity=args.parent_receipt_identity,
                    boundary_fingerprint=args.boundary_fingerprint,
                    boundary_mode=args.boundary_mode,
                    reviewed_input_identity=args.reviewed_input_identity,
                    execution_mode=args.execution_mode,
                    backend=args.backend,
                    prompt_sha256=args.prompt_sha256,
                    schema_sha256=args.schema_sha256,
                    capability_launch_envelope_sha256=args.capability_launch_envelope_sha256,
                    attempt_id=args.attempt_id,
                    recorded_at=args.recorded_at,
                )
                _write(path, ledger)
                payload = {"ok": True, "attempt": attempt.to_dict(), "delivery_complete": False}
            elif args.command == "transition":
                attempt = ledger.require(args.attempt_id)
                attempt.transition(args.state, args.signal, args.recorded_at or utc_now())
                _write(path, ledger)
                payload = {"ok": True, "attempt": attempt.to_dict(), "delivery_complete": attempt.delivery_complete}
            elif args.command == "findings":
                attempt = ledger.require(args.attempt_id)
                accepted = attempt.record_findings(
                    scope=args.scope,
                    packet_identity=args.packet_identity,
                    parent_receipt_identity=args.parent_receipt_identity,
                    findings_identity=args.findings_identity,
                    recorded_at=args.recorded_at or utc_now(),
                )
                _write(path, ledger)
                payload = {"ok": accepted, "attempt": attempt.to_dict(), "delivery_complete": attempt.delivery_complete}
            elif args.command == "recover":
                attempt = ledger.require(args.attempt_id)
                attempt.record_recovery(args.signal, args.recorded_at or utc_now())
                _write(path, ledger)
                payload = {"ok": True, "attempt": attempt.to_dict(), "delivery_complete": False}
            elif args.command == "retry":
                attempt = ledger.retry(args.from_attempt, new_attempt_id=args.attempt_id, recorded_at=args.recorded_at)
                _write(path, ledger)
                payload = {"ok": True, "attempt": attempt.to_dict(), "delivery_complete": False}
            elif args.command == "show":
                if args.attempt_id:
                    attempt = ledger.require(args.attempt_id)
                    payload = {"ok": True, "attempt": attempt.to_dict(), "delivery_complete": attempt.delivery_complete}
                else:
                    payload = {"ok": True, "ledger": ledger.to_dict()}
            else:
                raise DeliveryError(f"unsupported command: {args.command}")
        _emit(payload)
        if args.command == "findings" and not payload["ok"]:
            return 1
        return 0
    except DeliveryError as exc:
        _emit({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
