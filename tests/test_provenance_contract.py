from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import staged_commit_gate_plan
from skills.shared.scripts import provenance_contract as contract
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
CHECKER = load_script_module(
    "check_provenance_contract_under_test",
    ROOT / "skills/public/quality/scripts/check_provenance_contract.py",
)


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


def test_staged_gate_plan_triggers_on_contract_fixture_changes() -> None:
    gates = staged_commit_gate_plan._timing_layer_gates(
        ROOT,
        ["tests/test_capability_catalog.py"],
        existing=["tests/test_capability_catalog.py"],
    )
    assert "check-provenance-contract" in [gate.label for gate in gates]


def test_contract_checker_executes_source_fixtures_in_process() -> None:
    result = run_loaded_script_main(
        "check_provenance_contract.py", CHECKER, "--repo-root", str(ROOT)
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0
    assert payload["proof_level"] == "executable-fixtures"
    assert [item["status"] for item in payload["fixture_results"]] == [
        "passed"
    ] * 4


def test_contract_checker_marks_plugin_layout_shape_only() -> None:
    result = run_loaded_script_main(
        "check_provenance_contract.py",
        CHECKER,
        "--repo-root",
        str(ROOT / "plugins/charness"),
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0
    assert payload["proof_level"] == "shape-only"
    assert payload["fixture_results"] == []
    assert payload["non_claims"]


def test_contract_checker_reports_fixture_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(*args: object, **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(cmd="pytest", timeout=60)

    monkeypatch.setattr(CHECKER.subprocess, "run", timeout)
    result = run_loaded_script_main(
        "check_provenance_contract.py", CHECKER, "--repo-root", str(ROOT)
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["fixture_results"][0]["status"] == "timeout"
    assert payload["errors"]


def test_contract_checker_reports_fixture_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailedResult:
        returncode = 1
        stdout = ""
        stderr = "fixture failed"

    monkeypatch.setattr(CHECKER.subprocess, "run", lambda *args, **kwargs: FailedResult())
    result = run_loaded_script_main(
        "check_provenance_contract.py", CHECKER, "--repo-root", str(ROOT)
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["fixture_results"][0]["status"] == "failed"
    assert "fixture failed" in payload["errors"][0]
