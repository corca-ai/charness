"""Artifact-side validation for critique reviewed-input bindings."""

from __future__ import annotations

from datetime import date
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_identity = import_repo_module(__file__, "scripts.review.reviewed_input_verification")
_artifact_validator = import_repo_module(__file__, "scripts.artifacts.artifact_validator")
ValidationError = _artifact_validator.ValidationError
# One definition, shared with the validator. Two copies of this regex existed and
# both missed the bullet form the corpus writes, so "is this critique packet-bound"
# had two answers that could drift independently.
_scope = import_repo_module(__file__, "scripts.review.critique_enforcement_scope")
_sections = import_repo_module(__file__, "scripts.core.markdown_sections")
PACKET_CONSUMED_RE = _scope.PACKET_CONSUMED_RE
packet_consumed = _scope.packet_consumed
EXPECTED_KIND = "charness.critique_prepare_packet"


def _binding_fields(text: str) -> dict[str, str]:
    # The `- Key: value` read is one concept, shared with every other floor that
    # keys off a declared section; the copy here used `partition` on the heading
    # SUBSTRING, so a heading mentioned mid-prose sliced the section from the wrong
    # place. `section_field_map` requires the heading on its own line.
    return _sections.section_field_map(text, _identity.ARTIFACT_HEADING)


def reviewed_input_binding_fields(text: str) -> dict[str, str]:
    """Return the artifact's declared packet/input join fields for sibling floors."""

    return _binding_fields(text)


def validate_reviewed_input_binding(
    path: Path,
    text: str,
    observed_date: date | None,
    *,
    check_current: bool = True,
    repo_root: Path | None = None,
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
        repo_root=repo_root,
    )
    if not current:
        raise ValidationError(f"{path}: {reason}")
