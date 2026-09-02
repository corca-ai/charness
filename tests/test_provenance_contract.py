from __future__ import annotations

import runpy
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from scripts import staged_commit_gate_plan
from skills.shared.scripts import provenance_contract as contract
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "skills/public/quality/scripts/check_provenance_contract.py"
CHECKER = load_script_module(
    "check_provenance_contract_under_test",
    CHECKER_PATH,
)


def test_registry_has_one_complete_row_per_reviewed_boundary() -> None:
    assert contract.validate_registry(ROOT) == []
    assert {item.contract_id for item in contract.CONTRACTS} == {
        "reviewer_delivery",
        "skill_manifest_selection",
        "duplicate_lineage",
    }
    assert all(item.trigger_paths for item in contract.CONTRACTS)
    assert "skills/shared/scripts/reviewer_delivery_schema.py" in contract.contract_for(
        "reviewer_delivery"
    ).trigger_paths
    assert "skills/public/quality/scripts/dup_ratchet_scan.py" in contract.contract_for(
        "duplicate_lineage"
    ).trigger_paths


def test_registry_trigger_paths_cover_runtime_dependency_closures() -> None:
    expected = {
        "reviewer_delivery": {
            "skills/shared/scripts/reviewer_capability.py",
            "skills/shared/scripts/reviewer_capability_preflight.py",
            "skills/shared/scripts/reviewer_result_contract.py",
            "skills/shared/scripts/reviewer_delivery_state.py",
            "scripts/yaml_output.py",
        },
        "duplicate_lineage": {
            "skills/public/quality/scripts/dup_review_lib.py",
            "skills/public/quality/scripts/dup_ratchet_scope.py",
            "skills/public/quality/scripts/nose_report_lib.py",
            "skills/public/quality/scripts/nose_fingerprint_lib.py",
            "skills/public/quality/scripts/nose_tool_lib.py",
            "scripts/adapters/quality_adapter_lib.py",
        },
    }
    for contract_id, paths in expected.items():
        assert paths <= set(contract.contract_for(contract_id).trigger_paths)


def test_each_registered_dependency_schedules_provenance_gate() -> None:
    for item in contract.CONTRACTS:
        for path in item.trigger_paths:
            labels = [
                gate.label
                for gate in staged_commit_gate_plan._timing_layer_gates(
                    ROOT, [path], existing=[path]
                )
            ]
            assert "check-provenance-contract" in labels, (item.contract_id, path)


def test_missing_producer_binding_is_typed_and_fail_closed() -> None:
    with pytest.raises(contract.BoundaryContractError, match="receipt_file"):
        contract.require_bound_fields(
            "reviewer_delivery",
            {"output_file": "result.json", "receipt_file": None, "producer_run_id": "run-1"},
        )


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
    ] * 3


def test_contract_checker_marks_plugin_layout_shape_only() -> None:
    result = run_loaded_script_main(
        "check_provenance_contract.py",
        CHECKER,
        "--repo-root",
        str(ROOT / "plugins/charness"),
    )
    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0
    assert payload["proof_level"] == "shape+consumer-anchors"
    assert payload["fixture_results"] == []
    assert payload["non_claims"]


def test_plugin_anchor_validation_refuses_missing_consumer(tmp_path: Path) -> None:
    plugin = tmp_path / "plugin"
    (plugin / "shared" / "scripts").mkdir(parents=True)
    (plugin / "skills" / "quality" / "scripts").mkdir(parents=True)
    for item in contract.CONTRACTS:
        relative = CHECKER._plugin_relative_path(item.consumer_path)
        path = plugin / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(item.contract_id, encoding="utf-8")
    missing = plugin / CHECKER._plugin_relative_path(contract.CONTRACTS[0].consumer_path)
    missing.unlink()
    errors = CHECKER._validate_plugin_anchors(plugin, contract.CONTRACTS)
    assert any("reviewer_delivery" in error and "missing plugin consumer" in error for error in errors)
    unsafe = replace(contract.CONTRACTS[0], consumer_path="../escape.py")
    errors = CHECKER._validate_plugin_anchors(plugin, (unsafe,))
    assert any("unsafe plugin consumer path" in error for error in errors)


def test_fixture_status_refuses_skipped_xpassed_and_zero_tests(tmp_path: Path) -> None:
    skipped = tmp_path / "skipped.xml"
    skipped.write_text(
        '<testsuite><testcase><skipped type="pytest.skip" /></testcase></testsuite>',
        encoding="utf-8",
    )
    assert CHECKER._junit_fixture_status(skipped, "") == (
        "skipped",
        "pytest marked the fixture skipped",
    )
    empty = tmp_path / "empty.xml"
    empty.write_text("<testsuite />", encoding="utf-8")
    status, detail = CHECKER._junit_fixture_status(empty, "")
    assert status == "zero-tests"
    assert detail
    assert CHECKER._junit_fixture_status(empty, "XPASS test_example") == (
        "xpassed",
        "pytest reported XPASS",
    )
    namespaced = tmp_path / "namespaced.xml"
    namespaced.write_text(
        '<testsuite xmlns="urn:pytest"><testcase name="fixture" /></testsuite>',
        encoding="utf-8",
    )
    assert CHECKER._junit_fixture_status(namespaced, "") == ("passed", None)


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
    assert payload["fixture_results"][0]["status"] == "missing-result"
    assert "fixture failed" in payload["errors"][0]


def test_contract_checker_refuses_unloadable_yaml_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenSpec:
        loader = None

    monkeypatch.setattr(
        CHECKER.importlib.util,
        "spec_from_file_location",
        lambda *args, **kwargs: BrokenSpec(),
    )
    with pytest.raises(RuntimeError, match="yaml output helper is not loadable"):
        CHECKER._emit_yaml({}, ROOT)


def test_contract_checker_script_entrypoint_exits_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_provenance_contract.py", "--repo-root", str(ROOT / "plugins/charness")],
    )
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(CHECKER_PATH), run_name="__main__")
    assert raised.value.code == 0
