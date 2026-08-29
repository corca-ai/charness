"""Host-neutral capability envelope validation for the file-backed worker.

This module intentionally validates a small structured observation contract. It
does not infer network policy from sandbox labels, parse provider diagnostics, or
resolve domain allowlists. Its blind class is host behavior that was not
captured in the envelope: the validator can refuse missing or contradictory
observations, but cannot manufacture transport or provider evidence.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_preflight_contract():
    candidate = Path(__file__).resolve().with_name("reviewer_capability_preflight.py")
    spec = importlib.util.spec_from_file_location("charness_reviewer_capability_preflight", candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"package-local capability preflight helper not found: {candidate}")
    module = importlib.util.module_from_spec(spec)
    module_name = "charness_reviewer_capability_preflight"
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
    return module


_PREFLIGHT = _load_preflight_contract()
CAPABILITY_STATUSES = _PREFLIGHT.CAPABILITY_STATUSES
READY = _PREFLIGHT.READY
CapabilityError = _PREFLIGHT.CapabilityError
_FRESHNESS_MODES = _PREFLIGHT._FRESHNESS_MODES
_READ_POLICIES = _PREFLIGHT._READ_POLICIES
_fail = _PREFLIGHT._fail
_list = _PREFLIGHT._list
_mapping = _PREFLIGHT._mapping
_sha256 = _PREFLIGHT._sha256
_text = _PREFLIGHT._text
target_non_claim = _PREFLIGHT.target_non_claim
validate_non_claims = _PREFLIGHT.validate_non_claims
normalized_non_claims = _PREFLIGHT.normalized_non_claims
non_claims_sha256 = _PREFLIGHT.non_claims_sha256
validate_effective = _PREFLIGHT.validate_effective
validate_preflight = _PREFLIGHT.validate_preflight

SCHEMA_VERSION = "charness.capability_envelope.v1"


@dataclass(frozen=True)
class CapabilityDecision:
    """Validated immutable-in-practice envelope and its derived preflight state."""

    status: str
    payload: dict[str, Any]
    envelope_sha256: str

    @property
    def ready(self) -> bool:
        return self.status == READY


def envelope_sha256(payload: dict[str, Any]) -> str:
    """Hash the exact structured envelope without secrets or presentation text."""
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_capability_file(path: str | Path, *, attempt_id: str, require_ready: bool = False) -> CapabilityDecision:
    """Read and validate one host-authored capability envelope."""
    candidate = Path(path).expanduser().resolve()
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CapabilityError("probe-invalid", f"capability envelope is not readable JSON: {candidate}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CapabilityError("probe-invalid", "capability envelope must contain an object")
    return validate_capability_envelope(payload, attempt_id=attempt_id, require_ready=require_ready)


def collect_capability_file(
    path: str | Path, *, attempt_id: str, launch_envelope_sha256: str
) -> CapabilityDecision:
    """Revalidate the host envelope at collection and reject semantic drift."""
    decision = load_capability_file(path, attempt_id=attempt_id, require_ready=True)
    if decision.envelope_sha256 != launch_envelope_sha256:
        raise CapabilityError(
            "probe-invalid",
            "capability envelope changed between launch and collection",
            payload=decision.payload,
        )
    return decision


def receipt_capability_fields(
    payload: dict[str, Any], status: str, *, launch_envelope_sha256: str | None = None,
    collection_envelope_sha256: str | None = None,
) -> dict[str, Any]:
    """Copy one validated envelope into the existing worker receipt shape."""
    envelope_hash = envelope_sha256(payload)
    launch_hash = launch_envelope_sha256 or envelope_hash
    collection_hash = collection_envelope_sha256 or envelope_hash
    claims = normalized_non_claims(payload.get("capability_non_claims", []))
    return {
        "capability_status": status,
        "capability_envelope_sha256": envelope_hash,
        "capability_launch_envelope_sha256": launch_hash,
        "capability_collection_envelope_sha256": collection_hash,
        "requested_capabilities": payload.get("requested_capabilities"),
        "effective_capabilities": payload.get("effective_capabilities"),
        "preflight": payload.get("preflight"),
        "capability_non_claims": payload.get("capability_non_claims", []),
        "capability_non_claims_sha256": non_claims_sha256(claims),
    }


def validate_capability_envelope(
    payload: dict[str, Any], *, attempt_id: str, require_ready: bool = False
) -> CapabilityDecision:
    """Validate policy, effective-axis observations, and ordered preflight layers."""
    if payload.get("schema_version") != SCHEMA_VERSION:
        _fail(f"capability envelope schema_version must be {SCHEMA_VERSION}", payload)
    task_kind = _text(payload.get("task_kind"), "task_kind", payload)
    if task_kind != "read":
        _fail("first-slice capability envelope task_kind must be `read`", payload)
    requested = _mapping(payload.get("requested_capabilities"), "requested_capabilities", payload)
    effective = _mapping(payload.get("effective_capabilities"), "effective_capabilities", payload)
    raw_non_claims = payload.get("capability_non_claims", [])

    filesystem = _mapping(requested.get("filesystem"), "requested_capabilities.filesystem", payload)
    read_roots = _list(filesystem.get("read_roots"), "filesystem.read_roots", payload)
    if any(not isinstance(root, str) or not root.strip() for root in read_roots):
        _fail("filesystem.read_roots must contain non-empty paths", payload)
    write_policy = _text(filesystem.get("write_policy"), "filesystem.write_policy", payload)
    write_roots = _list(filesystem.get("write_roots"), "filesystem.write_roots", payload)
    if any(not isinstance(root, str) or not root.strip() for root in write_roots):
        _fail("filesystem.write_roots must contain non-empty paths", payload)
    if write_policy != "deny-all" or write_roots:
        _fail("a read task requires explicit filesystem write_policy=deny-all and empty write_roots", payload)

    external_reads = _list(requested.get("external_reads"), "requested_capabilities.external_reads", payload)
    read_policies: dict[str, str] = {}
    for index, entry_value in enumerate(external_reads):
        entry = _mapping(entry_value, f"external_reads[{index}]", payload)
        policy = _text(entry.get("policy"), f"external_reads[{index}].policy", payload)
        if policy not in _READ_POLICIES:
            _fail(f"external_reads[{index}].policy is unknown: {policy}", payload)
        target = _text(entry.get("logical_target"), f"external_reads[{index}].logical_target", payload)
        for field in ("capability", "probe_type", "target_class", "freshness"):
            value = _text(entry.get(field), f"external_reads[{index}].{field}", payload)
            if field == "freshness" and value not in _FRESHNESS_MODES:
                _fail(f"external_reads[{index}].freshness is unknown: {value}", payload)
        if target in read_policies:
            _fail(f"contradictory or duplicate external-read policy for target: {target}", payload)
        read_policies[target] = policy
    non_claims = validate_non_claims(raw_non_claims, read_policies, payload)

    effects = _mapping(requested.get("external_effects"), "requested_capabilities.external_effects", payload)
    effect_policy = _text(effects.get("policy"), "external_effects.policy", payload)
    effect_entries = _list(effects.get("entries"), "external_effects.entries", payload)
    if effect_policy != "deny-all" or effect_entries:
        _fail("a read task requires explicit external_effects policy=deny-all and empty entries", payload)

    effective_read_states = validate_effective(effective, read_policies, payload)
    preflight = _list(payload.get("preflight"), "preflight", payload)
    status = validate_preflight(preflight, read_policies, effective_read_states, attempt_id, non_claims, payload)
    decision = CapabilityDecision(status, payload, envelope_sha256(payload))
    if require_ready and not decision.ready:
        raise CapabilityError(status, f"required capability preflight is {status}", payload=payload)
    return decision


def validate_receipt_capabilities(receipt: dict[str, Any], *, attempt_id: str) -> CapabilityDecision:
    """Revalidate copied receipt fields before the combined report can approve."""
    fields = (
        "requested_capabilities",
        "effective_capabilities",
        "preflight",
        "capability_non_claims",
        "capability_non_claims_sha256",
    )
    if any(field not in receipt for field in fields):
        raise CapabilityError("probe-invalid", "worker receipt is missing capability envelope fields")
    envelope_fields = fields[:-1]
    decision = validate_capability_envelope(
        {
            "schema_version": SCHEMA_VERSION,
            "task_kind": "read",
            **{field: receipt[field] for field in envelope_fields},
        },
        attempt_id=attempt_id,
        require_ready=True,
    )
    if receipt.get("capability_status") != decision.status:
        raise CapabilityError("probe-invalid", "worker receipt capability_status does not match its envelope")
    if receipt.get("capability_envelope_sha256") != decision.envelope_sha256:
        raise CapabilityError("probe-invalid", "worker receipt capability envelope hash does not match its fields")
    if receipt.get("capability_launch_envelope_sha256") != decision.envelope_sha256:
        raise CapabilityError("probe-invalid", "worker receipt launch capability hash does not match its fields")
    if receipt.get("capability_collection_envelope_sha256") != decision.envelope_sha256:
        raise CapabilityError("probe-invalid", "worker receipt collection capability hash does not match its fields")
    expected_non_claims_sha256 = non_claims_sha256(decision.payload["capability_non_claims"])
    if receipt.get("capability_non_claims_sha256") != expected_non_claims_sha256:
        raise CapabilityError("probe-invalid", "worker receipt non-claim digest does not match its fields")
    return decision


def join_result_capability_non_claims(
    result: dict[str, Any], capability_payload: dict[str, Any]
) -> dict[str, Any]:
    """Return ``result`` with capability provenance taken from the envelope (#755).

    Capability non-claims are an authority statement about what the HOST granted
    this run. The reviewer model has no standing to assert them and no way to
    compute their canonical digest, so requiring it to reproduce both made a
    deterministic value the model's job. Three consecutive Ceal reviews returned
    substantive findings and were rejected on this field alone: a digest of `[]`
    computed the wrong way, then two invented external-read non-claims, then the
    SHA-256 of empty bytes.

    Whatever the model wrote here is REPLACED, not merged. A model-authored
    non-claim is not evidence of anything the host observed, so preserving it
    would carry an unfounded authority claim into the delivered artifact; the
    caller records that provenance was joined so an auditor can see these two
    fields are runner-owned. The fail-closed equality check remains after this
    join as the invariant, not as the thing that catches model error.
    """
    joined = dict(result)
    claims = normalized_non_claims(capability_payload.get("capability_non_claims", []))
    joined["capability_non_claims"] = claims
    joined["capability_non_claims_sha256"] = non_claims_sha256(claims)
    return joined


def validate_result_capability_non_claims(
    result: dict[str, Any], capability_payload: dict[str, Any]
) -> None:
    """Require the semantic result to repeat the exact capability non-claims."""
    expected = normalized_non_claims(capability_payload.get("capability_non_claims", []))
    actual_value = result.get("capability_non_claims")
    if actual_value is None:
        raise CapabilityError("probe-invalid", "worker result is missing capability_non_claims")
    actual = normalized_non_claims(actual_value)
    if actual != expected:
        raise CapabilityError("probe-invalid", "worker result capability non-claims do not match the launch envelope")
    expected_digest = non_claims_sha256(expected)
    if result.get("capability_non_claims_sha256") != expected_digest:
        raise CapabilityError("probe-invalid", "worker result capability non-claim digest does not match the launch envelope")
