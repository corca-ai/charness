"""Typed registry for producer-to-final-consumer boundary invariants.

The registry is an audit contract, not a second approval owner.  Domain
consumers still decide their own verdicts; this module makes the obligations
they must expose discoverable and mechanically checkable.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

SCHEMA_VERSION = "charness.provenance_contract.v1"
_ID_RE = re.compile(r"^[a-z][a-z0-9_]+$")


class BoundaryContractError(ValueError):
    """A boundary obligation is missing or malformed."""


@dataclass(frozen=True)
class BoundaryContract:
    contract_id: str
    producer: str
    consumer: str
    required_fields: tuple[str, ...]
    terminal_outcomes: tuple[str, ...]
    refusal_code: str
    negative_fixture: str
    consumer_path: str
    trigger_paths: tuple[str, ...]


CONTRACTS: tuple[BoundaryContract, ...] = (
    BoundaryContract(
        contract_id="reviewer_delivery",
        producer="reviewer receipt and delivery attempt",
        consumer="reviewer worker report",
        required_fields=("output_file", "receipt_file", "producer_run_id"),
        terminal_outcomes=("succeeded", "timed-out", "interrupted", "missing"),
        refusal_code="producer-binding-missing",
        negative_fixture=(
            "tests/quality_gates/test_reviewer_worker_report.py::"
            "test_missing_producer_binding_is_not_approval_eligible"
        ),
        consumer_path="skills/shared/scripts/reviewer_worker_report.py",
        trigger_paths=(
            "skills/shared/scripts/provenance_contract.py",
            "skills/shared/scripts/reviewer_worker_report.py",
            "skills/shared/scripts/reviewer_capability.py",
            "skills/shared/scripts/reviewer_capability_preflight.py",
            "skills/shared/scripts/reviewer_output.py",
            "skills/shared/scripts/reviewer_result_contract.py",
            "skills/shared/scripts/reviewer_runner_support.py",
            "skills/shared/scripts/reviewer_delivery.py",
            "skills/shared/scripts/reviewer_delivery_attempt.py",
            "skills/shared/scripts/reviewer_delivery_fields.py",
            "skills/shared/scripts/reviewer_delivery_schema.py",
            "skills/shared/scripts/reviewer_delivery_history.py",
            "skills/shared/scripts/reviewer_delivery_state.py",
            "skills/shared/scripts/reviewer_partial_output.py",
            "scripts/yaml_output.py",
            "plugins/charness/shared/scripts/provenance_contract.py",
            "plugins/charness/shared/scripts/reviewer_worker_report.py",
            "plugins/charness/shared/scripts/reviewer_capability.py",
            "plugins/charness/shared/scripts/reviewer_capability_preflight.py",
            "plugins/charness/shared/scripts/reviewer_output.py",
            "plugins/charness/shared/scripts/reviewer_result_contract.py",
            "plugins/charness/shared/scripts/reviewer_runner_support.py",
            "plugins/charness/shared/scripts/reviewer_delivery.py",
            "plugins/charness/shared/scripts/reviewer_delivery_attempt.py",
            "plugins/charness/shared/scripts/reviewer_delivery_fields.py",
            "plugins/charness/shared/scripts/reviewer_delivery_schema.py",
            "plugins/charness/shared/scripts/reviewer_delivery_history.py",
            "plugins/charness/shared/scripts/reviewer_delivery_state.py",
            "plugins/charness/shared/scripts/reviewer_partial_output.py",
            "plugins/charness/scripts/yaml_output.py",
            "tests/quality_gates/test_reviewer_worker_report.py",
            "skills/public/quality/scripts/check_provenance_contract.py",
            "plugins/charness/skills/quality/scripts/check_provenance_contract.py",
            "tests/test_provenance_contract.py",
        ),
    ),
    BoundaryContract(
        contract_id="skill_manifest_selection",
        producer="candidate plugin manifest",
        consumer="skill capability resolver",
        required_fields=("manifest_version", "manifest_object"),
        terminal_outcomes=("valid", "malformed", "missing"),
        refusal_code="package-manifest-invalid",
        negative_fixture=(
            "tests/test_capability_catalog.py::"
            "test_catalog_resolver_refuses_malformed_candidate_manifest"
        ),
        consumer_path="scripts/capability_catalog_resolver.py",
        trigger_paths=(
            "scripts/capability_catalog_resolver.py",
            "plugins/charness/scripts/capability_catalog_resolver.py",
            "tests/test_capability_catalog.py",
        ),
    ),
    BoundaryContract(
        contract_id="duplicate_lineage",
        producer="duplicate-family baseline and live scan",
        consumer="duplicate-ratchet verdict",
        required_fields=("baseline_member_paths", "lineage_readiness"),
        terminal_outcomes=("ready", "unavailable"),
        refusal_code="lineage-approval-unavailable",
        negative_fixture=(
            "tests/quality_gates/test_dup_ratchet.py::"
            "test_cli_lineage_unavailability_is_not_approval_eligible"
        ),
        consumer_path="skills/public/quality/scripts/check_dup_ratchet.py",
        trigger_paths=(
            "skills/public/quality/scripts/check_dup_ratchet.py",
            "skills/public/quality/scripts/dup_review_lib.py",
            "skills/public/quality/scripts/dup_family_lineage.py",
            "skills/public/quality/scripts/dup_ratchet_lib.py",
            "skills/public/quality/scripts/dup_ratchet_baseline_lib.py",
            "skills/public/quality/scripts/dup_ratchet_rebaseline.py",
            "skills/public/quality/scripts/dup_ratchet_scan.py",
            "skills/public/quality/scripts/dup_ratchet_git.py",
            "skills/public/quality/scripts/dup_ratchet_scope.py",
            "skills/public/quality/scripts/nose_report_lib.py",
            "skills/public/quality/scripts/nose_fingerprint_lib.py",
            "skills/public/quality/scripts/nose_tool_lib.py",
            "skills/public/quality/scripts/inventory_nose_clones.py",
            "skills/public/quality/scripts/inventory_doc_duplicates.py",
            "skills/public/quality/scripts/summary_output_lib.py",
            "scripts/quality_adapter_lib.py",
            "plugins/charness/skills/quality/scripts/check_dup_ratchet.py",
            "plugins/charness/skills/quality/scripts/dup_review_lib.py",
            "plugins/charness/skills/quality/scripts/dup_family_lineage.py",
            "plugins/charness/skills/quality/scripts/dup_ratchet_lib.py",
            "plugins/charness/skills/quality/scripts/dup_ratchet_baseline_lib.py",
            "plugins/charness/skills/quality/scripts/dup_ratchet_rebaseline.py",
            "plugins/charness/skills/quality/scripts/dup_ratchet_scan.py",
            "plugins/charness/skills/quality/scripts/dup_ratchet_git.py",
            "plugins/charness/skills/quality/scripts/dup_ratchet_scope.py",
            "plugins/charness/skills/quality/scripts/nose_report_lib.py",
            "plugins/charness/skills/quality/scripts/nose_fingerprint_lib.py",
            "plugins/charness/skills/quality/scripts/nose_tool_lib.py",
            "plugins/charness/skills/quality/scripts/inventory_nose_clones.py",
            "plugins/charness/skills/quality/scripts/inventory_doc_duplicates.py",
            "plugins/charness/skills/quality/scripts/summary_output_lib.py",
            "plugins/charness/scripts/quality_adapter_lib.py",
            "skills/public/quality/scripts/check_provenance_contract.py",
            "plugins/charness/skills/quality/scripts/check_provenance_contract.py",
            "tests/quality_gates/test_dup_ratchet.py",
            "tests/quality_gates/test_staged_commit_gate_plan.py",
            "tests/test_provenance_contract.py",
        ),
    ),
)


def contract_for(contract_id: str) -> BoundaryContract:
    """Return one named contract or fail closed on an unknown boundary."""
    for contract in CONTRACTS:
        if contract.contract_id == contract_id:
            return contract
    raise BoundaryContractError(f"unknown boundary contract: {contract_id}")


def require_bound_fields(contract_id: str, values: Mapping[str, object]) -> None:
    """Reject a consumer input that omits a producer-owned required binding."""
    contract = contract_for(contract_id)
    missing = [
        field
        for field in contract.required_fields
        if values.get(field) is None or values.get(field) == ""
    ]
    if missing:
        raise BoundaryContractError(
            f"{contract.contract_id} missing required producer binding(s): {', '.join(missing)}"
        )


def _relative_fixture_parts(reference: str) -> tuple[str, str | None]:
    """Split and validate a repo-relative pytest node reference."""
    path, separator, node = reference.partition("::")
    candidate = Path(path)
    if not path or candidate.is_absolute() or ".." in candidate.parts:
        raise BoundaryContractError(f"negative fixture path must be repo-relative: {reference!r}")
    if separator and not node:
        raise BoundaryContractError(f"negative fixture node is empty: {reference!r}")
    return path, node or None


def validate_registry(repo_root: Path, *, require_repo_anchors: bool = True) -> list[str]:
    """Validate shape, plus source/test anchors when running in the authoring tree."""
    errors: list[str] = []
    seen: set[str] = set()
    for contract in CONTRACTS:
        if not _ID_RE.fullmatch(contract.contract_id):
            errors.append(f"invalid contract_id: {contract.contract_id!r}")
        if contract.contract_id in seen:
            errors.append(f"duplicate contract_id: {contract.contract_id}")
        seen.add(contract.contract_id)
        if not contract.producer or not contract.consumer:
            errors.append(f"{contract.contract_id} lacks producer/consumer ownership")
        if len(set(contract.required_fields)) != len(contract.required_fields):
            errors.append(f"{contract.contract_id} repeats a required field")
        if not contract.required_fields or not contract.terminal_outcomes:
            errors.append(f"{contract.contract_id} lacks required obligations/outcomes")
        if not contract.refusal_code:
            errors.append(f"{contract.contract_id} lacks refusal_code")
        if not contract.trigger_paths:
            errors.append(f"{contract.contract_id} lacks trigger_paths")
        if require_repo_anchors:
            for relative in (
                contract.consumer_path,
                contract.negative_fixture.split("::", 1)[0],
                *contract.trigger_paths,
            ):
                try:
                    _relative_fixture_parts(relative)
                except BoundaryContractError as exc:
                    errors.append(f"{contract.contract_id}: {exc}")
                    continue
                if not (repo_root / relative).is_file():
                    errors.append(f"{contract.contract_id} references missing path: {relative}")
            consumer = repo_root / contract.consumer_path
            if consumer.is_file() and contract.contract_id not in consumer.read_text(encoding="utf-8"):
                errors.append(f"{contract.contract_id} is not anchored in {contract.consumer_path}")
            fixture_path, fixture_node = _relative_fixture_parts(contract.negative_fixture)
            fixture = repo_root / fixture_path
            if fixture.is_file() and not fixture_node:
                errors.append(
                    f"{contract.contract_id} negative fixture must name an exact test node: "
                    f"{contract.negative_fixture}"
                )
    # Keep the serialized shape deterministic for callers that snapshot the registry.
    # This is intentionally a read-only assertion: domain consumers still own verdicts.
    json.dumps(
        [
            {
                "contract_id": item.contract_id,
                "producer": item.producer,
                "consumer": item.consumer,
                "required_fields": item.required_fields,
                "terminal_outcomes": item.terminal_outcomes,
                "refusal_code": item.refusal_code,
                "negative_fixture": item.negative_fixture,
                "consumer_path": item.consumer_path,
                "trigger_paths": item.trigger_paths,
            }
            for item in CONTRACTS
        ],
        sort_keys=True,
    )
    return errors
