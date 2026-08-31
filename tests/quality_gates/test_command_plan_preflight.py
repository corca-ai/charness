from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from .repo_shapes import install_committed_repo
from .support import ROOT, run_script

SCRIPT = ROOT / "scripts" / "command_plan_preflight.py"

_DEMO_PY = """import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--repo-root')
parser.add_argument('--detail', action='store_true')
parser.add_argument('-v', action='store_true')
parser.parse_args()
"""


def _write_plan(repo: Path, payload: dict) -> Path:
    plan = repo / "plan.json"
    plan.write_text(json.dumps(payload), encoding="utf-8")
    return plan


def _demo(repo: Path) -> None:
    scripts = repo / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "demo.py").write_text(_DEMO_PY, encoding="utf-8")


def _base_plan() -> dict:
    return {
        "schema_version": 1,
        "targets": [
            {"id": "demo", "query": "demo.py", "expected_path": "scripts/demo.py"},
        ],
        "refs": [],
        "commands": [
            {
                "id": "demo-command",
                "owner_target": "demo",
                "argv": ["python3", "{target:demo}", "--repo-root", ".", "--detail", "-v"],
            }
        ],
    }


def _run(repo: Path, plan: Path):
    return run_script(str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan))


def _load_preflight_module():
    spec = importlib.util.spec_from_file_location("tests.command_plan_preflight", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_executable(path: Path, body: str) -> None:
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def test_command_plan_preflight_resolves_target_and_owner_flags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    result = _run(repo, _write_plan(repo, _base_plan()))
    assert result.returncode == 0, result.stderr
    assert "status: pass" in result.stdout
    assert "scripts/demo.py" in result.stdout
    assert "--detail" in result.stdout


def test_wrong_path_stops_help_fanout_and_reports_candidates(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["targets"][0] = {"id": "demo", "query": "scripts/missing_demo.py"}
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "target-not-found" in result.stdout
    assert "fanout-stopped" in result.stdout
    assert "commands: []" in result.stdout


def test_ambiguous_basename_requires_explicit_expected_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "one").mkdir(parents=True)
    (repo / "two").mkdir()
    (repo / "one" / "demo.py").write_text("", encoding="utf-8")
    (repo / "two" / "demo.py").write_text("", encoding="utf-8")
    plan = _base_plan()
    plan["targets"][0] = {"id": "demo", "query": "demo.py"}
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "target-ambiguous" in result.stdout


def test_owner_help_rejects_planned_flag_that_was_removed(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["commands"][0]["argv"] = ["python3", "{target:demo}", "--gone"]
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "flag-unresolved" in result.stdout
    assert "--gone" in result.stdout


def test_owner_help_rejects_unknown_short_flag(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["commands"][0]["argv"] = ["python3", "{target:demo}", "-x"]
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "flag-unresolved" in result.stdout
    assert "-x" in result.stdout


def test_owner_or_flag_failure_stops_later_help_probes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["commands"].extend(
        [{"id": "later-command", "owner_target": "demo", "argv": ["python3", "{target:demo}", "--detail"]}]
    )
    plan["commands"][0]["argv"] = ["python3", "{target:demo}", "--gone"]
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "fanout-stopped" in result.stdout
    assert "later command help probes were not run after the first preflight failure" in result.stdout
    assert "id: later-command" not in result.stdout


def test_ref_resolution_is_verified_before_help_probe(tmp_path: Path) -> None:
    repo = install_committed_repo(
        tmp_path / "repo",
        {"scripts/demo.py": _DEMO_PY},
        message="seed command plan",
    )
    plan = _base_plan()
    plan["refs"] = [{"id": "missing", "ref": "does-not-exist"}]
    plan["commands"].append(
        {"id": "later-command", "owner_target": "demo", "argv": ["python3", "{target:demo}", "--detail"]}
    )
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "ref-unresolved" in result.stdout
    assert "commands: []" in result.stdout
    assert "demo-command" not in result.stdout
    assert "later-command" not in result.stdout


@pytest.mark.parametrize(
    ("payload", "needle"),
    [
        (None, "plan-missing"),
        ("not-json", "plan-invalid-json"),
        (["not", "an", "object"], "plan-shape"),
    ],
)
def test_plan_input_failures_are_structured_refusals(
    tmp_path: Path, payload: object, needle: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    plan = repo / "plan.json"
    if payload is None:
        plan = repo / "missing.json"
    elif isinstance(payload, str):
        plan.write_text(payload, encoding="utf-8")
    else:
        plan.write_text(json.dumps(payload), encoding="utf-8")
    result = _run(repo, plan)
    assert result.returncode == 2
    assert needle in result.stdout


def test_plan_outside_repo_is_refused_before_reading(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    result = _run(repo, outside)
    assert result.returncode == 2
    assert "plan-outside-repo" in result.stdout


def test_plan_schema_and_field_shapes_fail_before_fanout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    plan = {
        "schema_version": 99,
        "targets": {},
        "refs": {},
        "commands": {},
    }
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    for needle in ("unsupported-plan-version", "targets must be a list", "refs must be a list"):
        assert needle in result.stdout


def test_target_resolver_covers_shape_expected_path_and_glob_contracts(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    resolved, errors = module._resolve_targets(
        repo,
        [
            None,
            {"id": "", "query": "demo.py"},
            {"id": "demo", "query": ""},
            {"id": "demo", "query": "demo.py", "expected_path": 3},
            {"id": "demo", "query": "scripts/demo.py", "expected_path": "other.py"},
            {"id": "missing", "query": "missing.py"},
            {"id": "demo", "query": "scripts/demo.py"},
            {"id": "glob", "query": "scripts/*.py", "expected_path": "scripts/demo.py"},
            {"id": "demo", "query": "scripts/demo.py"},
        ],
    )
    codes = {entry["code"] for entry in errors}
    assert resolved == {"demo": "scripts/demo.py", "glob": "scripts/demo.py"}
    assert {"target-shape", "target-mismatch", "target-not-found", "duplicate-target"} <= codes


def test_target_and_ref_inventory_failures_are_not_silent(tmp_path: Path, monkeypatch) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    missing_bin = tmp_path / "missing-bin"
    missing_bin.mkdir()
    monkeypatch.setenv("PATH", str(missing_bin))
    files, error = module._repo_files(repo)
    assert files == []
    assert error and error["code"] == "rg-unavailable"

    rg = missing_bin / "rg"
    _write_executable(rg, "exit 2")
    files, error = module._repo_files(repo)
    assert files == []
    assert error and error["code"] == "rg-files-failed"
    resolved, errors = module._resolve_targets(repo, [{"id": "demo", "query": "demo.py"}])
    assert resolved == {} and errors[0]["code"] == "rg-files-failed"
    resolved, errors = module._resolve_targets(repo, "bad-shape")
    assert resolved == {} and errors[0]["code"] == "plan-shape"
    observations, errors = module._verify_refs(repo, "bad-shape")
    assert observations == [] and errors[0]["code"] == "plan-shape"


def test_ref_verifier_records_success_failure_and_bad_shape(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = install_committed_repo(
        tmp_path / "repo",
        {"seed.txt": "seed"},
        message="seed refs",
    )
    observations, errors = module._verify_refs(
        repo, [None, {"id": "head", "ref": "HEAD"}, {"id": "missing", "ref": "nope"}]
    )
    assert len(observations) == 2
    assert any(item["status"] == "pass" and "resolved_commit" in item for item in observations)
    assert any(item["status"] == "fail" for item in observations)
    assert errors[0]["code"] == "ref-shape"
    assert errors[-1]["code"] == "ref-unresolved"


def test_token_and_argv_expansion_refuses_unbound_shapes(tmp_path: Path) -> None:
    module = _load_preflight_module()
    assert module._expand_token("plain", {}) == ("plain", None)
    assert module._expand_token("{target:demo", {"demo": "x"})[1]["code"] == "target-token"
    assert module._expand_token("{target:missing}", {})[1]["code"] == "target-token"
    assert module._expand_token("{target:a}", {"a": "{target:b}", "b": "x"}) == ("x", None)
    assert module._expand_argv([], {})[1][0]["code"] == "command-shape"
    expanded, errors = module._expand_argv(["{target:missing}"], {})
    assert expanded is None and errors[0]["code"] == "target-token"
    assert module._derived_help_argv(["python3", "script.py"]) == ["python3", "script.py", "--help"]


def test_command_probe_covers_shape_help_and_owner_failures(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    targets = {"demo": "scripts/demo.py"}
    assert module._probe_command(repo, {}, targets)[1][0]["code"] == "command-shape"
    assert module._probe_command(
        repo, {"id": "bad", "owner_target": "demo", "argv": ["python3", "{target:no}"]}, targets
    )[1][0]["code"] == "owner-binding"
    assert module._probe_command(
        repo,
        {
            "id": "help-token",
            "owner_target": "demo",
            "argv": ["python3", "{target:demo}"],
            "help_argv": ["python3", "{target:no}"],
        },
        targets,
    )[1][0]["code"] == "owner-binding"
    assert module._probe_command(
        repo,
        {
            "id": "no-help",
            "owner_target": "demo",
            "argv": ["python3", "{target:demo}"],
            "help_argv": ["python3", "{target:demo}"],
        },
        targets,
    )[1][0]["code"] == "help-probe-shape"
    assert module._probe_command(
        repo,
        {"id": "missing-exe", "owner_target": "demo", "argv": ["missing-command", "{target:demo}", "--x"]},
        targets,
    )[1][0]["code"] == "help-probe-failed"
    fail = repo / "scripts" / "fail.py"
    fail.write_text("raise SystemExit(3)\n", encoding="utf-8")
    targets["fail"] = "scripts/fail.py"
    observation, errors = module._probe_command(
        repo,
        {"id": "nonzero", "owner_target": "fail", "argv": ["python3", "{target:fail}"]},
        targets,
    )
    assert observation["status"] == "fail" and errors[0]["code"] == "help-probe-failed"


def test_owner_binding_and_expansion_refusal_branches_are_exercised(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    targets = {"demo": "scripts/demo.py"}

    observation, errors = module._probe_command(
        repo,
        {"id": "non-list-argv", "owner_target": "demo", "argv": None},
        targets,
    )
    assert observation["status"] == "fail" and errors[0]["code"] == "owner-binding"
    observation, errors = module._probe_command(
        repo,
        {"id": "missing-owner", "argv": ["python3", "{target:demo}"]},
        targets,
    )
    assert observation["status"] == "fail" and errors[0]["code"] == "owner-binding"
    observation, errors = module._probe_command(
        repo,
        {"id": "unresolved-owner", "owner_target": "missing", "argv": ["python3", "{target:demo}"]},
        targets,
    )
    assert observation["status"] == "fail" and errors[0]["code"] == "owner-binding"
    observation, errors = module._probe_command(
        repo,
        {
            "id": "malformed-argv-token",
            "owner_target": "demo",
            "argv": ["python3", "{target:demo}", "{target:missing"],
        },
        targets,
    )
    assert observation["status"] == "fail" and errors[0]["code"] == "target-token"
    observation, errors = module._probe_command(
        repo,
        {
            "id": "malformed-help-token",
            "owner_target": "demo",
            "argv": ["python3", "{target:demo}"],
            "help_argv": ["python3", "{target:demo}", "{target:missing"],
        },
        targets,
    )
    assert observation["status"] == "fail" and errors[0]["code"] == "target-token"


def test_owner_binding_rejects_literal_or_mismatched_help_paths(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    targets = {"demo": "scripts/demo.py", "other": "scripts/demo.py"}
    for command in (
        {"id": "literal", "owner_target": "demo", "argv": ["python3", "scripts/demo.py"]},
        {
            "id": "wrong-help-owner",
            "owner_target": "demo",
            "argv": ["python3", "{target:demo}"],
            "help_argv": ["python3", "{target:other}"],
        },
    ):
        observation, errors = module._probe_command(repo, command, targets)
        assert observation["status"] == "fail"
        assert errors[0]["code"] == "owner-binding"


@pytest.mark.parametrize("surface", ["argv", "help_argv"])
def test_owner_binding_rejects_embedded_target_tokens(tmp_path: Path, surface: str) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    command = {
        "id": f"embedded-{surface}",
        "owner_target": "demo",
        "argv": ["python3", "{target:demo}"],
    }
    if surface == "argv":
        command["argv"] = ["python3", "{target:demo}", "--input={target:other}"]
    else:
        command["help_argv"] = ["python3", "{target:demo}", "--input={target:other}", "--help"]
    observation, errors = module._probe_command(repo, command, {"demo": "scripts/demo.py", "other": "scripts/demo.py"})
    assert observation["status"] == "fail"
    assert errors[0]["code"] == "target-token"


def test_owner_binding_rejects_nested_target_tokens(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    observation, errors = module._probe_command(
        repo,
        {
            "id": "nested-target-token",
            "owner_target": "demo",
            "argv": ["python3", "{target:demo{target:other}}"],
        },
        {"demo": "scripts/demo.py", "other": "scripts/demo.py"},
    )
    assert observation["status"] == "fail"
    assert errors[0]["code"] == "target-token"


def test_command_probe_expansion_errors_are_structured_for_argv_and_help(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    targets = {"demo": "scripts/demo.py"}
    observation, errors = module._probe_command(
        repo,
        {"id": "non-string-argv", "owner_target": "demo", "argv": ["python3", "{target:demo}", 7]},
        targets,
    )
    assert observation["status"] == "fail"
    assert errors[0]["code"] == "command-shape"
    observation, errors = module._probe_command(
        repo,
        {
            "id": "non-string-help",
            "owner_target": "demo",
            "argv": ["python3", "{target:demo}"],
            "help_argv": ["python3", "{target:demo}", "--help", 7],
        },
        targets,
    )
    assert observation["status"] == "fail"
    assert errors[0]["code"] == "command-shape"


def test_malformed_command_is_structured_refusal_and_relative_plan_uses_repo_root(tmp_path: Path) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["commands"] = [None]
    report = module.build_report(repo, _write_plan(repo, plan))
    assert report["exit_code"] == 2
    assert report["errors"][0]["code"] == "command-shape"

    _write_plan(repo, _base_plan())
    result = run_script(str(SCRIPT), "--repo-root", str(repo), "--plan", "plan.json", cwd=tmp_path)
    assert result.returncode == 0, result.stderr


def test_main_converts_unexpected_preflight_errors_to_structured_refusal(tmp_path: Path, monkeypatch, capsys) -> None:
    module = _load_preflight_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    plan = _write_plan(repo, _base_plan())

    def explode(*_args, **_kwargs):
        raise ValueError("synthetic preflight failure")

    monkeypatch.setattr(module, "build_report", explode)
    assert module.main(["--repo-root", str(repo), "--plan", str(plan)]) == 2
    assert "preflight-error" in capsys.readouterr().out
