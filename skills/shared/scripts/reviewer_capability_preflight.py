"""Typed external-read policy and preflight observation validation.

This is the observation-side contract of the capability envelope. It binds
every named read target to a host observation, preserves layer ordering, and
does not infer authority from sandbox labels or aggregate booleans.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

READY = "ready"
CAPABILITY_STATUSES = frozenset(
    {
        READY,
        "transport-unestablished",
        "credential-invalid",
        "authorization-insufficient",
        "provider-unavailable",
        "probe-invalid",
    }
)
_LAYERS = ("none", "transport", "identity", "authorization", "provider-response")
_AXIS_STATES = frozenset({"allowed", "denied", "unproved"})
_READ_POLICIES = frozenset({"required", "optional", "deny-all"})
_FRESHNESS_MODES = frozenset({"same-attempt"})
_NON_CLAIM_DISPOSITIONS = frozenset({"unavailable", "unproved"})
NON_CLAIM_SCOPE = "external-read-evidence"
_NON_CLAIM_FIELDS = frozenset(
    {"logical_target", "disposition", "scope", "statement", "identity_sha256"}
)
_OBSERVATION_STATUSES = {
    "transport": frozenset({"established", "unestablished"}),
    "identity": frozenset({"established", "rejected", "unestablished"}),
    "authorization": frozenset({"allowed", "insufficient", "unestablished"}),
    "provider-response": frozenset({"ready", "unavailable", "unestablished"}),
}


class CapabilityError(ValueError):
    """A malformed, contradictory, or non-ready capability observation."""

    def __init__(self, status: str, message: str, *, payload: dict[str, Any] | None = None) -> None:
        if status not in CAPABILITY_STATUSES:
            raise ValueError(f"unknown capability status: {status}")
        super().__init__(message)
        self.status = status
        self.payload = payload


def _fail(message: str, payload: dict[str, Any] | None = None) -> None:
    raise CapabilityError("probe-invalid", message, payload=payload)


def _mapping(value: object, label: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be an object", payload)
    return value


def _text(value: object, label: str, payload: dict[str, Any]) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be a non-empty string", payload)
    return value.strip()


def _list(value: object, label: str, payload: dict[str, Any]) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{label} must be a list", payload)
    return value


def _sha256(value: object, label: str, payload: dict[str, Any]) -> str:
    text = _text(value, label, payload).lower()
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        _fail(f"{label} must be a lowercase SHA-256 identity", payload)
    return text


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def target_non_claim(logical_target: str, disposition: str) -> dict[str, str]:
    """Build the only supported target-bound optional evidence non-claim."""
    if not isinstance(logical_target, str) or not logical_target.strip():
        raise ValueError("logical_target must be a non-empty string")
    if disposition not in _NON_CLAIM_DISPOSITIONS:
        raise ValueError(f"unsupported non-claim disposition: {disposition}")
    target = logical_target.strip()
    base = {
        "logical_target": target,
        "disposition": disposition,
        "scope": NON_CLAIM_SCOPE,
        "statement": (
            f"No evidence claim is made for {target}; optional capability is {disposition}."
        ),
    }
    return {**base, "identity_sha256": hashlib.sha256(_canonical(base)).hexdigest()}


def _normalize_non_claims(
    value: object, payload: dict[str, Any], *, read_policies: dict[str, str] | None = None
) -> dict[str, dict[str, str]]:
    records = _list(value, "capability_non_claims", payload)
    by_target: dict[str, dict[str, str]] = {}
    for index, value in enumerate(records):
        record = _mapping(value, f"capability_non_claims[{index}]", payload)
        unknown = set(record) - _NON_CLAIM_FIELDS
        missing = _NON_CLAIM_FIELDS - set(record)
        if unknown or missing:
            _fail(
                f"capability_non_claims[{index}] must have exactly the target-bound fields "
                f"{sorted(_NON_CLAIM_FIELDS)}",
                payload,
            )
        target = _text(record.get("logical_target"), f"capability_non_claims[{index}].logical_target", payload)
        disposition = _text(record.get("disposition"), f"capability_non_claims[{index}].disposition", payload)
        if disposition not in _NON_CLAIM_DISPOSITIONS:
            _fail(f"capability_non_claims[{index}].disposition is unknown: {disposition}", payload)
        scope = _text(record.get("scope"), f"capability_non_claims[{index}].scope", payload)
        statement = _text(record.get("statement"), f"capability_non_claims[{index}].statement", payload)
        identity = _sha256(record.get("identity_sha256"), f"capability_non_claims[{index}].identity_sha256", payload)
        expected = target_non_claim(target, disposition)
        if scope != expected["scope"] or statement != expected["statement"] or identity != expected["identity_sha256"]:
            _fail(f"capability_non_claims[{index}] wording, scope, or identity is not canonical: {target}", payload)
        if target in by_target:
            _fail(f"duplicate capability non-claim target: {target}", payload)
        if read_policies is not None and read_policies.get(target) != "optional":
            _fail(f"capability non-claim target is not an optional external read: {target}", payload)
        by_target[target] = expected
    return by_target


def validate_non_claims(
    value: object, read_policies: dict[str, str], payload: dict[str, Any]
) -> dict[str, dict[str, str]]:
    return _normalize_non_claims(value, payload, read_policies=read_policies)


def normalized_non_claims(value: object) -> list[dict[str, str]]:
    return [record for _target, record in sorted(_normalize_non_claims(value, {}, read_policies=None).items())]


def non_claims_sha256(value: object) -> str:
    return hashlib.sha256(_canonical(normalized_non_claims(value))).hexdigest()


def validate_effective(
    effective: dict[str, Any], read_policies: dict[str, str], payload: dict[str, Any]
) -> dict[str, str]:
    filesystem = _mapping(effective.get("filesystem"), "effective_capabilities.filesystem", payload)
    if filesystem.get("write") != "denied" or filesystem.get("observation") != "host":
        _fail("read task requires host-observed effective filesystem write=denied", payload)
    effects = _mapping(effective.get("external_effects"), "effective_capabilities.external_effects", payload)
    if effects.get("state") != "denied" or effects.get("observation") != "host":
        _fail("read task requires host-observed effective external effects=denied", payload)
    reads = _mapping(effective.get("external_reads"), "effective_capabilities.external_reads", payload)
    if reads.get("state") not in _AXIS_STATES or reads.get("observation") != "host":
        _fail("effective external reads require a host observation in allowed/denied/unproved", payload)
    entries = _list(reads.get("entries"), "effective_capabilities.external_reads.entries", payload)
    effective_by_target: dict[str, str] = {}
    for index, value in enumerate(entries):
        entry = _mapping(value, f"effective_capabilities.external_reads.entries[{index}]", payload)
        target = _text(entry.get("logical_target"), f"effective external-read entry {index}.logical_target", payload)
        state = _text(entry.get("state"), f"effective external-read entry {index}.state", payload)
        observation = _text(
            entry.get("observation"), f"effective external-read entry {index}.observation", payload
        )
        if state not in _AXIS_STATES or observation != "host":
            _fail(f"effective external-read entry is not a host allowed/denied/unproved observation: {target}", payload)
        if target in effective_by_target:
            _fail(f"duplicate effective external-read target: {target}", payload)
        if target not in read_policies:
            _fail(f"effective external-read target was not requested: {target}", payload)
        if read_policies[target] == "deny-all" and state != "denied":
            _fail(f"deny-all external-read target must be host-observed as denied: {target}", payload)
        effective_by_target[target] = state
    missing = [target for target in read_policies if target not in effective_by_target]
    if missing:
        _fail("missing effective external-read target(s): " + ", ".join(missing), payload)
    states = list(effective_by_target.values())
    aggregate = "unproved" if not states or len(set(states)) > 1 else states[0]
    if reads.get("state") != aggregate:
        _fail("effective external-read aggregate state does not match its per-target observations", payload)
    _text(effective.get("host_selection_source"), "effective_capabilities.host_selection_source", payload)
    _text(effective.get("configuration_identity"), "effective_capabilities.configuration_identity", payload)
    sandbox = _mapping(effective.get("sandbox"), "effective_capabilities.sandbox", payload)
    _text(sandbox.get("label"), "effective_capabilities.sandbox.label", payload)
    _text(sandbox.get("source"), "effective_capabilities.sandbox.source", payload)
    return effective_by_target


def validate_preflight(
    records: list[Any],
    read_policies: dict[str, str],
    effective_read_states: dict[str, str],
    attempt_id: str,
    non_claims: dict[str, dict[str, str]],
    payload: dict[str, Any],
) -> str:
    by_target: dict[str, dict[str, Any]] = {}
    for index, record_value in enumerate(records):
        record = _mapping(record_value, f"preflight[{index}]", payload)
        target = _text(record.get("logical_target"), f"preflight[{index}].logical_target", payload)
        if target in by_target:
            _fail(f"duplicate preflight target: {target}", payload)
        by_target[target] = record
    preflight_targets = {target for target, policy in read_policies.items() if policy != "deny-all"}
    unexpected = [target for target in by_target if target not in preflight_targets]
    if unexpected:
        _fail("preflight contains a denied or unrequested logical target: " + ", ".join(unexpected), payload)
    missing = [target for target in preflight_targets if target not in by_target]
    if missing:
        _fail("missing preflight for requested non-deny-all logical target(s): " + ", ".join(missing), payload)
    required_statuses: list[str] = []
    for target in preflight_targets:
        policy = read_policies[target]
        status = _validate_preflight_record(
            target,
            by_target[target],
            policy=policy,
            effective_state=effective_read_states[target],
            attempt_id=attempt_id,
            non_claim=non_claims.get(target),
            payload=payload,
        )
        if policy == "required":
            required_statuses.append(status)
    if len(set(required_statuses)) > 1:
        _fail("required external-read preflight statuses disagree for one attempt", payload)
    return required_statuses[0] if required_statuses else READY


def _validate_preflight_record(
    target: str,
    record: dict[str, Any],
    *,
    policy: str,
    effective_state: str,
    attempt_id: str,
    non_claim: dict[str, str] | None,
    payload: dict[str, Any],
) -> str:
    """Validate one target observation and its policy-bound non-claim."""
    if record.get("attempt_id") != attempt_id:
        _fail(f"preflight attempt_id does not match {attempt_id}: {target}", payload)
    reached = _text(record.get("reached_layer"), f"preflight[{target}].reached_layer", payload)
    if reached not in _LAYERS:
        _fail(f"preflight reached_layer is unknown: {reached}", payload)
    _text(record.get("probe_identity"), f"preflight[{target}].probe_identity", payload)
    if record.get("attempt_started_at") is None:
        _fail(f"same-attempt freshness requires attempt_started_at: {target}", payload)
    observed_at = _timestamp(record.get("observed_at"), f"preflight[{target}].observed_at", payload)
    started_at = _timestamp(record.get("attempt_started_at"), f"preflight[{target}].attempt_started_at", payload)
    if observed_at < started_at:
        _fail(f"stale preflight observation precedes the attempt start: {target}", payload)
    _sha256(record.get("evidence_digest"), f"preflight[{target}].evidence_digest", payload)
    observations = _mapping(record.get("observations"), f"preflight[{target}].observations", payload)
    status = _classify_observations(observations, reached, target, payload)
    declared = _text(record.get("status"), f"preflight[{target}].status", payload)
    if declared != status:
        _fail(f"preflight status contradicts its typed layer observations: {target}", payload)
    if status == READY and effective_state != "allowed":
        _fail(f"ready preflight requires host-observed external-read state=allowed: {target}", payload)
    if status != READY and effective_state == "allowed":
        _fail(f"non-ready preflight cannot have effective external-read state=allowed: {target}", payload)
    if policy == "optional":
        _validate_optional_non_claim(target, status, effective_state, non_claim, payload)
    return status


def _validate_optional_non_claim(
    target: str,
    status: str,
    effective_state: str,
    non_claim: dict[str, str] | None,
    payload: dict[str, Any],
) -> None:
    if status == READY:
        if non_claim is not None:
            _fail(f"ready optional target cannot carry an unavailable non-claim: {target}", payload)
        return
    expected_disposition = "unproved" if effective_state == "unproved" else "unavailable"
    if non_claim is None:
        _fail(f"optional unavailable/unproved target lacks an explicit non-claim: {target}", payload)
    if non_claim["disposition"] != expected_disposition:
        _fail(f"optional target non-claim disposition contradicts its observation: {target}", payload)


def _timestamp(value: object, label: str, payload: dict[str, Any]) -> datetime:
    text = _text(value, label, payload)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        _fail(f"{label} must be a valid ISO-8601 timestamp", payload)
        raise AssertionError("unreachable") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"{label} must include a timezone", payload)
    return parsed.astimezone(timezone.utc)


def _classify_observations(
    observations: dict[str, Any], reached: str, target: str, payload: dict[str, Any]
) -> str:
    unknown = set(observations) - set(_OBSERVATION_STATUSES)
    if unknown:
        _fail(f"unknown preflight observation layer(s) for {target}: {sorted(unknown)}", payload)
    normalized: dict[str, str] = {}
    for layer, value in observations.items():
        item = _mapping(value, f"preflight[{target}].observations.{layer}", payload)
        status = _text(item.get("status"), f"preflight[{target}].observations.{layer}.status", payload)
        if status not in _OBSERVATION_STATUSES[layer]:
            _fail(f"unknown {layer} observation status for {target}: {status}", payload)
        normalized[layer] = status

    def require(expected: dict[str, str], *, layer: str) -> None:
        if any(normalized.get(key) != value for key, value in expected.items()):
            _fail(f"contradictory or incomplete {layer} preflight observations for {target}", payload)

    if normalized.get("transport") == "unestablished":
        if set(normalized) != {"transport"} or reached != "none":
            _fail(f"transport-unestablished must stop at reached_layer=none for {target}", payload)
        return "transport-unestablished"
    if normalized.get("identity") == "rejected":
        require({"transport": "established", "identity": "rejected"}, layer="credential")
        if set(normalized) != {"transport", "identity"} or reached != "transport":
            _fail(f"credential-invalid must follow transport and stop before scope for {target}", payload)
        return "credential-invalid"
    if normalized.get("authorization") == "insufficient":
        require(
            {"transport": "established", "identity": "established", "authorization": "insufficient"},
            layer="authorization",
        )
        if set(normalized) != {"transport", "identity", "authorization"} or reached != "identity":
            _fail(f"authorization-insufficient must follow identity for {target}", payload)
        return "authorization-insufficient"
    if normalized.get("provider-response") == "unavailable":
        require(
            {
                "transport": "established",
                "identity": "established",
                "authorization": "allowed",
                "provider-response": "unavailable",
            },
            layer="provider",
        )
        if set(normalized) != {"transport", "identity", "authorization", "provider-response"} or reached != "provider-response":
            _fail(f"provider-unavailable must record the preceding layers for {target}", payload)
        return "provider-unavailable"
    require(
        {
            "transport": "established",
            "identity": "established",
            "authorization": "allowed",
            "provider-response": "ready",
        },
        layer="ready",
    )
    if set(normalized) != {"transport", "identity", "authorization", "provider-response"} or reached != "provider-response":
        _fail(f"ready preflight must reach provider-response for {target}", payload)
    return READY
