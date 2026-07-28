"""Artifact-side validation for critique reviewed-input bindings."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module

_identity = import_repo_module(__file__, "scripts.reviewed_input_identity")
_artifact_validator = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _artifact_validator.ValidationError
# One definition, shared with the validator. Two copies of this regex existed and
# both missed the bullet form the corpus writes, so "is this critique packet-bound"
# had two answers that could drift independently.
_scope = import_repo_module(__file__, "scripts.critique_enforcement_scope")
PACKET_CONSUMED_RE = _scope.PACKET_CONSUMED_RE
packet_consumed = _scope.packet_consumed
EXPECTED_KIND = "charness.critique_prepare_packet"


def _binding_fields(text: str) -> dict[str, str]:
    section = text.partition(_identity.ARTIFACT_HEADING)[2].partition("\n## ")[0]
    fields: dict[str, str] = {}
    for raw in section.splitlines():
        stripped = raw.strip()
        if stripped.startswith("- ") and ":" in stripped:
            key, _, value = stripped.lstrip("- ").partition(":")
            fields[key.replace("*", "").strip().lower()] = value.strip().strip("`")
    return fields


def validate_reviewed_input_binding(
    path: Path,
    text: str,
    observed_date: date | None,
    *,
    check_current: bool = True,
) -> None:
    fields = _binding_fields(text)
    required = _identity.artifact_binding_required(
        path.name, observed_date, packet_consumed(text)
    )
    current, reason = _identity.verify_declared_binding(
        path,
        fields,
        required=required,
        required_fields=_identity.ARTIFACT_REQUIRED_FIELDS,
        expected_kind=EXPECTED_KIND,
        check_current=check_current,
    )
    if not current:
        raise ValidationError(f"{path}: {reason}")
