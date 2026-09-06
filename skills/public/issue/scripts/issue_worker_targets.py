"""Issue-owned exact membership policy for verified worker evidence."""

from __future__ import annotations

import re
from typing import Any


class WorkerTargetError(ValueError):
    """A verified carrier does not cover the requested issue target set."""


# Shared by the issue-owned launch path and the final issue consumer.  The
# prefix is deliberately still required by the consumer: target membership and
# passing observations do not prove that a review was a resolution review.
ISSUE_RESOLUTION_SCOPE_PREFIX = "issue-resolution"


def _normalize_worker_target(value: object) -> str:
    """Normalize one owner/repo#N target at the issue-owned boundary."""
    if not isinstance(value, str):
        raise WorkerTargetError("worker target must be a string")
    match = re.fullmatch(r"(?P<repo>[^/\s]+/[^#\s]+)#(?P<number>[0-9]+)", value.strip())
    if match is None:
        raise WorkerTargetError(
            f"worker target is not a qualified owner/repo#N identity: {value!r}"
        )
    repository = match.group("repo").lower()
    return f"{repository}#{int(match.group('number'))}"


def _exact_worker_targets(
    values: object,
    *,
    expected_issue_numbers: list[int],
    expected_repository: str,
    label: str,
) -> set[str]:
    if not isinstance(values, list) or not values:
        raise WorkerTargetError(f"{label} must be a nonempty array")
    raw_targets: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise WorkerTargetError(f"{label} targets must be strings")
        if value in raw_targets:
            raise WorkerTargetError(f"{label} contains duplicate targets")
        raw_targets.append(value)
    normalized = {
        _normalize_worker_target(value)
        for value in values
    }
    expected = {
        f"{expected_repository.strip().lower()}#{number}" for number in expected_issue_numbers
    }
    if len(values) != len(expected):
        raise WorkerTargetError(
            f"{label} cardinality does not match the invoked target set"
        )
    if normalized != expected:
        raise WorkerTargetError(
            f"{label} does not exactly match the invoked target set"
        )
    return normalized


def validate_worker_target_membership(
    *,
    packet: dict[str, Any] | None,
    result: dict[str, Any] | None,
    expected_issue_numbers: list[int] | None,
    expected_repository: str | None,
) -> None:
    """Apply issue-owned legacy/structured membership and observation floors."""
    if not isinstance(packet, dict) or not isinstance(result, dict):
        raise WorkerTargetError("worker carrier did not return packet and result payloads")
    numbers = list(expected_issue_numbers or [])
    repository = (expected_repository or "").strip()
    if not numbers or not repository:
        raise WorkerTargetError("issue target membership requires repository and issue numbers")
    prepared_present = "prepared_targets" in packet
    observations_present = result.get("target_observations") is not None
    if prepared_present != observations_present:
        raise WorkerTargetError(
            "structured packet targets and result target observations must appear together"
        )
    if not prepared_present:
        if len(numbers) != 1:
            raise WorkerTargetError(
                "legacy worker carriers bind only one issue target"
            )
        expected = f"{repository.lower()}#{numbers[0]}"
        prepared_for = str(packet.get("prepared_for", "")).strip().lower()
        if not prepared_for.startswith(expected) or (
            len(prepared_for) > len(expected) and prepared_for[len(expected)].isalnum()
        ):
            raise WorkerTargetError(
                f"reviewed packet prepared_for does not bind exactly to {expected}"
            )
        packet_repository = str(packet.get("repo", "")).strip().lower()
        accepted = {repository.lower(), repository.lower().rsplit("/", 1)[-1]}
        if packet_repository not in accepted:
            raise WorkerTargetError(
                f"reviewed packet repo does not bind exactly to {repository}"
            )
        return

    _exact_worker_targets(
        packet.get("prepared_targets"),
        expected_issue_numbers=numbers,
        expected_repository=repository,
        label="prepared_targets",
    )
    observations = result.get("target_observations")
    if not isinstance(observations, list) or not observations:
        raise WorkerTargetError("target_observations must be a nonempty array")
    observation_targets: list[object] = []
    for observation in observations:
        if not isinstance(observation, dict):
            raise WorkerTargetError("target_observations entries must be objects")
        observation_targets.append(observation.get("target"))
        if observation.get("verdict") != "pass":
            raise WorkerTargetError(
                "every target observation must have a passing verdict"
            )
        if not isinstance(observation.get("summary"), str) or not observation["summary"].strip():
            raise WorkerTargetError("target observations require a nonempty summary")
        evidence = observation.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(item, str) and item.strip() for item in evidence
        ):
            raise WorkerTargetError(
                "target observations require a nonempty evidence array"
            )
    _exact_worker_targets(
        observation_targets,
        expected_issue_numbers=numbers,
        expected_repository=repository,
        label="target_observations",
    )
