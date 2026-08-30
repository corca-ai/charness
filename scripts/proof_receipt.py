#!/usr/bin/env python3
"""Semantic receipts for the terminal quality verdict.

The producers retain their domain-specific status vocabularies.  This module
owns the facts that a reader needs to act on a terminal proof: scope, adverse
subjects, recovery evidence, cause, and the actual entrypoint exit code.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

QUALITY_STATUSES = {"pass", "fail", "unestablished"}
RECOVERY_STATUSES = {"available", "unavailable", "not-applicable"}


class ReceiptContractError(ValueError):
    """Raised when a producer cannot provide an honest receipt."""


@dataclass(frozen=True)
class RecoveryEvidence:
    status: str
    path: str | None = None
    reason: str | None = None

    def as_dict(self) -> dict[str, str]:
        result = {"status": self.status}
        if self.path is not None:
            result["path"] = self.path
        if self.reason is not None:
            result["reason"] = self.reason
        return result


@dataclass(frozen=True)
class AdverseSubject:
    subject: str
    recovery: RecoveryEvidence

    def as_dict(self) -> dict[str, object]:
        return {"subject": self.subject, "recovery": self.recovery.as_dict()}


@dataclass(frozen=True)
class ProofReceipt:
    surface: str
    status: str
    measured_scope: tuple[str, ...]
    adverse_subjects: tuple[AdverseSubject, ...]
    unproven_subjects: tuple[str, ...]
    cause: str | None
    effective_exit_code: int
    details: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "surface": self.surface,
            "status": self.status,
            "measured_scope": list(self.measured_scope),
            "adverse_subjects": [subject.as_dict() for subject in self.adverse_subjects],
            "unproven_subjects": list(self.unproven_subjects),
            "cause": self.cause,
            "effective_exit_code": self.effective_exit_code,
            "details": self.details,
        }


def _scope(values: Iterable[object]) -> tuple[str, ...]:
    return tuple(str(value) for value in values if str(value))


def _recovery(status: str, *, path: str | None = None, reason: str | None = None) -> RecoveryEvidence:
    if status not in RECOVERY_STATUSES:
        raise ReceiptContractError(f"unknown recovery status: {status}")
    if status == "available" and not path:
        raise ReceiptContractError("available recovery requires a path")
    if status != "available" and path is not None:
        raise ReceiptContractError(f"{status} recovery must not advertise a path")
    if status == "unavailable" and not reason:
        raise ReceiptContractError("unavailable recovery requires a reason")
    return RecoveryEvidence(status=status, path=path, reason=reason)


def _adverse(
    subjects: Iterable[str], recoveries: Iterable[RecoveryEvidence]
) -> tuple[AdverseSubject, ...]:
    subject_values = tuple(str(subject) for subject in subjects)
    recovery_values = tuple(recoveries)
    if len(subject_values) != len(recovery_values):
        raise ReceiptContractError("each adverse subject must have one recovery disposition")
    return tuple(
        AdverseSubject(subject=subject, recovery=recovery)
        for subject, recovery in zip(subject_values, recovery_values)
    )


def quality_receipt(
    *,
    status: str,
    measured_scope: Iterable[object],
    adverse_subjects: Iterable[str] = (),
    recoveries: Iterable[RecoveryEvidence] = (),
    unproven_subjects: Iterable[object] = (),
    effective_exit_code: int,
    details: dict[str, object] | None = None,
) -> ProofReceipt:
    if status not in QUALITY_STATUSES:
        raise ReceiptContractError(f"unknown quality status: {status}")
    adverse = _adverse(adverse_subjects, recoveries)
    return ProofReceipt(
        surface="quality",
        status=status,
        measured_scope=_scope(measured_scope),
        adverse_subjects=adverse,
        unproven_subjects=_scope(unproven_subjects),
        cause=("selected scope was not fully established" if status == "unestablished" else None),
        effective_exit_code=int(effective_exit_code),
        details=dict(details or {}),
    )


def _quality_adverse_text(subject: AdverseSubject) -> str:
    recovery = subject.recovery
    if recovery.status == "available":
        return f"{subject.subject} [log: {recovery.path}]"
    if recovery.status == "unavailable":
        return f"{subject.subject} [log unavailable]"
    return subject.subject


def render_quality_summary(receipt: ProofReceipt) -> str:
    passed = receipt.details.get("passed", 0)
    failed = receipt.details.get("failed", 0)
    elapsed = receipt.details.get("elapsed", "0ms")
    failed_note = ""
    if receipt.adverse_subjects:
        failed_note = " (FAILED: " + "; ".join(_quality_adverse_text(subject) for subject in receipt.adverse_subjects) + ")"
    if receipt.unproven_subjects:
        unproven = " ".join(receipt.unproven_subjects)
        unproven_note = f" (UNPROVEN: {unproven})" if unproven else " (UNPROVEN)"
        return (
            f"Quality summary: {passed} passed, {failed} failed{failed_note}, "
            f"{len(receipt.unproven_subjects)} UNPROVEN{unproven_note} "
            f"(ran; established nothing, or only part of its scope), total {elapsed}"
        )
    return f"Quality summary: {passed} passed, {failed} failed{failed_note}, total {elapsed}"


def write_receipt_json(receipt: ProofReceipt, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt.as_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _parse_recovery_spec(spec: str) -> RecoveryEvidence:
    status, separator, value = spec.partition(":")
    if not separator:
        return _recovery(status)
    if status == "available":
        return _recovery(status, path=value)
    return _recovery(status, reason=value)


def _quality_cli(args: argparse.Namespace) -> int:
    recoveries = [_parse_recovery_spec(spec) for spec in args.recovery]
    receipt = quality_receipt(
        status=args.status,
        measured_scope=args.measured_scope,
        adverse_subjects=args.adverse_subject,
        recoveries=recoveries,
        unproven_subjects=args.unproven_subject,
        effective_exit_code=args.effective_exit_code,
        details={
            "passed": args.passed,
            "failed": args.failed,
            "elapsed": args.elapsed,
            "execution_mode": args.execution_mode,
            "release": args.release,
            "full_queue": args.full_queue,
            "non_claim": args.non_claim,
        },
    )
    write_failed = False
    if args.json_path:
        try:
            write_receipt_json(receipt, args.json_path)
        except OSError as exc:
            print(f"proof receipt: could not write {args.json_path}: {exc}", file=sys.stderr)
            write_failed = True
    print(render_quality_summary(receipt))
    return 1 if write_failed else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="surface", required=True)
    quality = subparsers.add_parser("quality")
    quality.add_argument("--status", choices=sorted(QUALITY_STATUSES), required=True)
    quality.add_argument("--effective-exit-code", type=int, required=True)
    quality.add_argument("--passed", type=int, required=True)
    quality.add_argument("--failed", type=int, required=True)
    quality.add_argument("--elapsed", required=True)
    quality.add_argument("--execution-mode", choices=("full", "read-only"), required=True)
    quality.add_argument("--release", action="store_true")
    quality.add_argument("--full-queue", action="store_true")
    quality.add_argument("--non-claim", default="")
    quality.add_argument("--measured-scope", action="append", default=[])
    quality.add_argument("--adverse-subject", action="append", default=[])
    quality.add_argument("--recovery", action="append", default=[])
    quality.add_argument("--unproven-subject", action="append", default=[])
    quality.add_argument("--json-path")
    quality.set_defaults(handler=_quality_cli)
    return parser


def main() -> int:
    args = _parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
