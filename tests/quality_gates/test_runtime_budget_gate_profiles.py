"""Runtime-budget profile selection and machine-affinity scenarios."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

from .support import ROOT, run_script, seed_runtime_budget_repo

SCRIPT = "skills/public/quality/scripts/check_runtime_budget.py"
QUALITY_SCRIPTS_DIR = ROOT / "skills" / "public" / "quality" / "scripts"
if str(QUALITY_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_SCRIPTS_DIR))
RUNTIME_PROFILE_LIB = QUALITY_SCRIPTS_DIR / "runtime_profile_lib.py"
_spec = importlib.util.spec_from_file_location("runtime_profile_lib_profiles", RUNTIME_PROFILE_LIB)
assert _spec is not None and _spec.loader is not None
runtime_profile_lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runtime_profile_lib)


def test_runtime_profile_lib_default_profile_uses_top_level_commands_and_budgets() -> None:
    commands = {"pytest": {"latest": {"elapsed_ms": 1000}}}
    named_commands = {"pytest": {"latest": {"elapsed_ms": 999999}}}
    payload = {
        "commands": commands,
        "profiles": {"ci": {"commands": named_commands}},
    }
    adapter_data = {
        "runtime_budgets": {"pytest": 22000},
        "runtime_budget_profiles": {"ci": {"budgets": {"pytest": 540000}}},
    }

    assert runtime_profile_lib.profile_commands(payload, runtime_profile_lib.DEFAULT_RUNTIME_PROFILE) == commands
    assert runtime_profile_lib.profile_budgets(adapter_data, runtime_profile_lib.DEFAULT_RUNTIME_PROFILE) == (
        {"pytest": 22000},
        [],
    )


def test_runtime_profile_lib_named_profile_uses_profile_commands_and_budgets() -> None:
    commands = {"pytest": {"latest": {"elapsed_ms": 1000}}}
    named_commands = {"pytest": {"latest": {"elapsed_ms": 300000}}}
    payload = {
        "commands": commands,
        "profiles": {"ci": {"commands": named_commands}},
    }
    adapter_data = {
        "runtime_budgets": {"pytest": 22000},
        "runtime_budget_profiles": {"ci": {"budgets": {"pytest": 540000}}},
    }

    assert runtime_profile_lib.profile_commands(payload, "ci") == named_commands
    assert runtime_profile_lib.profile_budgets(adapter_data, "ci") == ({"pytest": 540000}, [])


def test_runtime_profile_selection_treats_literal_default_as_machine_auto(monkeypatch) -> None:
    monkeypatch.delenv("CHARNESS_RUNTIME_PROFILE", raising=False)

    selected = runtime_profile_lib.selected_runtime_profile(
        {"runtime_profile_default": runtime_profile_lib.DEFAULT_RUNTIME_PROFILE},
        requested_profile=None,
    )

    assert selected.startswith("local-")
    assert selected != runtime_profile_lib.DEFAULT_RUNTIME_PROFILE


def test_runtime_profile_selection_returns_configured_non_default(monkeypatch) -> None:
    monkeypatch.delenv("CHARNESS_RUNTIME_PROFILE", raising=False)
    assert runtime_profile_lib.selected_runtime_profile({"runtime_profile_default": "slow-ci"}, None) == "slow-ci"
    assert runtime_profile_lib.selected_runtime_profile({"runtime_profile_default": "ci-fast"}, None) == "ci-fast"


def test_runtime_profile_commands_named_profile_sorting_after_default() -> None:
    top = {"pytest": {"latest": {"elapsed_ms": 1}}}
    named = {"pytest": {"latest": {"elapsed_ms": 2}}}
    payload = {"commands": top, "profiles": {"slow": {"commands": named}}}
    assert runtime_profile_lib.profile_commands(payload, "slow") == named


def test_runtime_profile_budgets_named_profile_without_budget_profiles_falls_back() -> None:
    adapter_data = {"runtime_budgets": {"pytest": 7000}}
    assert runtime_profile_lib.profile_budgets(adapter_data, "slow-ci") == ({"pytest": 7000}, [])


def test_machine_runtime_profile_uses_detected_system(monkeypatch) -> None:
    monkeypatch.setattr(runtime_profile_lib.platform, "system", lambda: "TestOS")
    monkeypatch.setattr(runtime_profile_lib.platform, "machine", lambda: "TestArch")
    monkeypatch.setattr(runtime_profile_lib.os, "sched_getaffinity", lambda _pid: set(range(4)))
    monkeypatch.setattr(runtime_profile_lib.os, "cpu_count", lambda: 36)
    assert runtime_profile_lib.machine_runtime_profile() == "local-testos-testarch-4cpu"


def test_runtime_profile_keys_on_affinity_not_total_cpus(monkeypatch) -> None:
    monkeypatch.setattr(runtime_profile_lib.os, "cpu_count", lambda: 36)
    monkeypatch.setattr(runtime_profile_lib.os, "sched_getaffinity", lambda _pid: set(range(4)))
    monkeypatch.setattr(runtime_profile_lib.platform, "system", lambda: "Linux")
    monkeypatch.setattr(runtime_profile_lib.platform, "machine", lambda: "x86_64")

    assert runtime_profile_lib.usable_cpu_count() == 4
    assert runtime_profile_lib.machine_runtime_profile() == "local-linux-x86_64-4cpu"


def test_runtime_profile_falls_back_to_cpu_count_without_affinity(monkeypatch) -> None:
    monkeypatch.setattr(runtime_profile_lib.os, "cpu_count", lambda: 8)
    monkeypatch.delattr(runtime_profile_lib.os, "sched_getaffinity", raising=False)
    monkeypatch.setattr(runtime_profile_lib.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(runtime_profile_lib.platform, "machine", lambda: "arm64")

    assert runtime_profile_lib.usable_cpu_count() == 8
    assert runtime_profile_lib.machine_runtime_profile() == "local-darwin-arm64-8cpu"


def test_runtime_profile_survives_sched_getaffinity_oserror(monkeypatch) -> None:
    monkeypatch.setattr(runtime_profile_lib.os, "cpu_count", lambda: 12)

    def refuse(_pid: int) -> set[int]:
        raise OSError(1, "Operation not permitted")

    monkeypatch.setattr(runtime_profile_lib.os, "sched_getaffinity", refuse)
    monkeypatch.setattr(runtime_profile_lib.platform, "system", lambda: "Linux")
    monkeypatch.setattr(runtime_profile_lib.platform, "machine", lambda: "x86_64")

    assert runtime_profile_lib.usable_cpu_count() == 12
    assert runtime_profile_lib.machine_runtime_profile() == "local-linux-x86_64-12cpu"


def test_runtime_budget_gate_auto_selects_machine_profile(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals={"profiles": {}})
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["runtime_profile"].startswith("local-")
    assert payload["runtime_profile"].endswith("cpu")


def test_runtime_budget_gate_selects_named_profile_budget_and_samples(tmp_path: Path) -> None:
    signals = {
        "profiles": {
            "local-fast": {
                "commands": {
                    "pytest": {
                        "latest": {"elapsed_ms": 42000, "status": "pass"},
                        "median_recent_elapsed_ms": 41000,
                    }
                }
            },
            "ci-slow": {
                "commands": {
                    "pytest": {
                        "latest": {"elapsed_ms": 300000, "status": "pass"},
                        "median_recent_elapsed_ms": 290000,
                    }
                }
            },
        }
    }
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 70000},
        budget_profiles={
            "local-fast": {"budgets": {"pytest": 45000}},
            "ci-slow": {"budgets": {"pytest": 540000}},
        },
        signals=signals,
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "ci-slow")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["runtime_profile"] == "ci-slow"
    assert payload["checked"][0]["budget_ms"] == 540000
    assert payload["checked"][0]["median_recent_elapsed_ms"] == 290000
    assert payload["violations"] == []


def test_runtime_budget_gate_fails_unknown_explicit_profile(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(
        tmp_path,
        budgets={"pytest": 70000},
        budget_profiles={"local-fast": {"budgets": {"pytest": 45000}}},
        signals={"profiles": {}},
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "ci-slow")
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["profile_config_errors"] == [
        "runtime profile `ci-slow` is not configured in runtime_budget_profiles"
        " (derive a starting block with `check_runtime_budget.py"
        " --runtime-profile ci-slow --suggest-budgets`)"
    ]
