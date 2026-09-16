"""Executable proof for the declarative semantic coverage floor (#819).

A schema-valid bounded-review result must not pass on shape alone once the
author declares the admitted target set. These controls pin the three
failure classes apart: tool/delivery failure (outside this module), schema
failure (ReviewerResultError), and thin-but-valid results
(ReviewerCoverageError).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skills.shared.scripts.reviewer_result_contract import (
    ReviewerCoverageError,
    ReviewerResultError,
    validate_bounded_result,
)

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
