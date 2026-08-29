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
    projected["required"] = [
        field for field in schema.get("required", []) if field not in RUNNER_JOINED_FIELDS
    ]
    projected["properties"] = {
        name: value
        for name, value in schema.get("properties", {}).items()
        if name not in RUNNER_JOINED_FIELDS
    }
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


def validate_bounded_result(
    path: Path,
    *,
    packet_identity: str,
    reviewed_input_identity: str,
    require_pass: bool,
) -> dict[str, Any]:
    """Validate the canonical result and optionally require a passing verdict."""
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
    if require_pass and payload.get("verdict") != "pass":
        raise ReviewerResultError(
            f"worker reviewer verdict is not approval-eligible: {payload.get('verdict')!r}"
        )
    return payload
