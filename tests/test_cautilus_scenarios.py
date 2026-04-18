from __future__ import annotations

import json
import subprocess
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


def test_validate_cautilus_scenarios_covers_instruction_surface_wiring() -> None:
    result = run_script("scripts/validate-cautilus-scenarios.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_instruction_surface_runner_supports_fixture_backend(tmp_path: Path) -> None:
    cases_path = ROOT / "evals" / "cautilus" / "instruction-surface-cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    workspace = str(ROOT)

    fixture_results = {}
    for evaluation in cases["evaluations"]:
        fixture_results[evaluation["evaluationId"]] = {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": f"Observed {evaluation['evaluationId']}",
            "entryFile": f"{workspace}/AGENTS.md",
            "loadedInstructionFiles": [f"{workspace}/AGENTS.md"],
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": evaluation.get("expectedRouting", {}).get("selectedSkill", "none"),
                "selectedSupport": evaluation.get("expectedRouting", {}).get("selectedSupport", "none"),
                "firstToolCall": "none",
                "reasonSummary": f"Observed {evaluation['evaluationId']}",
            },
        }

    fixture_path = tmp_path / "fixture-results.json"
    output_path = tmp_path / "instruction-surface-inputs.json"
    artifact_dir = tmp_path / "artifacts"
    fixture_path.write_text(json.dumps(fixture_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            "node",
            "scripts/agent-runtime/run-local-instruction-surface-test.mjs",
            "--repo-root",
            str(ROOT),
            "--workspace",
            str(ROOT),
            "--cases-file",
            str(cases_path),
            "--output-file",
            str(output_path),
            "--artifact-dir",
            str(artifact_dir),
            "--backend",
            "fixture",
            "--fixture-results-file",
            str(fixture_path),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    assert packet["schemaVersion"] == "cautilus.instruction_surface_inputs.v1"
    assert packet["suiteId"] == "charness-instruction-surface"
    assert len(packet["evaluations"]) == len(cases["evaluations"])

    by_id = {item["evaluationId"]: item for item in packet["evaluations"]}
    assert by_id["checked-in-bootstrap-before-impl"]["expectedRouting"]["selectedSkill"] == "find-skills"
    assert by_id["compact-no-bootstrap-impl"]["expectedRouting"]["selectedSkill"] == "impl"
    assert "expectedRouting" not in by_id["compact-no-bootstrap-spec"]
    assert by_id["expanded-no-bootstrap-spec"]["expectedRouting"]["selectedSkill"] == "spec"
