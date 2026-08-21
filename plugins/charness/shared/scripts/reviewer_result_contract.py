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
