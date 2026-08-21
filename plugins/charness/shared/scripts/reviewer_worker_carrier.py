"""Validate the typed report carrier used by a file-backed reviewer.

The sibling support module owns repository I/O and receipt/ledger joins. This
surface owns the artifact-field contract and joins those results to the cited
critique, so public consumers share one approval meaning.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any

import yaml


def _load_support_module():
    candidate = Path(__file__).resolve().with_name("reviewer_worker_carrier_support.py")
    spec = importlib.util.spec_from_file_location("charness_reviewer_worker_carrier_support", candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"package-local worker carrier support is unavailable: {candidate}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SUPPORT = _load_support_module()
PARENT_RECEIPT_ID_RE = _SUPPORT.PARENT_RECEIPT_ID_RE
WorkerCarrierError = _SUPPORT.WorkerCarrierError
_report_path = _SUPPORT._report_path
_sha256 = _SUPPORT._sha256
_validate_delivery_chain = _SUPPORT._validate_delivery_chain
_validate_packet_binding = _SUPPORT._validate_packet_binding

WORKER_REPORT_FIELDS = (
    "worker report",
    "worker report identity",
    "worker report approval",
    "worker report delivery",
    "worker report packet identity",
    "worker report input identity",
    "worker report parent receipt identity",
    "worker report findings identity",
)


def _validate_artifact_fields(fields: dict[str, str]) -> None:
    missing = [field for field in WORKER_REPORT_FIELDS if not fields.get(field)]
    if missing:
        raise WorkerCarrierError(f"`worker-delivered` requires the durable worker report carrier fields: {missing}")
    if fields["worker report approval"].strip().lower() != "approval_eligible: true":
        raise WorkerCarrierError("worker-delivered requires `Worker report approval: approval_eligible: true`; a receipt or output file alone is not approval")
    if fields["worker report delivery"].strip().lower() != "findings-received":
        raise WorkerCarrierError("worker-delivered requires `Worker report delivery: findings-received`; a spawned or recovered worker is not a delivered report")
    for field in (
        "worker report identity",
        "worker report packet identity",
        "worker report input identity",
        "worker report findings identity",
    ):
        if not re.fullmatch(r"[0-9a-f]{64}", fields[field].strip().lower()):
            raise WorkerCarrierError(f"`{field}` must carry a lowercase SHA-256 identity from the combined worker report")
    if not PARENT_RECEIPT_ID_RE.fullmatch(fields["worker report parent receipt identity"].strip()):
        raise WorkerCarrierError("`worker report parent receipt identity` must carry the non-empty, single-line receipt identity from the combined worker report")


def _read_report(report_file: Path, expected_identity: str) -> dict[str, Any]:
    if _sha256(report_file) != expected_identity.strip().lower():
        raise WorkerCarrierError("worker report carrier SHA-256 does not match its recorded identity")
    try:
        report = yaml.safe_load(report_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise WorkerCarrierError(f"worker report carrier is not readable YAML: {exc}") from exc
    if not isinstance(report, dict):
        raise WorkerCarrierError("worker report carrier must contain a mapping")
    required = {
        "schema_version": "charness.reviewer_worker_report.v1",
        "execution_mode": "file-backed-worker",
        "approval_eligible": True,
        "delivery_state": "findings-received",
        "receipt_ok": True,
        "ledger_ok": True,
        "provenance_ok": True,
    }
    mismatches = [key for key, expected in required.items() if report.get(key) != expected]
    if mismatches:
        raise WorkerCarrierError(f"worker report carrier does not prove approval for fields: {mismatches}")
    return report


def _validate_identity_joins(
    *, report: dict[str, Any], fields: dict[str, str], artifact_binding_fields: dict[str, str] | None
) -> None:
    report_fields = {
        "worker report packet identity": report.get("packet_identity"),
        "worker report input identity": report.get("reviewed_input_identity"),
        "worker report parent receipt identity": report.get("parent_receipt_identity"),
        "worker report findings identity": report.get("findings_identity"),
    }
    mismatches = [
        field
        for field, expected in report_fields.items()
        if expected
        != (
            fields[field].strip()
            if field == "worker report parent receipt identity"
            else fields[field].strip().lower()
        )
    ]
    if mismatches:
        raise WorkerCarrierError(f"worker report carrier identity joins do not match: {mismatches}")
    if artifact_binding_fields is None or not all(
        artifact_binding_fields.get(field, "").strip()
        for field in ("packet sha256", "identity sha256")
    ):
        raise WorkerCarrierError("worker-delivered requires a Reviewed Input Identity binding so the worker report's packet and input identities can be joined to the artifact it closes")
    binding_mismatches = []
    for report_field, binding_field in (
        ("worker report packet identity", "packet sha256"),
        ("worker report input identity", "identity sha256"),
    ):
        binding_value = artifact_binding_fields.get(binding_field, "").strip().lower()
        if not binding_value or report_fields[report_field] != binding_value:
            binding_mismatches.append(f"{report_field} != Reviewed Input Identity:{binding_field}")
    if binding_mismatches:
        raise WorkerCarrierError("worker report identities do not match the artifact's Reviewed Input Identity: " + str(binding_mismatches))


def validate_worker_report_carrier(
    *,
    artifact_label: str,
    fields: dict[str, str],
    repo_root: Path,
    artifact_binding_fields: dict[str, str] | None,
    require_delivery_chain: bool = False,
    required_issue_numbers: list[int] | None = None,
    required_repository: str | None = None,
    required_scope_prefix: str | None = None,
) -> dict[str, Any]:
    """Validate and return the joined worker-report mapping."""
    _validate_artifact_fields(fields)
    report = _read_report(_report_path(repo_root, fields["worker report"]), fields["worker report identity"])
    if required_scope_prefix and not str(report.get("scope", "")).startswith(required_scope_prefix):
        raise WorkerCarrierError(f"worker report scope must start with {required_scope_prefix!r} for this consumer")
    _validate_identity_joins(report=report, fields=fields, artifact_binding_fields=artifact_binding_fields)
    if require_delivery_chain:
        _validate_packet_binding(
            repo_root=repo_root,
            artifact_binding_fields=artifact_binding_fields or {},
            required_issue_numbers=required_issue_numbers,
            required_repository=required_repository,
        )
        _validate_delivery_chain(repo_root=repo_root, report=report)
    return report
