"""Direct seam tests for the worker-facing capability lifecycle owner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skills.shared.scripts.reviewer_capability import (
    envelope_sha256,
    non_claims_sha256,
    target_non_claim,
)
from skills.shared.scripts.reviewer_worker_capability import (
    CapabilityLifecycleError,
    adapt_failure,
    collect,
    launch,
    receipt_fields,
    validate_result_non_claims,
)
from tests.quality_gates.reviewer_capability_support import ready_capability


def test_worker_capability_launch_translates_refusal_and_preserves_typed_status(tmp_path: Path) -> None:
    path = tmp_path / "capability.json"
    payload = ready_capability("attempt-1")
    payload["effective_capabilities"]["external_reads"]["state"] = "unproved"
    payload["effective_capabilities"]["external_reads"]["entries"][0]["state"] = "unproved"
    payload["preflight"][0].update(
        {
            "status": "transport-unestablished",
            "reached_layer": "none",
            "observations": {"transport": {"status": "unestablished"}},
        }
    )
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(CapabilityLifecycleError) as refused:
        launch(path, attempt_id="attempt-1")

    assert refused.value.status == "transport-unestablished"
    assert refused.value.payload is not None


def test_worker_capability_collection_drift_is_adapted_without_rebinding_launch(tmp_path: Path) -> None:
    path = tmp_path / "capability.json"
    payload = ready_capability("attempt-1")
    path.write_text(json.dumps(payload), encoding="utf-8")
    state = launch(path, attempt_id="attempt-1")
    path.write_text(json.dumps({**payload, "effective_capabilities": {
        **payload["effective_capabilities"], "configuration_identity": "fixture-config-2"
    }}), encoding="utf-8")

    with pytest.raises(CapabilityLifecycleError) as drift:
        collect(state, path, attempt_id="attempt-1")

    assert drift.value.status == "probe-invalid"
    assert drift.value.adapt_capability is True
    adapted = adapt_failure(state, drift.value)
    assert adapted.status == "probe-invalid"
    assert adapted.launch_envelope_sha256 == state.launch_envelope_sha256
    assert adapted.collection_envelope_sha256 == envelope_sha256(adapted.payload)
    assert adapted.collection_envelope_sha256 != adapted.launch_envelope_sha256


def test_worker_capability_result_mismatch_and_receipt_fields_cross_the_seam(tmp_path: Path) -> None:
    payload = ready_capability("attempt-1")
    path = tmp_path / "capability.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    state = launch(path, attempt_id="attempt-1")

    result = {
        "capability_non_claims": [target_non_claim("github:issue:690", "unproved")],
        "capability_non_claims_sha256": non_claims_sha256(
            [target_non_claim("github:issue:690", "unproved")]
        ),
    }
    with pytest.raises(CapabilityLifecycleError) as mismatch:
        validate_result_non_claims(result, state)

    assert mismatch.value.status == "schema-invalid"
    assert mismatch.value.adapt_capability is False
    fields = receipt_fields(state)
    assert fields["capability_status"] == "ready"
    assert fields["capability_envelope_sha256"] == state.launch_envelope_sha256
    assert fields["capability_launch_envelope_sha256"] == state.launch_envelope_sha256
    assert fields["capability_collection_envelope_sha256"] == state.collection_envelope_sha256
