"""Executable proof for the host-neutral external-worker capability contract."""

from __future__ import annotations

from copy import deepcopy

import pytest

from skills.shared.scripts.reviewer_capability import (
    CapabilityError,
    non_claims_sha256,
    target_non_claim,
    validate_capability_envelope,
    validate_result_capability_non_claims,
)
from tests.quality_gates.reviewer_capability_support import ready_capability


def _set_preflight(payload: dict, *, status: str, reached: str, observations: dict) -> None:
    record = payload["preflight"][0]
    record["status"] = status
    record["reached_layer"] = reached
    record["observations"] = observations
    if status != "ready":
        payload["effective_capabilities"]["external_reads"]["state"] = "unproved"
        for entry in payload["effective_capabilities"]["external_reads"]["entries"]:
            entry["state"] = "unproved"


def test_ready_requires_explicit_write_and_effect_denial() -> None:
    decision = validate_capability_envelope(ready_capability("attempt-1"), attempt_id="attempt-1", require_ready=True)
    assert decision.status == "ready"
    assert decision.payload["effective_capabilities"]["filesystem"]["write"] == "denied"
    assert decision.payload["effective_capabilities"]["external_effects"]["state"] == "denied"


def test_transport_failure_cannot_become_credential_invalid() -> None:
    payload = ready_capability("attempt-1")
    _set_preflight(
        payload,
        status="transport-unestablished",
        reached="none",
        observations={"transport": {"status": "unestablished"}},
    )
    decision = validate_capability_envelope(payload, attempt_id="attempt-1")
    assert decision.status == "transport-unestablished"
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1", require_ready=True)
    assert refused.value.status == "transport-unestablished"


def test_credential_invalid_is_valid_only_after_transport() -> None:
    payload = ready_capability("attempt-1")
    _set_preflight(
        payload,
        status="credential-invalid",
        reached="transport",
        observations={
            "transport": {"status": "established"},
            "identity": {"status": "rejected"},
        },
    )
    assert validate_capability_envelope(payload, attempt_id="attempt-1").status == "credential-invalid"

    missing_transport = deepcopy(payload)
    missing_transport["preflight"][0]["observations"] = {"identity": {"status": "rejected"}}
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(missing_transport, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_authorization_insufficient_is_valid_only_after_identity() -> None:
    payload = ready_capability("attempt-1")
    _set_preflight(
        payload,
        status="authorization-insufficient",
        reached="identity",
        observations={
            "transport": {"status": "established"},
            "identity": {"status": "established"},
            "authorization": {"status": "insufficient"},
        },
    )
    assert validate_capability_envelope(payload, attempt_id="attempt-1").status == "authorization-insufficient"

    missing_identity = deepcopy(payload)
    missing_identity["preflight"][0]["observations"].pop("identity")
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(missing_identity, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_provider_unavailable_preserves_all_preceding_layers() -> None:
    payload = ready_capability("attempt-1")
    _set_preflight(
        payload,
        status="provider-unavailable",
        reached="provider-response",
        observations={
            "transport": {"status": "established"},
            "identity": {"status": "established"},
            "authorization": {"status": "allowed"},
            "provider-response": {"status": "unavailable"},
        },
    )
    assert validate_capability_envelope(payload, attempt_id="attempt-1").status == "provider-unavailable"


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("missing filesystem denial", lambda p: p["effective_capabilities"]["filesystem"].pop("write")),
        ("unproved filesystem denial", lambda p: p["effective_capabilities"]["filesystem"].update(write="unproved")),
        ("missing effect denial", lambda p: p["effective_capabilities"]["external_effects"].pop("state")),
        ("effect allow contradiction", lambda p: p["effective_capabilities"]["external_effects"].update(state="allowed")),
        ("missing effect policy", lambda p: p["requested_capabilities"]["external_effects"].pop("policy")),
        ("sandbox label does not grant", lambda p: p["effective_capabilities"]["filesystem"].update(write="allowed")),
    ],
)
def test_missing_or_contradictory_denial_fails_closed(label: str, mutate) -> None:
    payload = ready_capability("attempt-1")
    mutate(payload)
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid", label


def test_preflight_attempt_and_target_are_join_keys() -> None:
    payload = ready_capability("attempt-foreign")
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_duplicate_preflight_records_are_not_ambiguous_success() -> None:
    payload = ready_capability("attempt-1")
    payload["preflight"].append(deepcopy(payload["preflight"][0]))
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_deny_all_external_read_cannot_become_allowed_or_have_preflight() -> None:
    payload = ready_capability("attempt-1")
    denied_target = "github:issue:private"
    payload["requested_capabilities"]["external_reads"].append(
        {
            "capability": "github.issue.read",
            "policy": "deny-all",
            "logical_target": denied_target,
            "probe_type": "transport-and-provider",
            "target_class": "github",
            "freshness": "same-attempt",
        }
    )
    payload["effective_capabilities"]["external_reads"]["entries"].append(
        {"logical_target": denied_target, "state": "allowed", "observation": "host"}
    )
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"

    payload = ready_capability("attempt-1")
    payload["requested_capabilities"]["external_reads"].append(
        {
            "capability": "github.issue.read",
            "policy": "deny-all",
            "logical_target": denied_target,
            "probe_type": "transport-and-provider",
            "target_class": "github",
            "freshness": "same-attempt",
        }
    )
    payload["effective_capabilities"]["external_reads"]["state"] = "unproved"
    payload["effective_capabilities"]["external_reads"]["entries"].append(
        {"logical_target": denied_target, "state": "denied", "observation": "host"}
    )
    payload["preflight"].append(deepcopy(payload["preflight"][0]))
    payload["preflight"][1]["logical_target"] = denied_target
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_optional_unavailable_is_ready_only_with_an_explicit_non_claim() -> None:
    target = "github:issue:689"
    payload = ready_capability("attempt-1", target=target)
    payload["requested_capabilities"]["external_reads"][0]["policy"] = "optional"
    _set_preflight(
        payload,
        status="transport-unestablished",
        reached="none",
        observations={"transport": {"status": "unestablished"}},
    )
    payload["capability_non_claims"] = [target_non_claim(target, "unproved")]
    decision = validate_capability_envelope(payload, attempt_id="attempt-1", require_ready=True)
    assert decision.status == "ready"

    payload["capability_non_claims"] = []
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1", require_ready=True)
    assert refused.value.status == "probe-invalid"


def test_optional_non_claim_rejects_contradictory_prose_instead_of_matching_substrings() -> None:
    payload = ready_capability("attempt-1", target="github:issue:689")
    payload["requested_capabilities"]["external_reads"][0]["policy"] = "optional"
    _set_preflight(
        payload,
        status="transport-unestablished",
        reached="none",
        observations={"transport": {"status": "unestablished"}},
    )
    payload["capability_non_claims"] = [
        "github:issue:689 unavailable; remote evidence claim IS made"
    ]
    with pytest.raises(CapabilityError, match="capability_non_claims") as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("statement", "No evidence claim is made for github:issue:689; scope is broader."),
        ("scope", "all-evidence"),
    ],
)
def test_optional_non_claim_wording_and_scope_are_canonical(field: str, value: str) -> None:
    target = "github:issue:689"
    payload = ready_capability("attempt-1", target=target)
    payload["requested_capabilities"]["external_reads"][0]["policy"] = "optional"
    _set_preflight(
        payload,
        status="transport-unestablished",
        reached="none",
        observations={"transport": {"status": "unestablished"}},
    )
    claim = target_non_claim(target, "unproved")
    claim[field] = value
    payload["capability_non_claims"] = [claim]
    with pytest.raises(CapabilityError, match="canonical") as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_optional_non_claim_ready_target_cannot_rebound_to_unavailable() -> None:
    target = "github:issue:689"
    payload = ready_capability("attempt-1", target=target)
    payload["requested_capabilities"]["external_reads"][0]["policy"] = "optional"
    payload["capability_non_claims"] = [target_non_claim(target, "unproved")]
    with pytest.raises(CapabilityError, match="ready optional") as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_result_must_repeat_the_exact_target_bound_non_claim_identity() -> None:
    target = "github:issue:689"
    payload = ready_capability("attempt-1", target=target)
    payload["requested_capabilities"]["external_reads"][0]["policy"] = "optional"
    _set_preflight(
        payload,
        status="transport-unestablished",
        reached="none",
        observations={"transport": {"status": "unestablished"}},
    )
    payload["capability_non_claims"] = [target_non_claim(target, "unproved")]
    validate_capability_envelope(payload, attempt_id="attempt-1", require_ready=True)
    result = {
        "capability_non_claims": payload["capability_non_claims"],
        "capability_non_claims_sha256": non_claims_sha256(payload["capability_non_claims"]),
    }
    validate_result_capability_non_claims(result, payload)

    result["capability_non_claims"] = []
    result["capability_non_claims_sha256"] = non_claims_sha256([])
    with pytest.raises(CapabilityError, match="do not match"):
        validate_result_capability_non_claims(result, payload)

    result["capability_non_claims"] = [target_non_claim("github:issue:690", "unproved")]
    result["capability_non_claims_sha256"] = non_claims_sha256(result["capability_non_claims"])
    with pytest.raises(CapabilityError, match="do not match"):
        validate_result_capability_non_claims(result, payload)


def test_external_read_policy_duplicates_are_rejected_even_when_targets_match() -> None:
    payload = ready_capability("attempt-1")
    duplicate = deepcopy(payload["requested_capabilities"]["external_reads"][0])
    duplicate["policy"] = "optional"
    payload["requested_capabilities"]["external_reads"].append(duplicate)
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("observed_at", "yesterday"),
        ("observed_at", "2026-08-24T00:00:00"),
        ("attempt_started_at", "not-a-timestamp"),
    ],
)
def test_preflight_timestamps_are_typed_and_timezone_bound(field: str, value: str) -> None:
    payload = ready_capability("attempt-1")
    payload["preflight"][0][field] = value
    with pytest.raises(CapabilityError) as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_preflight_observation_before_attempt_start_is_stale() -> None:
    payload = ready_capability("attempt-1")
    payload["preflight"][0]["attempt_started_at"] = "2026-08-24T00:00:01Z"
    with pytest.raises(CapabilityError, match="stale") as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


@pytest.mark.parametrize("observed_at", ["2099-01-01T00:00:00Z", "1970-01-01T00:00:00Z"])
def test_live_freshness_is_rejected_without_host_attested_window(observed_at: str) -> None:
    payload = ready_capability("attempt-1")
    payload["requested_capabilities"]["external_reads"][0]["freshness"] = "live"
    payload["preflight"][0]["observed_at"] = observed_at
    with pytest.raises(CapabilityError, match="freshness") as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"


def test_same_attempt_freshness_requires_an_attempt_start_witness() -> None:
    payload = ready_capability("attempt-1")
    payload["preflight"][0].pop("attempt_started_at")
    with pytest.raises(CapabilityError, match="attempt_started_at") as refused:
        validate_capability_envelope(payload, attempt_id="attempt-1")
    assert refused.value.status == "probe-invalid"
