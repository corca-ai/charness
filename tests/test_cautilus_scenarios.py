from __future__ import annotations

import json
from pathlib import Path

from .test_quality_artifact import run_script

ROOT = Path(__file__).resolve().parents[1]
def test_run_evals_supports_scenario_filter() -> None:
    result = run_script(
        "scripts/run-evals.py",
        "--repo-root",
        str(ROOT),
        "--scenario-id",
        "find-skills-local-first",
    )
    assert result.returncode == 0, result.stderr
    assert "PASS find-skills-local-first" in result.stdout
    assert "Ran 1 eval scenario(s)." in result.stdout


def test_eval_cautilus_scenarios_writes_summary(tmp_path: Path) -> None:
    output_dir = tmp_path / "cautilus-held-out"
    result = run_script(
        "scripts/eval_cautilus_scenarios.py",
        "--repo-root",
        str(ROOT),
        "--mode",
        "held_out",
        "--baseline-ref",
        "origin/main",
        "--output-dir",
        str(output_dir),
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["mode"] == "held_out"
    assert summary["profile"] == "evaluator-required"
    assert summary["scenario_count"] >= 8
    assert summary["run_evals"]["exit_code"] == 0
