#!/usr/bin/env python3
"""Compute a stable, bounded retry decision for a verification claim.

This helper does not run a gate and does not decide whether a claim is true. It
only makes the retry question explicit: the same subject, verifier, input, and
stable failure with no new evidence is ``stop-no-progress``. Keeping this
separate from the gate avoids turning every retry decision into another broad
verification pass.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass

IDENTITY_PREFIX = "sha256:"
FAILURE_PREFIX = "stable:"
NONE = "none"
_FAILURE_CODE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def _normalized(value: str) -> str:
    normalized = " ".join(value.strip().split())
    if not normalized:
        raise ValueError("identity values must not be empty")
    return normalized


def canonical_identity(value: str) -> str:
    """Return a stable identity, preserving an already-qualified digest."""

    normalized = _normalized(value).lower()
    if normalized.startswith(IDENTITY_PREFIX):
        if not _DIGEST.fullmatch(normalized):
            raise ValueError("sha256 identity must contain exactly 64 lowercase hex characters")
        return normalized
    return f"{IDENTITY_PREFIX}{hashlib.sha256(normalized.encode('utf-8')).hexdigest()}"


def canonical_failure_code(value: str) -> str:
    """Require a stable code instead of accepting changing log prose."""

    normalized = _normalized(value).lower()
    if normalized.startswith(FAILURE_PREFIX):
        normalized = normalized.removeprefix(FAILURE_PREFIX)
    if not _FAILURE_CODE.fullmatch(normalized):
        raise ValueError("failure code must be a stable lowercase slug, not log prose")
    return f"{FAILURE_PREFIX}{normalized}"


def evidence_identity(value: str | None) -> str:
    if value is None or value.strip().lower() == NONE:
        return NONE
    return canonical_identity(value)


def build_retry_key(*, subject: str, verifier: str, input_identity: str, failure: str) -> str:
    parts = (
        canonical_identity(subject),
        canonical_identity(verifier),
        canonical_identity(input_identity),
        canonical_failure_code(failure),
    )
    payload = "\0".join(parts).encode("utf-8")
    return f"{IDENTITY_PREFIX}{hashlib.sha256(payload).hexdigest()}"


@dataclass(frozen=True)
class RetryDecision:
    disposition: str
    reason: str


def decide_retry(
    *,
    current_key: str,
    current_evidence: str,
    previous_key: str | None = None,
    previous_evidence: str = NONE,
) -> RetryDecision:
    """Classify one attempt without treating log churn as new evidence."""

    if not _DIGEST.fullmatch(current_key):
        raise ValueError("current retry key must be a sha256 digest")
    if previous_key is None:
        return RetryDecision("first-attempt", "no previous attempt for this claim")
    if not _DIGEST.fullmatch(previous_key):
        raise ValueError("previous retry key must be a sha256 digest")
    current_evidence = evidence_identity(current_evidence)
    previous_evidence = evidence_identity(previous_evidence)
    if current_key != previous_key:
        return RetryDecision("retry-new-identity", "subject, verifier, input, or stable failure changed")
    if current_evidence != NONE and current_evidence != previous_evidence:
        return RetryDecision("retry-new-evidence", "the same claim has a different evidence identity")
    return RetryDecision("stop-no-progress", "same claim and stable failure have no new evidence")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--verifier", required=True)
    parser.add_argument("--input", dest="input_identity", required=True)
    parser.add_argument("--failure-code", required=True)
    parser.add_argument("--evidence", default=NONE)
    parser.add_argument("--previous-key")
    parser.add_argument("--previous-evidence", default=NONE)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        key = build_retry_key(
            subject=args.subject,
            verifier=args.verifier,
            input_identity=args.input_identity,
            failure=args.failure_code,
        )
        current_evidence = evidence_identity(args.evidence)
        decision = decide_retry(
            current_key=key,
            current_evidence=current_evidence,
            previous_key=args.previous_key,
            previous_evidence=args.previous_evidence,
        )
    except ValueError as error:
        print(f"error: {error}")
        return 2
    print(f"retry_key: {key}")
    print(f"evidence_identity: {current_evidence}")
    print(f"retry_disposition: {decision.disposition}")
    print(f"reason: {decision.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
