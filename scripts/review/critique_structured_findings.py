"""Validation for the structured findings section of critique records."""

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

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_artifact_validator = import_repo_module(__file__, "scripts.artifacts.artifact_validator")
_structured_entry_floor = import_repo_module(__file__, "scripts.gates_support.structured_entry_floor")
ValidationError = _artifact_validator.ValidationError
is_valid_followup_tail = _artifact_validator.is_valid_followup_tail

STRUCTURED_FINDINGS_HEADING = "## Structured Findings"
STRUCTURED_BINS = frozenset({"act-before-ship", "bundle-anyway", "over-worry", "valid-but-defer"})
STRUCTURED_EVIDENCE = frozenset({"strong", "moderate", "weak", "contested"})
STRUCTURED_ACTIONS = frozenset({"fix", "file-issue", "document", "defer"})
STRUCTURED_REQUIRED_FIELDS = ("bin", "evidence", "ref", "action", "note")
STRUCTURED_FINDING_FORM = (
    "- <id> | bin: <bin> | evidence: <evidence> | ref: <path-or-line> | "
    "action: <action> | note: <one-line rationale>"
)


def _check_finding_followup(finding: dict[str, str], finding_id: str, path: Path) -> None:
    """Require a parseable follow-up when a finding files an issue."""
    followup_value = finding.get("follow-up", "")
    if finding["action"] == "file-issue":
        if not is_valid_followup_tail(followup_value.strip().lower()):
            raise ValidationError(
                f"{path}: `{STRUCTURED_FINDINGS_HEADING}` entry {finding_id} has `action: file-issue` "
                "but no parseable `follow-up:` field; record the issue URL or "
                "`follow-up: deferred <handoff-anchor>` per "
                "skills/public/critique/references/counterweight-triage.md."
            )
    elif followup_value and not is_valid_followup_tail(followup_value.strip().lower()):
        raise ValidationError(
            f"{path}: `{STRUCTURED_FINDINGS_HEADING}` entry {finding_id} has malformed `follow-up:` value "
            "(bare `deferred` without an anchor)."
        )


def validate_structured_findings(path: Path, text: str) -> None:
    _structured_entry_floor.validate_structured_entries(
        path,
        text,
        heading=STRUCTURED_FINDINGS_HEADING,
        required_fields=STRUCTURED_REQUIRED_FIELDS,
        enum_fields={
            "bin": STRUCTURED_BINS,
            "evidence": STRUCTURED_EVIDENCE,
            "action": STRUCTURED_ACTIONS,
        },
        form_hint=STRUCTURED_FINDING_FORM,
        per_entry=lambda finding, finding_id: _check_finding_followup(finding, finding_id, path),
    )
