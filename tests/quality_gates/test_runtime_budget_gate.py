from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .support import ROOT, run_script

SCRIPT = "skills/public/quality/scripts/check_runtime_budget.py"
RENDER_SCRIPT = "skills/public/quality/scripts/render_runtime_summary.py"
RUNTIME_PROFILE_LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "runtime_profile_lib.py"
_spec = importlib.util.spec_from_file_location("runtime_profile_lib_under_test", RUNTIME_PROFILE_LIB)
assert _spec is not None and _spec.loader is not None
runtime_profile_lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runtime_profile_lib)


def _seed_repo(
    tmp_path: Path,
    *,
    budgets: dict[str, int] | None,
    signals: dict | None,
    budget_profiles: dict[str, dict[str, dict[str, int]]] | None = None,
    smoothing: dict | None = None,
    explicit_empty_budgets: bool = False,
    startup_probes: list[dict[str, object]] | None = None,
) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".charness" / "quality").mkdir(parents=True)
    adapter_lines = ["version: 1", "repo: testrepo", "output_dir: charness-artifacts/quality"]
    if budgets is not None:
        adapter_lines.append("runtime_budgets:")
        for label, ms in budgets.items():
            adapter_lines.append(f"  {label}: {ms}")
    elif explicit_empty_budgets:
        adapter_lines.append("runtime_budgets:")
    if budget_profiles is not None:
        adapter_lines.append("runtime_budget_profiles:")
        for profile_id, profile in budget_profiles.items():
            adapter_lines.append(f"  {profile_id}:")
            adapter_lines.append("    budgets:")
            for label, ms in profile["budgets"].items():
                adapter_lines.append(f"      {label}: {ms}")
    if startup_probes is not None:
        if not startup_probes:
            adapter_lines.append("startup_probes: []")
        else:
            adapter_lines.append("startup_probes:")
            for probe in startup_probes:
                adapter_lines.extend(
                    [
                        f"  - label: {probe['label']}",
                        "    command:",
                        *[f"      - {item}" for item in probe["command"]],
                        f"    class: {probe['class']}",
                        f"    startup_mode: {probe['startup_mode']}",
                        f"    surface: {probe['surface']}",
                        f"    samples: {probe['samples']}",
                    ]
                )
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")
    if signals is not None:
        (repo / ".charness" / "quality" / "runtime-signals.json").write_text(
            json.dumps(signals), encoding="utf-8"
        )
    if smoothing is not None:
        (repo / ".charness" / "quality" / "runtime-smoothing.json").write_text(
            json.dumps(smoothing), encoding="utf-8"
        )
    return repo


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


def test_runtime_budget_gate_no_budgets_passes(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets=None, signals=None)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["budgets_configured"] == 0
    assert payload["runtime_profile"] == "default"
    assert payload["violations"] == []
    assert [finding["type"] for finding in payload["runtime_visibility_findings"]] == [
        "runtime_visibility_missing_budgets",
        "runtime_visibility_missing_startup_probes",
    ]

    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 0, plain_result.stderr
    assert "WEAK  runtime_visibility_missing_budgets" in plain_result.stdout


def test_runtime_budget_gate_reports_explicit_empty_runtime_fields(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets=None, signals=None, explicit_empty_budgets=True, startup_probes=[])

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [finding["type"] for finding in payload["runtime_visibility_findings"]] == [
        "runtime_visibility_missing_budgets",
        "runtime_visibility_missing_startup_probes",
    ]


def test_runtime_budget_gate_reports_empty_selected_profile_budget(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        budgets=None,
        budget_profiles={"ci": {"budgets": {}}},
        signals={"profiles": {"ci": {"commands": {}}}},
        startup_probes=[],
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "ci")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["budgets_configured"] == 0
    assert payload["runtime_visibility_findings"][0]["type"] == "runtime_visibility_missing_budgets"


def test_runtime_budget_gate_has_no_visibility_findings_when_budget_and_probe_exist(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        budgets={"pytest": 22000},
        signals={"commands": {"pytest": {"latest": {"elapsed_ms": 15000, "status": "pass"}}}},
        startup_probes=[
            {
                "label": "cli-version",
                "command": ["python3", "-c", "print('ok')"],
                "class": "standing",
                "startup_mode": "warm",
                "surface": "direct",
                "samples": 1,
            }
        ],
    )

    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["runtime_visibility_findings"] == []


def test_runtime_budget_gate_passes_when_within_budget(tmp_path: Path) -> None:
    signals = {"commands": {"pytest": {"latest": {"elapsed_ms": 15000, "status": "pass"}}}}
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []
    assert payload["latest_spikes"] == []
    assert payload["checked"][0] == {
        "label": "pytest",
        "budget_ms": 22000,
        "latest_elapsed_ms": 15000,
        "median_recent_elapsed_ms": 15000,
        "max_recent_elapsed_ms": None,
        "ewma_advisory_elapsed_ms": None,
        "ewma_alpha": None,
        "ewma_samples": None,
        "status": "ok",
    }


def test_runtime_budget_gate_fails_when_over_budget(tmp_path: Path) -> None:
    signals = {"commands": {"pytest": {"latest": {"elapsed_ms": 30000, "status": "pass"}}}}
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violations"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "median_recent_elapsed_ms": 30000,
            "latest_elapsed_ms": 30000,
        }
    ]
    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 1
    assert "exceeded" in plain_result.stderr.lower()


def test_runtime_budget_gate_reports_latest_spike_without_failing(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 30000, "status": "pass"},
                "median_recent_elapsed_ms": 15000,
                "max_recent_elapsed_ms": 30000,
            }
        }
    }
    smoothing = {
        "commands": {
            "pytest": {
                "samples": 4,
                "ewma_elapsed_ms": 18000,
                "alpha_last": 0.28,
                "advisory": True,
            }
        }
    }
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals, smoothing=smoothing)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []
    assert payload["latest_spikes"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "latest_elapsed_ms": 30000,
            "median_recent_elapsed_ms": 15000,
        }
    ]
    assert payload["checked"][0]["status"] == "latest-spike"
    assert payload["checked"][0]["ewma_advisory_elapsed_ms"] == 18000.0


def test_runtime_budget_gate_reports_advisory_ewma_without_enforcing_it(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 15000, "status": "pass"},
                "median_recent_elapsed_ms": 15000,
            }
        }
    }
    smoothing = {
        "commands": {
            "pytest": {
                "samples": 7,
                "ewma_elapsed_ms": 45000.5,
                "alpha_last": 0.35,
                "advisory": True,
            }
        }
    }
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals, smoothing=smoothing)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []
    assert payload["checked"][0]["status"] == "ok"
    assert payload["checked"][0]["ewma_advisory_elapsed_ms"] == 45000.5
    assert payload["checked"][0]["ewma_alpha"] == 0.35
    assert payload["checked"][0]["ewma_samples"] == 7

    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")
    assert plain_result.returncode == 0, plain_result.stderr
    assert "ewma 45000.5ms advisory" in plain_result.stdout


def test_runtime_budget_gate_fails_on_recent_median_drift(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 25000, "status": "pass"},
                "median_recent_elapsed_ms": 23000,
                "max_recent_elapsed_ms": 30000,
            }
        }
    }
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violations"] == [
        {
            "label": "pytest",
            "budget_ms": 22000,
            "median_recent_elapsed_ms": 23000,
            "latest_elapsed_ms": 25000,
        }
    ]


def test_runtime_budget_gate_warns_on_missing_sample(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals={"commands": {}})
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["missing_samples"] == ["pytest"]
    assert payload["violations"] == []


def test_runtime_budget_gate_auto_selects_machine_profile(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals={"profiles": {}})
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    repo = _seed_repo(
        tmp_path,
        budgets={"pytest": 70000},
        budget_profiles={
            "local-fast": {"budgets": {"pytest": 45000}},
            "ci-slow": {"budgets": {"pytest": 540000}},
        },
        signals=signals,
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "ci-slow")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["runtime_profile"] == "ci-slow"
    assert payload["checked"][0]["budget_ms"] == 540000
    assert payload["checked"][0]["median_recent_elapsed_ms"] == 290000
    assert payload["violations"] == []


def test_runtime_budget_gate_fails_unknown_explicit_profile(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        budgets={"pytest": 70000},
        budget_profiles={"local-fast": {"budgets": {"pytest": 45000}}},
        signals={"profiles": {}},
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "ci-slow")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["profile_config_errors"] == [
        "runtime profile `ci-slow` is not configured in runtime_budget_profiles"
    ]


def test_runtime_budget_gate_reports_top_runtime_hotspots(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 15000, "status": "pass"},
                "median_recent_elapsed_ms": 14000,
            },
            "check-cli-skill-surface": {
                "latest": {"elapsed_ms": 9000, "status": "pass"},
                "median_recent_elapsed_ms": 8000,
            },
            "check-markdown": {
                "latest": {"elapsed_ms": 7000, "status": "pass"},
                "median_recent_elapsed_ms": 6500,
            },
        }
    }
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--json",
        "--top-runtime-count",
        "2",
        "--runtime-profile",
        "default",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["runtime_hotspots"] == [
        {
            "label": "pytest",
            "latest_elapsed_ms": 15000,
            "median_recent_elapsed_ms": 14000,
            "max_recent_elapsed_ms": None,
            "budget_ms": 22000,
            "budgeted": True,
        },
        {
            "label": "check-cli-skill-surface",
            "latest_elapsed_ms": 9000,
            "median_recent_elapsed_ms": 8000,
            "max_recent_elapsed_ms": None,
            "budget_ms": None,
            "budgeted": False,
        },
    ]

    plain_result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--top-runtime-count",
        "2",
        "--runtime-profile",
        "default",
    )
    assert plain_result.returncode == 0, plain_result.stderr
    assert "Runtime hot spots:" in plain_result.stdout
    assert "check-cli-skill-surface" in plain_result.stdout
    assert "unbudgeted" in plain_result.stdout


def test_render_runtime_summary_uses_structured_runtime_signals(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 15000, "status": "pass"},
                "median_recent_elapsed_ms": 14000,
            }
        }
    }
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["signals_present"] is True
    assert payload["markdown_lines"][:3] == [
        "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `default`.",
        "- runtime hot spots: `pytest` 15.0s latest / 14.0s median, budget 22.0s.",
        "- runtime visibility: weak due to `runtime_visibility_missing_startup_probes`; Add at least one standing startup probe for agent-facing CLI or adapter startup.",
    ]
    # Advisory-interpretation contract rollout (#322): the hot-spot ranking is
    # inference-layer, so a 4th interpretation bullet rides the lines and the JSON.
    assert payload["markdown_lines"][3].startswith("- runtime interpretation (inference-layer trend, not a verdict):")
    interpretation = payload["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)
    assert "transient" in interpretation["blind_spots"]  # the load-bearing blind spot


def test_render_runtime_summary_omits_interpretation_without_hotspots(tmp_path: Path) -> None:
    # Cardinal-error guard: no hot spots -> no inference-layer declaration (it must
    # never attach to an empty report; only a produced ranking is re-interpreted).
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=None)
    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["runtime_hotspots"] == []
    assert "interpretation" not in payload
    assert not any("runtime interpretation" in line for line in payload["markdown_lines"])

    reference = (
        Path(__file__).resolve().parents[2]
        / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    assert "render_runtime_summary.py" in reference


def test_render_runtime_summary_reports_missing_structured_signals(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=None)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    assert (
        "- runtime source: not configured; add structured timing capture before reporting timing trends."
        in result.stdout
    )
    assert "runtime_visibility_missing_startup_probes" in result.stdout
    assert "10s" not in result.stdout


def test_render_runtime_summary_escalates_empty_runtime_visibility(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets=None, signals=None)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [finding["type"] for finding in payload["runtime_visibility_findings"]] == [
        "runtime_visibility_missing_budgets",
        "runtime_visibility_missing_startup_probes",
    ]
    assert payload["markdown_lines"][2].startswith(
        "- runtime visibility: weak due to `runtime_visibility_missing_budgets`, "
        "`runtime_visibility_missing_startup_probes`;"
    )
