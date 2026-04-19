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


def test_eval_cautilus_chatbot_proposals_writes_summary(tmp_path: Path) -> None:
    output_dir = tmp_path / "chatbot-proposals"
    result = run_script(
        "scripts/eval_cautilus_chatbot_proposals.py",
        "--repo-root",
        str(ROOT),
        "--output-dir",
        str(output_dir),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["candidate_count"] == 12
    assert payload["proposal_count"] == 5
    assert len(payload["candidate_keys"]) == 12
    assert payload["proposal_keys"] == [
        "quality-proof-layering-followup",
        "init-repo-partial-normalization-followup",
        "handoff-workflow-trigger-followup",
        "find-skills-canonical-artifact-followup",
        "retro-structural-cause-followup",
    ]
    assert "premortem-canonical-subagent-followup" in payload["omitted_candidate_keys"]
    assert "narrative-truth-before-announcement-followup" in payload["omitted_candidate_keys"]
    assert "spec-before-impl-followup" in payload["omitted_candidate_keys"]
    assert "debug-exact-symptom-before-fix-followup" in payload["omitted_candidate_keys"]
    assert "release-real-host-proof-followup" in payload["omitted_candidate_keys"]
    assert "hitl-bounded-review-loop-followup" in payload["omitted_candidate_keys"]
    assert "gather-official-path-before-browser-followup" in payload["omitted_candidate_keys"]
    assert (output_dir / "latest.json").is_file()
    assert (output_dir / "latest.md").is_file()


def test_instruction_surface_runner_supports_fixture_backend(tmp_path: Path) -> None:
    cases_path = ROOT / "evals" / "cautilus" / "instruction-surface-cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    workspace = str(ROOT)

    fixture_results = {}
    for evaluation in cases["evaluations"]:
        expected_routing = evaluation.get("expectedRouting", {})
        fixture_results[evaluation["evaluationId"]] = {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": f"Observed {evaluation['evaluationId']}",
            "entryFile": f"{workspace}/AGENTS.md",
            "loadedInstructionFiles": [f"{workspace}/AGENTS.md"],
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": expected_routing.get("selectedSkill", expected_routing.get("workSkill", "none")),
                "bootstrapHelper": expected_routing.get("bootstrapHelper", "none"),
                "workSkill": expected_routing.get("workSkill", expected_routing.get("selectedSkill", "none")),
                "selectedSupport": expected_routing.get("selectedSupport", "none"),
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
    assert by_id["checked-in-bootstrap-before-impl"]["expectedRouting"]["bootstrapHelper"] == "find-skills"
    assert by_id["checked-in-bootstrap-before-impl"]["expectedRouting"]["workSkill"] == "impl"
    assert by_id["compact-no-bootstrap-impl"]["expectedRouting"]["selectedSkill"] == "impl"
    assert "expectedRouting" not in by_id["compact-no-bootstrap-spec"]
    assert by_id["expanded-no-bootstrap-spec"]["expectedRouting"]["selectedSkill"] == "spec"


def test_instruction_surface_runner_normalizes_markdown_link_entry_file(tmp_path: Path) -> None:
    cases = {
        "schemaVersion": "cautilus.instruction_surface_cases.v1",
        "suiteId": "entry-file-normalization",
        "evaluations": [
            {
                "evaluationId": "markdown-link-entry-file",
                "prompt": "Route this request.",
                "expectedEntryFile": "AGENTS.md",
                "instructionSurface": {
                    "surfaceLabel": "compact_no_bootstrap",
                    "files": [
                        {
                            "path": "AGENTS.md",
                            "content": "# demo\n",
                        }
                    ],
                },
            }
        ],
    }
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    workspace = str(ROOT)
    fixture_results = {
        "markdown-link-entry-file": {
            "observationStatus": "observed",
            "summary": "Observed markdown link entry file",
            "entryFile": f"[{workspace}/AGENTS.md]({workspace}/AGENTS.md)",
            "loadedInstructionFiles": [f"{workspace}/AGENTS.md"],
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": "none",
                "bootstrapHelper": "none",
                "workSkill": "none",
                "selectedSupport": "none",
                "firstToolCall": "none",
                "reasonSummary": "Observed markdown link entry file",
            },
        }
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
    evaluation = packet["evaluations"][0]
    assert evaluation["entryFile"] == "AGENTS.md"
