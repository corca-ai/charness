"""Executable proof for the declarative semantic coverage floor (#819).

A schema-valid bounded-review result must not pass on shape alone once the
author declares the admitted target set. These controls pin the three
failure classes apart: tool/delivery failure (outside this module), schema
failure (ReviewerResultError), and thin-but-valid results
(ReviewerCoverageError).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from skills.shared.scripts import reviewer_delivery as delivery
from skills.shared.scripts.reviewer_capability import (
    non_claims_sha256,
    validate_capability_envelope,
)
from skills.shared.scripts.reviewer_result_contract import (
    ReviewerCoverageError,
    ReviewerResultError,
    declared_targets_digest,
    validate_bounded_result,
)
from skills.shared.scripts.reviewer_worker_carrier_support import (
    WorkerCarrierError,
    validate_delivered_worker_report,
)
from skills.shared.scripts.reviewer_worker_report import build_report
from skills.shared.scripts import reviewer_runner_support
from tests.quality_gates.reviewer_capability_support import ready_capability

PACKET = "a" * 64
INPUT = "b" * 64
TARGETS = ["packet-target-alpha", "packet-target-beta"]


def _observation(target: str, *, verdict: str = "pass") -> dict:
    return {
        "target": target,
        "verdict": verdict,
        "summary": f"observed {target}",
        "evidence": [f"evidence for {target}"],
    }


def _result(**overrides: object) -> dict:
    payload: dict[str, object] = {
        "kind": "charness.bounded_review.v1",
        "lens": "contract",
        "packet_sha256": PACKET,
        "reviewed_input_identity_sha256": INPUT,
        "verdict": "pass",
        "findings": [],
        "target_observations": None,
        "counterweight_triage": [],
        "next_move": "no further move",
        "non_claims": [],
        "capability_non_claims": [],
        "capability_non_claims_sha256": "c" * 64,
    }
    payload.update(overrides)
    return payload


def _validate(payload: dict, tmp_path: Path, **kwargs: object) -> dict:
    path = tmp_path / "result.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return validate_bounded_result(
        path,
        packet_identity=PACKET,
        reviewed_input_identity=INPUT,
        require_pass=False,
        **kwargs,
    )


def test_declared_floor_accepts_full_coverage(tmp_path: Path) -> None:
    payload = _result(target_observations=[_observation(t) for t in TARGETS])
    assert _validate(payload, tmp_path, expected_targets=TARGETS)["verdict"] == "pass"


def test_undeclared_floor_accepts_target_free_pass(tmp_path: Path) -> None:
    """Null observations with no declared targets stay valid aggregation."""
    assert _validate(_result(), tmp_path)["verdict"] == "pass"


def test_declared_floor_rejects_dummy_valid_shape(tmp_path: Path) -> None:
    """The #819 hole: pass + empty findings + no observations must not slide through."""
    with pytest.raises(ReviewerCoverageError, match="none of the 2 expected targets"):
        _validate(_result(), tmp_path, expected_targets=TARGETS)


def test_declared_floor_rejects_partial_coverage(tmp_path: Path) -> None:
    payload = _result(target_observations=[_observation(TARGETS[0])])
    with pytest.raises(ReviewerCoverageError, match=TARGETS[1]):
        _validate(payload, tmp_path, expected_targets=TARGETS)


def test_coverage_is_verdict_agnostic(tmp_path: Path) -> None:
    """A block that observes every target is still a delivered finding."""
    payload = _result(
        verdict="block",
        target_observations=[_observation(t, verdict="block") for t in TARGETS],
    )
    assert _validate(payload, tmp_path, expected_targets=TARGETS)["verdict"] == "block"


def test_schema_failure_stays_schema_class(tmp_path: Path) -> None:
    payload = _result(kind="wrong.kind", target_observations=[_observation(t) for t in TARGETS])
    with pytest.raises(ReviewerResultError) as exc:
        _validate(payload, tmp_path, expected_targets=TARGETS)
    assert type(exc.value) is ReviewerResultError


def test_coverage_error_is_exact_class(tmp_path: Path) -> None:
    with pytest.raises(ReviewerCoverageError) as exc:
        _validate(_result(), tmp_path, expected_targets=TARGETS)
    assert type(exc.value) is ReviewerCoverageError


@pytest.mark.parametrize("declared", [[], ["t1", "t1"], ["ok", ""], "not-a-list"])
def test_malformed_declaration_is_author_error(tmp_path: Path, declared: object) -> None:
    payload = _result(target_observations=[_observation("ok")])
    with pytest.raises(ReviewerResultError) as exc:
        _validate(payload, tmp_path, expected_targets=declared)
    assert type(exc.value) is ReviewerResultError


@pytest.mark.parametrize(
    "observations",
    [
        [{"target": "t1", "verdict": "pass", "summary": "   ", "evidence": ["e"]}],
        [{"target": "t1", "verdict": "pass", "summary": "s", "evidence": ["  "]}],
        [
            {"target": "t1", "verdict": "pass", "summary": "s", "evidence": ["e"]},
            {"target": "t1", "verdict": "pass", "summary": "s", "evidence": ["e"]},
        ],
    ],
)
def test_observations_need_substance_and_singularity(
    tmp_path: Path, observations: object
) -> None:
    payload = _result(target_observations=observations)
    with pytest.raises(ReviewerCoverageError):
        _validate(payload, tmp_path, expected_targets=["t1"])


def test_empty_evidence_fails_at_schema_layer_first(tmp_path: Path) -> None:
    """Shape violations stay schema-class: coverage only judges schema-valid results."""
    payload = _result(
        target_observations=[
            {"target": "t1", "verdict": "pass", "summary": "s", "evidence": []}
        ]
    )
    with pytest.raises(ReviewerResultError) as exc:
        _validate(payload, tmp_path, expected_targets=["t1"])
    assert type(exc.value) is ReviewerResultError


def test_coverage_error_stays_compatible_with_value_handlers() -> None:
    assert issubclass(ReviewerCoverageError, ReviewerResultError)
    assert issubclass(ReviewerCoverageError, ValueError)


_E2E_ATTEMPT = "attempt-e2e"
_E2E_SCOPE = "e2e-scope"
_E2E_PARENT = "receipt-e2e"
_E2E_BACKEND = "e2e-backend"
_E2E_TARGETS = ["packet-target-alpha", "packet-target-beta"]


def _e2e_result(*, observations: object) -> dict:
    digest = non_claims_sha256([])
    return _result(
        target_observations=observations,
        capability_non_claims=[],
        capability_non_claims_sha256=digest,
    )


def _e2e_envelope() -> tuple[dict, str]:
    env = ready_capability(_E2E_ATTEMPT)
    decision = validate_capability_envelope(
        {
            "schema_version": env["schema_version"],
            "task_kind": "read",
            "requested_capabilities": env["requested_capabilities"],
            "effective_capabilities": env["effective_capabilities"],
            "preflight": env["preflight"],
            "capability_non_claims": [],
        },
        attempt_id=_E2E_ATTEMPT,
        require_ready=True,
    )
    return env, decision


def _e2e_files(
    tmp_path: Path,
    result_payload: dict,
    *,
    floor: list[str] | None = None,
    findings: bool = True,
) -> dict:
    """Fabricate a consistent report/receipt/ledger triple via public APIs.

    ``floor`` is the coverage set the collection declared: its digest is
    recorded in the ledger attempt, the report, and the report provenance —
    the three sides the durable join requires to agree. ``findings=False``
    leaves the attempt started but unrecorded, for tests that drive the real
    collection path themselves.
    """
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(result_payload), encoding="utf-8")
    output_hash = hashlib.sha256(result_path.read_bytes()).hexdigest()
    output_size = result_path.stat().st_size
    env, decision = _e2e_envelope()
    digest = non_claims_sha256([])
    receipt = {
        "schema_version": "charness.reviewer_worker.v1",
        "status": "succeeded",
        "terminal": True,
        "exit_code": 0,
        "output_fresh": True,
        "output_sha256": output_hash,
        "output_size": output_size,
        "requested_capabilities": env["requested_capabilities"],
        "effective_capabilities": env["effective_capabilities"],
        "preflight": env["preflight"],
        "capability_non_claims": [],
        "capability_non_claims_sha256": digest,
        "capability_status": decision.status,
        "capability_envelope_sha256": decision.envelope_sha256,
        "capability_launch_envelope_sha256": decision.envelope_sha256,
        "capability_collection_envelope_sha256": decision.envelope_sha256,
        "attempt_id": _E2E_ATTEMPT,
        "scope": _E2E_SCOPE,
        "packet_identity": PACKET,
        "reviewed_input_identity": INPUT,
        "parent_receipt_identity": _E2E_PARENT,
        "boundary_mode": "read-only-worker",
        "execution_mode": "file-backed-worker",
        "backend": _E2E_BACKEND,
        "prompt_sha256": "e" * 64,
        "schema_sha256": "f" * 64,
        "run_id": "run-e2e",
        "output_file": str(result_path),
        "receipt_file": str(tmp_path / "receipt.json"),
        "producer_run_id": "run-e2e",
    }
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    ledger = delivery.DeliveryLedger.empty()
    ledger.start(
        attempt_id=_E2E_ATTEMPT,
        scope=_E2E_SCOPE,
        packet_identity=PACKET,
        parent_receipt_identity=_E2E_PARENT,
        recorded_at="2026-09-16T00:00:00Z",
        boundary_mode="read-only-worker",
        reviewed_input_identity=INPUT,
        execution_mode="file-backed-worker",
        backend=_E2E_BACKEND,
        prompt_sha256="e" * 64,
        schema_sha256="f" * 64,
        capability_launch_envelope_sha256=decision.envelope_sha256,
        output_file=str(result_path),
        receipt_file=str(receipt_path),
        producer_run_id="run-e2e",
    )
    ledger.require(_E2E_ATTEMPT).transition(
        delivery.RUNNING, "reviewer started", "2026-09-16T00:00:10Z"
    )
    floor_digest = declared_targets_digest(floor)
    if findings:
        assert ledger.require(_E2E_ATTEMPT).record_findings(
            scope=_E2E_SCOPE,
            packet_identity=PACKET,
            parent_receipt_identity=_E2E_PARENT,
            findings_identity=output_hash,
            recorded_at="2026-09-16T00:01:00Z",
            expected_targets_sha256=floor_digest,
        )
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(ledger.to_dict()), encoding="utf-8")
    report = {
        "schema_version": "charness.reviewer_worker_report.v1",
        "delivery_state": "findings-received",
        "collection_ready": True,
        "provenance_ok": True,
        "receipt_ok": True,
        "ledger_ok": True,
        "result_schema_ok": True,
        "attempt_id": _E2E_ATTEMPT,
        "producer_run_id": "run-e2e",
        "scope": _E2E_SCOPE,
        "packet_identity": PACKET,
        "reviewed_input_identity": INPUT,
        "parent_receipt_identity": _E2E_PARENT,
        "boundary_mode": "read-only-worker",
        "findings_identity": output_hash,
        "receipt_output_sha256": output_hash,
        "receipt_path": "receipt.json",
        "ledger_path": "ledger.json",
        "execution_mode": "file-backed-worker",
        "backend": _E2E_BACKEND,
        "prompt_sha256": "e" * 64,
        "schema_sha256": "f" * 64,
        "capability_launch_envelope_sha256": decision.envelope_sha256,
        "capability_non_claims": [],
        "capability_non_claims_sha256": digest,
        "expected_targets_sha256": floor_digest,
        "provenance": {
            "scope": _E2E_SCOPE,
            "packet_identity": PACKET,
            "reviewed_input_identity": INPUT,
            "parent_receipt_identity": _E2E_PARENT,
            "expected_targets_sha256": floor_digest,
            "attempt_id": _E2E_ATTEMPT,
            "attempt_scope": _E2E_SCOPE,
            "attempt_packet_identity": PACKET,
            "attempt_parent_receipt_identity": _E2E_PARENT,
            "result_packet_identity": PACKET,
            "result_reviewed_input_identity": INPUT,
            "boundary_mode": "read-only-worker",
            "boundary_fingerprint": None,
            "execution_mode": "file-backed-worker",
            "backend": _E2E_BACKEND,
            "prompt_sha256": "e" * 64,
            "schema_sha256": "f" * 64,
            "capability_launch_envelope_sha256": decision.envelope_sha256,
            "capability_non_claims_sha256": digest,
        },
    }
    return {"report": report, "output_hash": output_hash}


def test_collection_carries_the_declared_floor_into_the_report(tmp_path: Path) -> None:
    files = _e2e_files(
        tmp_path,
        _e2e_result(observations=[_observation(t) for t in _E2E_TARGETS]),
        floor=_E2E_TARGETS,
    )
    report = build_report(
        receipt_path=str(tmp_path / "receipt.json"),
        ledger_path=str(tmp_path / "ledger.json"),
        attempt_id=_E2E_ATTEMPT,
        scope=_E2E_SCOPE,
        packet_identity=PACKET,
        reviewed_input_identity=INPUT,
        parent_receipt_identity=_E2E_PARENT,
        expected_targets=_E2E_TARGETS,
    )
    assert report["coverage_ok"] is True
    assert report["expected_targets"] == _E2E_TARGETS
    assert report["expected_targets_sha256"] == declared_targets_digest(_E2E_TARGETS)
    assert files["report"]["findings_identity"] == report["findings_identity"]
    receipt, result, _ = validate_delivered_worker_report(
        repo_root=tmp_path, report=report
    )
    assert result["verdict"] == "pass"


def test_durable_carrier_rejects_a_thin_file_despite_the_report(tmp_path: Path) -> None:
    # A thin file swapped in after collection: the hand-built report models a
    # collection that declared the floor, and the durable boundary must
    # re-enforce it from the carried declaration even with no caller argument.
    files = _e2e_files(tmp_path, _e2e_result(observations=None), floor=_E2E_TARGETS)
    report = files["report"] | {"coverage_ok": True, "expected_targets": list(_E2E_TARGETS)}
    with pytest.raises(WorkerCarrierError, match="expected targets"):
        validate_delivered_worker_report(repo_root=tmp_path, report=report)


def test_durable_carrier_passes_an_undeclared_thin_result(tmp_path: Path) -> None:
    # Opt-in preserved end to end: with no declared floor anywhere, a thin
    # but schema-valid result still delivers.
    files = _e2e_files(tmp_path, _e2e_result(observations=None))
    _, result, _ = validate_delivered_worker_report(
        repo_root=tmp_path, report=files["report"]
    )
    assert result["verdict"] == "pass"


def test_floor_digest_is_order_insensitive_and_absent_when_undeclared() -> None:
    assert declared_targets_digest(None) is None
    assert declared_targets_digest(["b", "a"]) == declared_targets_digest(["a", "b"])
    assert declared_targets_digest(["a"]) != declared_targets_digest(["a", "b"])


def test_floor_digest_rejects_a_malformed_declaration() -> None:
    with pytest.raises(ReviewerResultError, match="malformed expected-target set"):
        declared_targets_digest("not-a-list")


def test_durable_carrier_refuses_a_deleted_declaration(tmp_path: Path) -> None:
    # The ledger attempt and provenance still record the floor digest, so
    # dropping the declaration list from the report refuses instead of
    # silently delivering the thin file with no floor.
    files = _e2e_files(tmp_path, _e2e_result(observations=None), floor=_E2E_TARGETS)
    report = files["report"] | {"coverage_ok": True, "expected_targets": None}
    with pytest.raises(WorkerCarrierError, match="declaration digest"):
        validate_delivered_worker_report(repo_root=tmp_path, report=report)


def test_durable_carrier_refuses_an_altered_declaration(tmp_path: Path) -> None:
    # The result covers the rewritten declaration, so the collection-time
    # check passes and only the durable join can refuse: the joined digest
    # no longer matches the altered list.
    files = _e2e_files(
        tmp_path,
        _e2e_result(observations=[_observation("forged-target")]),
        floor=_E2E_TARGETS,
    )
    report = files["report"] | {"coverage_ok": True, "expected_targets": ["forged-target"]}
    with pytest.raises(WorkerCarrierError, match="declaration digest"):
        validate_delivered_worker_report(repo_root=tmp_path, report=report)


def test_durable_carrier_refuses_a_floor_without_ledger_backing(tmp_path: Path) -> None:
    # The result covers the invented declaration, so the collection-time
    # check passes and only the durable join can refuse: the report cannot
    # invent a floor the ledger attempt never recorded.
    files = _e2e_files(
        tmp_path,
        _e2e_result(observations=[_observation(t) for t in _E2E_TARGETS]),
    )
    report = files["report"] | {
        "coverage_ok": True,
        "expected_targets": list(_E2E_TARGETS),
        "expected_targets_sha256": declared_targets_digest(_E2E_TARGETS),
    }
    with pytest.raises(WorkerCarrierError, match="declaration digest"):
        validate_delivered_worker_report(repo_root=tmp_path, report=report)


def test_durable_carrier_refuses_a_malformed_declaration_with_a_joined_floor(
    tmp_path: Path,
) -> None:
    # The carried list itself is malformed while the digests agree, so the
    # durable boundary refuses as an authoring error rather than enforcing
    # garbage.
    files = _e2e_files(
        tmp_path,
        _e2e_result(observations=[_observation(t) for t in _E2E_TARGETS]),
        floor=_E2E_TARGETS,
    )
    report = files["report"] | {"coverage_ok": True, "expected_targets": "not-a-list"}
    with pytest.raises(WorkerCarrierError, match="malformed expected-target set"):
        validate_delivered_worker_report(repo_root=tmp_path, report=report)


def test_finalize_attempt_binds_the_floor_through_collection(tmp_path: Path) -> None:
    # End to end through the real collection path: finalize_attempt records
    # the floor digest in the ledger attempt, build_report carries it, and
    # the durable boundary validates the joined triple with no caller floor.
    files = _e2e_files(
        tmp_path,
        _e2e_result(observations=[_observation(t) for t in _E2E_TARGETS]),
        floor=None,
        findings=False,
    )
    report = reviewer_runner_support.finalize_attempt(
        receipt_path=tmp_path / "receipt.json",
        ledger_path=tmp_path / "ledger.json",
        attempt_id=_E2E_ATTEMPT,
        scope=_E2E_SCOPE,
        packet_identity=PACKET,
        reviewed_input_identity=INPUT,
        parent_receipt_identity=_E2E_PARENT,
        execution_mode="file-backed-worker",
        build_report=build_report,
        expected_targets=_E2E_TARGETS,
    )
    assert report["collection_ready"] is True
    assert report["expected_targets"] == _E2E_TARGETS
    assert report["expected_targets_sha256"] == declared_targets_digest(_E2E_TARGETS)
    assert files["report"]["findings_identity"] == report["findings_identity"]
    _, result, _ = validate_delivered_worker_report(
        repo_root=tmp_path, report=report
    )
    assert result["verdict"] == "pass"


def test_durable_carrier_refuses_a_tampered_provenance_digest(tmp_path: Path) -> None:
    # Agreement is three-sided: the result covers the rewritten declaration
    # and the provenance digest was edited to match it, yet the ledger
    # attempt still disagrees, so the durable join refuses.
    files = _e2e_files(
        tmp_path,
        _e2e_result(observations=[_observation("forged-target")]),
        floor=_E2E_TARGETS,
    )
    forged = ["forged-target"]
    report = files["report"] | {
        "coverage_ok": True,
        "expected_targets": forged,
        "provenance": files["report"]["provenance"]
        | {"expected_targets_sha256": declared_targets_digest(forged)},
    }
    with pytest.raises(WorkerCarrierError, match="declaration digest"):
        validate_delivered_worker_report(repo_root=tmp_path, report=report)
