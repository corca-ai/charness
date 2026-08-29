"""Executable proof for the host-neutral external-worker capability contract."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest

from skills.shared.scripts.reviewer_capability import (
    CapabilityError,
    join_result_capability_non_claims,
    non_claims_sha256,
    target_non_claim,
    validate_capability_envelope,
    validate_result_capability_non_claims,
)
from skills.shared.scripts.reviewer_result_contract import (
    RUNNER_JOINED_FIELDS,
    canonical_schema_path,
    model_authored_schema,
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


# --- #755: the runner owns capability provenance, not the reviewer model -------
#
# Ceal ran the canonical file-backed critique path three times against 8.0.0. Every
# reviewer returned substantive bounded-review JSON and every delivery was rejected
# on these two fields alone. Each case below is one of those three attempts, plus
# the non-empty-envelope case the issue asks for.


def _semantic_result() -> dict:
    """What a reviewer model legitimately authors: findings, verdict, next move."""
    return {
        "kind": "charness.bounded_review.v1",
        "lens": "contract",
        "verdict": "block",
        "findings": [
            {
                "id": "F1",
                "severity": "high",
                "summary": "the delivery path rejects on a field the worker cannot author",
                "evidence": ["skills/shared/scripts/reviewer_capability.py"],
                "action": "join provenance deterministically",
            }
        ],
        "counterweight_triage": [],
        "next_move": "join the launch envelope provenance before validation",
        "non_claims": ["did not execute the reviewed code"],
    }


def test_join_repairs_a_model_computed_digest_of_an_empty_envelope() -> None:
    """Attempt 1: envelope `[]`, model returned `[]` with a wrong digest."""
    payload = ready_capability("attempt-1")
    payload["capability_non_claims"] = []
    result = _semantic_result() | {
        "capability_non_claims": [],
        # The exact wrong digest from the issue: a hand-computed variant of `[]`.
        "capability_non_claims_sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e6a69b3e8e1a36c13b920c6",
    }
    with pytest.raises(CapabilityError, match="digest does not match"):
        validate_result_capability_non_claims(result, payload)

    joined = join_result_capability_non_claims(result, payload)
    validate_result_capability_non_claims(joined, payload)
    assert joined["capability_non_claims_sha256"] == non_claims_sha256([])


def test_join_replaces_a_non_claim_the_model_invented() -> None:
    """Attempt 2: envelope `[]`, model invented external-read non-claims.

    Replaced rather than merged: a model-authored non-claim asserts something about
    what the HOST granted, which the model never observed.
    """
    payload = ready_capability("attempt-1")
    payload["capability_non_claims"] = []
    invented = [target_non_claim("github:issue:689", "unproved"), target_non_claim("notion:page:1", "unproved")]
    result = _semantic_result() | {
        "capability_non_claims": invented,
        "capability_non_claims_sha256": non_claims_sha256(invented),
    }
    with pytest.raises(CapabilityError, match="do not match"):
        validate_result_capability_non_claims(result, payload)

    joined = join_result_capability_non_claims(result, payload)
    assert joined["capability_non_claims"] == []
    validate_result_capability_non_claims(joined, payload)


def test_join_repairs_the_sha256_of_empty_bytes() -> None:
    """Attempt 3: model returned the SHA-256 of empty bytes, not of `[]`."""
    payload = ready_capability("attempt-1")
    payload["capability_non_claims"] = []
    result = _semantic_result() | {
        "capability_non_claims": [],
        "capability_non_claims_sha256": (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
    }
    with pytest.raises(CapabilityError, match="digest does not match"):
        validate_result_capability_non_claims(result, payload)
    validate_result_capability_non_claims(
        join_result_capability_non_claims(result, payload), payload
    )


def test_join_copies_non_empty_launch_non_claims_into_the_result() -> None:
    """The envelope carrying real non-claims is the case the join must not flatten."""
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

    # The model omitted them entirely, which is what the model-facing schema now asks for.
    joined = join_result_capability_non_claims(_semantic_result(), payload)
    assert [claim["logical_target"] for claim in joined["capability_non_claims"]] == [target]
    validate_result_capability_non_claims(joined, payload)


def test_join_cannot_alter_semantic_findings() -> None:
    """Provenance joining touches exactly two fields and never the review itself."""
    payload = ready_capability("attempt-1")
    payload["capability_non_claims"] = []
    original = _semantic_result()
    joined = join_result_capability_non_claims(original, payload)

    assert set(joined) - set(original) == {
        "capability_non_claims",
        "capability_non_claims_sha256",
    }
    for field in original:
        assert joined[field] == original[field]
    # ...and the input is not mutated, so a caller keeping the model's own bytes
    # for the record still has them.
    assert "capability_non_claims" not in original


def test_model_facing_schema_drops_exactly_the_runner_joined_fields() -> None:
    """The generation contract must stop asking for digests a model cannot compute."""
    canonical = json.loads(canonical_schema_path().read_text(encoding="utf-8"))
    projected = model_authored_schema(canonical)

    assert set(canonical["required"]) - set(projected["required"]) == set(RUNNER_JOINED_FIELDS)
    assert set(canonical["properties"]) - set(projected["properties"]) == set(RUNNER_JOINED_FIELDS)
    # Everything a reviewer actually authors survives the projection.
    assert "findings" in projected["properties"]
    assert "verdict" in projected["required"]
    # The canonical schema is not mutated by projecting it.
    assert set(canonical["required"]) >= set(RUNNER_JOINED_FIELDS)


def test_a_joined_result_satisfies_the_canonical_schema() -> None:
    """The projection relaxes GENERATION only; the delivered artifact is unchanged."""
    jsonschema = pytest.importorskip("jsonschema")
    canonical = json.loads(canonical_schema_path().read_text(encoding="utf-8"))
    payload = ready_capability("attempt-1")
    payload["capability_non_claims"] = []

    model_output = _semantic_result() | {
        "packet_sha256": "a" * 64,
        "reviewed_input_identity_sha256": "b" * 64,
    }
    # The model's own output does NOT satisfy the canonical schema -- that is the
    # whole point of the projection -- and the joined result does.
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validators.validator_for(canonical)(canonical).validate(model_output)
    joined = join_result_capability_non_claims(model_output, payload)
    jsonschema.validators.validator_for(canonical)(canonical).validate(joined)
