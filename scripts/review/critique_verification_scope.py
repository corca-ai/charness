"""Validate the optional reduction-first verification scope record."""

from __future__ import annotations

from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    load_path_module,
    repo_root_from_script,
    skill_script,
)

REPO_ROOT = repo_root_from_script(__file__)
_artifact_validator = import_repo_module(__file__, "scripts.artifacts.artifact_validator")
_sections = import_repo_module(__file__, "scripts.core.markdown_sections")
_verification_retry = load_path_module(
    "charness_critique_verification_retry",
    skill_script(REPO_ROOT, "critique", "verification_retry.py"),
)
ValidationError = _artifact_validator.ValidationError

HEADING = "## Verification Scope Decision"
REQUIRED_FIELDS = (
    "claim under test",
    "changed surfaces",
    "minimum sufficient proof",
    "deliberately omitted checks",
    "verifier contract",
    "failure classification",
    "negative control",
    "subject identity",
    "verifier identity",
    "input identity",
    "failure identity",
    "evidence identity",
    "retry disposition",
    "retry key",
)
FAILURE_CLASSIFICATIONS = frozenset({"scope-too-broad", "verifier-defect", "subject-defect", "none"})
RETRY_DISPOSITIONS = frozenset({"first-attempt", "retry-new-identity", "stop-no-progress", "non-claim"})
PLACEHOLDERS = {"", "todo", "tbd", "missing", "n/a", "na", "blocked"}


def _field_map(text: str) -> dict[str, str]:
    return _sections.section_field_map(text, HEADING)


def validate(path: Path, text: str) -> None:
    """Check record shape and retry-key binding, without judging proof truth."""
    if HEADING not in text:
        return
    fields = _field_map(text)
    missing = [field for field in REQUIRED_FIELDS if not fields.get(field)]
    if missing:
        raise ValidationError(f"{path}: `{HEADING}` is missing fields: " + ", ".join(missing))
    for field in REQUIRED_FIELDS:
        value = fields[field].strip()
        if value.lower().startswith("todo") or value.lower() in PLACEHOLDERS:
            raise ValidationError(f"{path}: `{HEADING}` field `{field}` is still a placeholder")

    classification = fields["failure classification"].strip().lower()
    if classification not in FAILURE_CLASSIFICATIONS:
        raise ValidationError(
            f"{path}: failure classification `{classification}` must be one of "
            + ", ".join(sorted(FAILURE_CLASSIFICATIONS))
        )
    disposition = fields["retry disposition"].strip().lower()
    if disposition not in RETRY_DISPOSITIONS:
        raise ValidationError(
            f"{path}: retry disposition `{disposition}` must be one of "
            + ", ".join(sorted(RETRY_DISPOSITIONS))
        )
    negative_control = fields["negative control"].strip().lower()
    if not (
        negative_control.startswith("none with rationale:")
        or all(marker in negative_control for marker in ("command", "expected", "observed", "receipt"))
    ):
        raise ValidationError(
            f"{path}: negative control must record command/expected refusal/observed result/receipt "
            "or `none with rationale: ...`"
        )
    try:
        subject = _verification_retry.canonical_identity(fields["subject identity"])
        verifier = _verification_retry.canonical_identity(fields["verifier identity"])
        input_identity = _verification_retry.canonical_identity(fields["input identity"])
        failure = _verification_retry.canonical_failure_code(fields["failure identity"])
        _verification_retry.evidence_identity(fields["evidence identity"])
        expected_key = _verification_retry.build_retry_key(
            subject=subject,
            verifier=verifier,
            input_identity=input_identity,
            failure=failure,
        )
    except ValueError as exc:
        raise ValidationError(f"{path}: invalid verification scope identity: {exc}") from exc
    if fields["retry key"].strip().lower() != expected_key:
        raise ValidationError(f"{path}: retry key does not match subject/verifier/input/failure identities")
