"""Canonical semantic contract for a bounded fresh-eye result.

Delivery metadata proves that bytes arrived. This module proves what those
bytes mean: the result is the repository-owned bounded-review document, its
packet/input identities match the delivery request, and only ``verdict: pass``
can be consumed as reviewer approval.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReviewerResultError(ValueError):
    """A result cannot support a bounded-review approval claim."""


class ReviewerCoverageError(ReviewerResultError):
    """A schema-valid result does not cover its declared target set.

    Kept distinct from a schema failure on purpose: the runner must tell
    "the model/tool failed", "the JSON shape is wrong", and "the shape is
    right but admitted inputs went unobserved" apart instead of merging all
    three into one unverified outcome.
    """


def canonical_schema_path() -> Path:
    here = Path(__file__).resolve()
    for ancestor in (here.parent, *here.parents):
        for candidate in (
            ancestor / "references" / "bounded-review-result.schema.json",
            ancestor / "shared" / "references" / "bounded-review-result.schema.json",
            ancestor / "skills" / "shared" / "references" / "bounded-review-result.schema.json",
        ):
            if candidate.is_file():
                return candidate
    raise ReviewerResultError("canonical bounded-review result schema is unavailable")


#: Capability provenance the RUNNER joins from the launch envelope, never the
#: model. Named here because the canonical schema and the model-facing projection
#: must not disagree about which fields those are; deriving the projection from
#: this one tuple is what keeps a field added to the schema from silently landing
#: back on the model.
RUNNER_JOINED_FIELDS = ("capability_non_claims", "capability_non_claims_sha256")


def bounded_result_shape(payload: dict[str, Any]) -> str:
    """Classify reusable result shape without confusing model and runner fields.

    The generation-facing schema intentionally omits ``RUNNER_JOINED_FIELDS``;
    the runner adds them before an approval consumer validates the canonical
    result.  A model-shaped result is therefore useful retry evidence, not a
    malformed partial result.  Only missing semantic/model-authored fields are
    genuinely partial.
    """
    schema = json.loads(canonical_schema_path().read_text(encoding="utf-8"))
    required = frozenset(schema.get("required", ()))
    model_required = required - frozenset(RUNNER_JOINED_FIELDS)
    if not model_required <= payload.keys():
        return "partial-schema"
    if required <= payload.keys():
        return "canonical-shaped"
    return "model-shaped"


def model_authored_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Project the canonical schema down to what a reviewer model may author (#755).

    The canonical schema requires the model to emit a capability non-claim list
    whose every entry carries its own SHA-256, plus a canonical digest over the
    whole list. A language model cannot compute either, and the generated prompt
    said only "return JSON matching this schema" -- so the backend was handed a
    contract it had no way to satisfy, and three substantive reviews died on it.

    Removing the fields from the GENERATION contract is what stops the model from
    being asked. The delivered result is still validated against the canonical
    schema after the runner joins them, so nothing about the final artifact's
    shape is relaxed.
    """
    projected = dict(schema)
    projected["properties"] = {
        name: value
        for name, value in schema.get("properties", {}).items()
        if name not in RUNNER_JOINED_FIELDS
    }
    # Strict generation requires every property. Optional semantic fields use
    # nullable types in the canonical schema; omission stays valid for historical
    # delivered results, while the model emits null for an inapplicable field.
    projected["required"] = list(projected["properties"])
    return projected


def write_model_authored_schema(schema: dict[str, Any], path: Path) -> Path:
    """Materialize the generation-facing projection and return its path.

    The backend generates against this file, never the canonical schema: the
    canonical one requires two digests no language model can compute. The worker
    receipt still records the CANONICAL schema's identity, because that is the
    contract the delivered result is validated against -- the projection relaxes
    what is asked of the model, not what the artifact must be.
    """
    path.write_text(
        json.dumps(model_authored_schema(schema), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _read_result(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewerResultError(f"worker result is not readable JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReviewerResultError("worker result must be a JSON object")
    return payload


def _normalize_expected_targets(expected_targets: Any) -> set[str]:
    """Validate an author-declared coverage set without naming any workflow's items.

    The runner never embeds item names: the author derives the set from the
    admitted inputs (for example a packet's prepared targets) and the contract
    only enforces set coverage. A malformed declaration is the author's
    programming error, so it raises the schema-class error, never the
    coverage-class one reserved for result shortfalls.
    """
    if not isinstance(expected_targets, (list, tuple)) or not expected_targets:
        raise ReviewerResultError("expected target set must be a nonempty list of strings")
    declared: set[str] = set()
    for target in expected_targets:
        if not isinstance(target, str) or not target.strip():
            raise ReviewerResultError("expected targets must be nonempty strings")
        if target in declared:
            raise ReviewerResultError(f"expected target set contains a duplicate: {target!r}")
        declared.add(target)
    return declared


def _require_target_coverage(payload: dict[str, Any], *, expected: set[str]) -> None:
    """Refuse a schema-valid result that leaves declared targets unobserved.

    Coverage is verdict-agnostic on purpose: a ``block`` verdict that observes
    every target is still a delivered finding, while a ``pass`` that observes
    none of them is a dummy. ``target_observations: null`` stays valid only
    when no targets are declared, which keeps legitimate finding-free and
    target-free results passing.
    """
    observations = payload.get("target_observations")
    if observations is None:
        raise ReviewerCoverageError(
            f"worker result observes none of the {len(expected)} expected targets"
        )
    if not isinstance(observations, list):
        raise ReviewerCoverageError("worker result target_observations must be an array")
    by_target: dict[str, list[dict[str, Any]]] = {}
    for entry in observations:
        if not isinstance(entry, dict) or not isinstance(entry.get("target"), str):
            raise ReviewerCoverageError("target observations must name string targets")
        by_target.setdefault(entry["target"], []).append(entry)
    missing = sorted(expected - set(by_target))
    if missing:
        raise ReviewerCoverageError(
            f"worker result does not observe expected targets: {missing!r}"
        )
    for target in sorted(expected):
        entries = by_target[target]
        if len(entries) != 1:
            raise ReviewerCoverageError(
                f"target {target!r} has {len(entries)} observations, want exactly one"
            )
        entry = entries[0]
        summary = entry.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise ReviewerCoverageError(
                f"target {target!r} observation needs a nonempty summary"
            )
        evidence = entry.get("evidence")
        if (
            not isinstance(evidence, list)
            or not evidence
            or not all(isinstance(item, str) and item.strip() for item in evidence)
        ):
            raise ReviewerCoverageError(
                f"target {target!r} observation needs a nonempty evidence array"
            )


def validate_bounded_result(
    path: Path,
    *,
    packet_identity: str,
    reviewed_input_identity: str,
    require_pass: bool,
    expected_targets: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Validate the canonical result and optionally require a passing verdict.

    ``expected_targets`` is the opt-in declarative coverage floor: when the
    author declares the admitted target set, a schema-valid result must
    observe every member or validation raises ``ReviewerCoverageError``.
    ``None`` (the default) preserves the historical shape-only behavior for
    target-free packets, so legitimate aggregation and finding-free results
    keep passing.
    """
    payload = _read_result(path)
    try:
        import jsonschema

        schema = json.loads(canonical_schema_path().read_text(encoding="utf-8"))
        jsonschema.validators.validator_for(schema)(schema).validate(payload)
    except ReviewerResultError:
        raise
    except Exception as exc:
        raise ReviewerResultError(f"worker result failed canonical schema validation: {exc}") from exc
    if payload.get("packet_sha256") != packet_identity:
        raise ReviewerResultError("worker result packet_sha256 does not match the delivery request")
    if payload.get("reviewed_input_identity_sha256") != reviewed_input_identity:
        raise ReviewerResultError(
            "worker result reviewed_input_identity_sha256 does not match the delivery request"
        )
    if expected_targets is not None:
        _require_target_coverage(payload, expected=_normalize_expected_targets(expected_targets))
    if require_pass and payload.get("verdict") != "pass":
        raise ReviewerResultError(
            f"worker reviewer verdict is not approval-eligible: {payload.get('verdict')!r}"
        )
    return payload
