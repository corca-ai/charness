"""Capability lifecycle owned by the portable reviewer worker.

This module owns launch loading/refusal, collection revalidation, result
non-claim checks, capability-failure adaptation, and worker receipt capability
fields. Canonical envelope semantics stay in the reviewer_capability module; the
generic runtime consumes the typed state and does not decide capability
meaning. Its blind class is host behavior that never enters the structured
envelope, which remains unprovable rather than inferred from backend output.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from reviewer_capability import (
        CapabilityError,
        collect_capability_file,
        envelope_sha256,
        join_result_capability_non_claims,
        load_capability_file,
        receipt_capability_fields,
        validate_result_capability_non_claims,
    )
except ImportError:
    from skills.shared.scripts.reviewer_capability import (
        CapabilityError,
        collect_capability_file,
        envelope_sha256,
        join_result_capability_non_claims,
        load_capability_file,
        receipt_capability_fields,
        validate_result_capability_non_claims,
    )


@dataclass(frozen=True)
class WorkerCapability:
    """The capability fields carried across one worker attempt."""

    payload: dict[str, Any]
    status: str
    launch_envelope_sha256: str
    collection_envelope_sha256: str


class CapabilityLifecycleError(ValueError):
    """A typed capability failure crossing into the generic worker runtime."""

    def __init__(
        self,
        status: str,
        message: str,
        *,
        payload: dict[str, Any] | None = None,
        adapt_capability: bool = False,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.payload = payload
        self.adapt_capability = adapt_capability


def _translate(
    error: CapabilityError,
    *,
    adapt_capability: bool = False,
    message_prefix: str = "",
) -> CapabilityLifecycleError:
    return CapabilityLifecycleError(
        error.status,
        f"{message_prefix}{error}",
        payload=error.payload,
        adapt_capability=adapt_capability,
    )


def launch(path: str | Path, *, attempt_id: str) -> WorkerCapability:
    """Load the required ready envelope before a backend process starts."""
    try:
        decision = load_capability_file(path, attempt_id=attempt_id, require_ready=True)
    except CapabilityError as exc:
        raise _translate(exc) from exc
    return WorkerCapability(
        payload=decision.payload,
        status=decision.status,
        launch_envelope_sha256=decision.envelope_sha256,
        collection_envelope_sha256=decision.envelope_sha256,
    )


def collect(
    state: WorkerCapability,
    path: str | Path,
    *,
    attempt_id: str,
) -> WorkerCapability:
    """Revalidate collection against the exact launch envelope identity."""
    try:
        decision = collect_capability_file(
            path,
            attempt_id=attempt_id,
            launch_envelope_sha256=state.launch_envelope_sha256,
        )
    except CapabilityError as exc:
        raise _translate(exc, adapt_capability=True, message_prefix="capability collection is not ready: ") from exc
    return WorkerCapability(
        payload=decision.payload,
        status=decision.status,
        launch_envelope_sha256=state.launch_envelope_sha256,
        collection_envelope_sha256=decision.envelope_sha256,
    )


def join_result_non_claims(result: dict[str, Any], state: WorkerCapability) -> dict[str, Any]:
    """Join launch-bound capability provenance into a model-authored result (#755)."""
    return join_result_capability_non_claims(result, state.payload)


def validate_result_non_claims(result: dict[str, Any], state: WorkerCapability) -> None:
    """Require the result to repeat the exact launch-bound non-claim records."""
    try:
        validate_result_capability_non_claims(result, state.payload)
    except CapabilityError as exc:
        raise CapabilityLifecycleError(
            "schema-invalid",
            f"worker result capability non-claims are invalid: {exc}",
        ) from exc


def adapt_failure(state: WorkerCapability, error: CapabilityLifecycleError) -> WorkerCapability:
    """Preserve the launch identity while recording the failed collection view."""
    payload = error.payload or state.payload
    return WorkerCapability(
        payload=payload,
        status=error.status,
        launch_envelope_sha256=state.launch_envelope_sha256,
        collection_envelope_sha256=envelope_sha256(payload),
    )


def receipt_fields(state: WorkerCapability) -> dict[str, Any]:
    """Assemble worker fields through the canonical envelope owner."""
    return receipt_capability_fields(
        state.payload,
        state.status,
        launch_envelope_sha256=state.launch_envelope_sha256,
        collection_envelope_sha256=state.collection_envelope_sha256,
    )


def failure_receipt_fields(payload: dict[str, Any], status: str) -> dict[str, Any]:
    """Assemble capability fields for a refusal before launch state exists."""
    return receipt_capability_fields(payload, status)
