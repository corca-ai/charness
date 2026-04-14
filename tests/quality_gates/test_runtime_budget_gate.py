from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/check-runtime-budget.py"


def _seed_repo(tmp_path: Path, *, budgets: dict[str, int] | None, signals: dict | None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "skill-outputs" / "quality").mkdir(parents=True)
    adapter_lines = ["version: 1", "repo: testrepo", "output_dir: skill-outputs/quality"]
    if budgets is not None:
        adapter_lines.append("runtime_budgets:")
        for label, ms in budgets.items():
            adapter_lines.append(f"  {label}: {ms}")
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")
    if signals is not None:
        (repo / "skill-outputs" / "quality" / "runtime-signals.json").write_text(
            json.dumps(signals), encoding="utf-8"
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
    assert payload["checked"][0] == {"label": "pytest", "budget_ms": 22000, "elapsed_ms": 15000, "status": "ok"}


def test_runtime_budget_gate_fails_when_over_budget(tmp_path: Path) -> None:
    signals = {"commands": {"pytest": {"latest": {"elapsed_ms": 30000, "status": "pass"}}}}
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violations"] == [{"label": "pytest", "budget_ms": 22000, "elapsed_ms": 30000}]
    plain_result = run_script(SCRIPT, "--repo-root", str(repo))
    assert plain_result.returncode == 1
    assert "exceeded" in plain_result.stderr.lower()


def test_runtime_budget_gate_warns_on_missing_sample(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, budgets={"pytest": 22000}, signals={"commands": {}})
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["missing_samples"] == ["pytest"]
    assert payload["violations"] == []
