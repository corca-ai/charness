"""Shared structured capability fixtures for reviewer boundary tests."""

from __future__ import annotations

from skills.shared.scripts.reviewer_capability import (
    envelope_sha256,
    non_claims_sha256,
    target_non_claim,
)

EMPTY_NON_CLAIMS_SHA256 = non_claims_sha256([])


def ready_capability(attempt_id: str, *, target: str = "github:issue:689") -> dict:
    return {
        "schema_version": "charness.capability_envelope.v1",
        "task_kind": "read",
        "requested_capabilities": {
            "filesystem": {
                "read_roots": ["/workspace"],
                "write_policy": "deny-all",
                "write_roots": [],
            },
            "external_reads": [
                {
                    "capability": "github.issue.read",
                    "policy": "required",
                    "logical_target": target,
                    "probe_type": "transport-and-provider",
                    "target_class": "github",
                    "freshness": "same-attempt",
                }
            ],
            "external_effects": {"policy": "deny-all", "entries": []},
        },
        "effective_capabilities": {
            "filesystem": {"write": "denied", "observation": "host"},
        "external_reads": {
            "state": "allowed",
            "observation": "host",
            "entries": [{"logical_target": target, "state": "allowed", "observation": "host"}],
        },
            "external_effects": {"state": "denied", "observation": "host"},
            "host_selection_source": "fixture",
            "sandbox": {"label": "read-only", "source": "host-provenance"},
            "configuration_identity": "fixture-config-1",
        },
        "preflight": [
            {
                "attempt_id": attempt_id,
                "attempt_started_at": "2026-08-24T00:00:00Z",
                "logical_target": target,
                "reached_layer": "provider-response",
                "observations": {
                    "transport": {"status": "established"},
                    "identity": {"status": "established"},
                    "authorization": {"status": "allowed"},
                    "provider-response": {"status": "ready"},
                },
                "status": "ready",
                "probe_identity": "probe-ready-1",
                "observed_at": "2026-08-24T00:00:00Z",
                "evidence_digest": "d" * 64,
            }
        ],
        "capability_non_claims": [],
    }


def unavailable_optional_capability(attempt_id: str, *, target: str = "github:issue:689") -> dict:
    payload = ready_capability(attempt_id, target=target)
    payload["requested_capabilities"]["external_reads"][0]["policy"] = "optional"
    payload["effective_capabilities"]["external_reads"]["state"] = "unproved"
    payload["effective_capabilities"]["external_reads"]["entries"][0]["state"] = "unproved"
    payload["preflight"][0].update(
        {
            "status": "transport-unestablished",
            "reached_layer": "none",
            "observations": {"transport": {"status": "unestablished"}},
        }
    )
    payload["capability_non_claims"] = [target_non_claim(target, "unproved")]
    return payload


def result_capability_fields(payload: dict) -> dict:
    return {
        "capability_non_claims": payload["capability_non_claims"],
        "capability_non_claims_sha256": non_claims_sha256(payload["capability_non_claims"]),
    }


def receipt_capability_fields(
    attempt_id: str,
    *,
    target: str = "github:issue:689",
    payload: dict | None = None,
) -> dict:
    payload = payload or ready_capability(attempt_id, target=target)
    return {
        "capability_status": "ready",
        "capability_envelope_sha256": envelope_sha256(payload),
        "capability_launch_envelope_sha256": envelope_sha256(payload),
        "capability_collection_envelope_sha256": envelope_sha256(payload),
        "requested_capabilities": payload["requested_capabilities"],
        "effective_capabilities": payload["effective_capabilities"],
        "preflight": payload["preflight"],
        "capability_non_claims": payload["capability_non_claims"],
        "capability_non_claims_sha256": non_claims_sha256(payload["capability_non_claims"]),
    }
