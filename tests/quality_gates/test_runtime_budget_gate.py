from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/check_runtime_budget.py"


def _seed_repo(
    tmp_path: Path,
    *,
    budgets: dict[str, int] | None,
    signals: dict | None,
    smoothing: dict | None = None,
) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".charness" / "quality").mkdir(parents=True)
    adapter_lines = ["version: 1", "repo: testrepo", "output_dir: charness-artifacts/quality"]
    if budgets is not None:
        adapter_lines.append("runtime_budgets:")
        for label, ms in budgets.items():
            adapter_lines.append(f"  {label}: {ms}")
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


def test_runtime_budget_gate_no_budgets_passes(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets=None, signals=None)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["budgets_configured"] == 0
    assert payload["violations"] == []


def test_runtime_budget_gate_passes_when_within_budget(tmp_path: Path) -> None:
    signals = {"commands": {"pytest": {"latest": {"elapsed_ms": 15000, "status": "pass"}}}}
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
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
    plain_result = run_script(SCRIPT, "--repo-root", str(repo))
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []
    assert payload["checked"][0]["status"] == "ok"
    assert payload["checked"][0]["ewma_advisory_elapsed_ms"] == 45000.5
    assert payload["checked"][0]["ewma_alpha"] == 0.35
    assert payload["checked"][0]["ewma_samples"] == 7

    plain_result = run_script(SCRIPT, "--repo-root", str(repo))
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
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
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["missing_samples"] == ["pytest"]
    assert payload["violations"] == []


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

    plain_result = run_script(SCRIPT, "--repo-root", str(repo), "--top-runtime-count", "2")
    assert plain_result.returncode == 0, plain_result.stderr
    assert "Runtime hot spots:" in plain_result.stdout
    assert "check-cli-skill-surface" in plain_result.stdout
    assert "unbudgeted" in plain_result.stdout
