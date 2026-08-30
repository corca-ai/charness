"""Closed-world shape of a release claims-review record.

Versioned proof records must reject unknown fields. An open dictionary let a retired
scope state survive in the validator result, resume payload, and public renderer after
the validator had changed to refuse that state. Closed shapes turn future state
contraction into an immediate authoring refusal instead of accidental residue.
"""
from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "charness.release.claims-review.v4"
VERDICTS = ("pass", "unproven")
DISTINCTNESS_KINDS = ("separate-agent-context", "separate-host", "separate-operator")

_BASE_FIELDS = {
    "schema_version", "prepared_commit", "release_record_path", "release_record_sha256",
    "target_version", "tag_name", "verdict", "preparer_context", "reviewer_context",
    "observer_distinctness",
}
_PASS_FIELDS = _BASE_FIELDS | {"review_scope", "scope_basis", "advisory_findings"}
_OBSERVER_FIELDS = {"kind", "signal", "review_artifact"}
_SCOPE_FIELDS = {"blocking_paths", "advisory_paths"}
_BASIS_FIELDS = {"base_ref", "changed_paths_sha256", "changed_path_count"}


def _exact_keys(value: object, expected: set[str], field: str) -> None:
    if not isinstance(value, dict):
        raise SystemExit(f"--resume: claims-review `{field}` must be an object")
    observed = set(value)
    if observed != expected:
        missing, unknown = sorted(expected - observed), sorted(observed - expected)
        raise SystemExit(
            f"--resume: claims-review `{field}` has a non-canonical field set; "
            f"missing={missing!r}, unknown={unknown!r}"
        )


def assert_closed_record_shape(data: dict[str, Any], *, verdict: str) -> None:
    """Refuse stale or invented state before any field can be silently ignored."""
    _exact_keys(data, _PASS_FIELDS if verdict == "pass" else _BASE_FIELDS, "record")
    _exact_keys(data.get("observer_distinctness"), _OBSERVER_FIELDS, "observer_distinctness")
    if verdict == "pass":
        _exact_keys(data.get("review_scope"), _SCOPE_FIELDS, "review_scope")
        _exact_keys(data.get("scope_basis"), _BASIS_FIELDS, "scope_basis")


def assert_exact_record_binding(
    data: object, *, prepared: dict[str, str], target_version: str, tag_name: str
) -> dict[str, Any]:
    """Bind a record to the prepared release facts the scaffold derives."""
    if not isinstance(data, dict):
        raise SystemExit("--resume: claims-review artifact does not bind the exact prepared release record")
    expected = {
        "schema_version": SCHEMA_VERSION,
        "prepared_commit": prepared["commit"],
        "release_record_path": prepared["path"],
        "release_record_sha256": prepared["sha256"],
        "target_version": target_version,
        "tag_name": tag_name,
    }
    mismatched = {key: value for key, value in expected.items() if data.get(key) != value}
    if mismatched:
        detail = "; ".join(
            f"{key}: expected {value!r}, record carries {data.get(key)!r}"
            for key, value in sorted(mismatched.items())
        )
        raise SystemExit(
            "--resume: claims-review artifact does not bind the exact prepared release record -- "
            f"{detail}. Repair by AMENDING the evidence commit in place; a follow-on commit is "
            "not the direct child of the prepared record and is refused."
        )
    return data
