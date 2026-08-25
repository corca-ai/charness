from __future__ import annotations

from pathlib import Path

import pytest

from skills.shared.scripts import provenance_contract as contract

ROOT = Path(__file__).resolve().parents[1]


def test_registry_has_one_complete_row_per_reviewed_boundary() -> None:
    assert contract.validate_registry(ROOT) == []
    assert {item.contract_id for item in contract.CONTRACTS} == {
        "reviewer_delivery",
        "lesson_finalization",
        "skill_manifest_selection",
        "duplicate_lineage",
    }


def test_missing_producer_binding_is_typed_and_fail_closed() -> None:
    with pytest.raises(contract.BoundaryContractError, match="receipt_file"):
        contract.require_bound_fields(
            "reviewer_delivery",
            {"output_file": "result.json", "receipt_file": None, "producer_run_id": "run-1"},
        )


@pytest.mark.parametrize("outcome", ["succeeded", "timed-out", "interrupted", "missing"])
def test_lesson_fence_is_required_for_every_terminal_outcome(outcome: str) -> None:
    with pytest.raises(contract.BoundaryContractError, match="requires its fence"):
        contract.require_terminal_fence(
            "lesson_finalization", outcome=outcome, fence_ran=False
        )
    contract.require_terminal_fence("lesson_finalization", outcome=outcome, fence_ran=True)


def test_fixture_references_are_exact_repo_relative_nodes() -> None:
    for item in contract.CONTRACTS:
        path, node = item.negative_fixture.split("::", 1)
        assert not Path(path).is_absolute()
        assert ".." not in Path(path).parts
        assert node
