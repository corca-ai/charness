from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_instruction_surface_runner_supports_fixture_backend(tmp_path: Path) -> None:
    cases_path = ROOT / "evals" / "cautilus" / "whole-repo-routing.fixture.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    workspace = str(workspace_path)

    fixture_results = {}
    for item in cases["cases"]:
        evaluation = {
            **{key: value for key, value in item.items() if key != "caseId"},
            "evaluationId": item["caseId"],
        }
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
            "scripts/agent-runtime/run-local-eval-test.mjs",
            "--repo-root",
            str(ROOT),
            "--workspace",
            workspace,
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
    assert packet["schemaVersion"] == "cautilus.evaluation_observed.v1"
    assert packet["suiteId"] == "charness-instruction-surface"
    assert len(packet["evaluations"]) == len(cases["cases"])

    by_id = {item["evaluationId"]: item for item in packet["evaluations"]}
    assert by_id["checked-in-bootstrap-before-impl"]["expectedRouting"]["bootstrapHelper"] == "find-skills"
    assert by_id["checked-in-bootstrap-before-impl"]["expectedRouting"]["workSkill"] == "impl"
    assert by_id["compact-startup-bootstrap-before-impl"]["expectedRouting"]["bootstrapHelper"] == "find-skills"
    assert by_id["compact-startup-bootstrap-before-impl"]["expectedRouting"]["workSkill"] == "impl"
    assert by_id["compact-startup-bootstrap-before-spec"]["expectedRouting"]["bootstrapHelper"] == "find-skills"
    assert by_id["compact-startup-bootstrap-before-spec"]["expectedRouting"]["workSkill"] == "spec"


def test_instruction_surface_runner_fails_required_concept_assertions(tmp_path: Path) -> None:
    cases = {
        "schemaVersion": "cautilus.evaluation_cases.v1",
        "suiteId": "concept-assertions",
        "evaluations": [
            {
                "evaluationId": "concept-pass",
                "prompt": "Inspect the issue resolution requirement.",
                "requiredConcepts": [
                    {
                        "id": "mental-model-sibling-search",
                        "terms": ["mental model", "structural sibling", "keyword", "proximity"],
                    }
                ],
            },
            {
                "evaluationId": "concept-fail",
                "prompt": "Inspect the issue resolution requirement.",
                "requiredConcepts": [
                    {
                        "id": "mental-model-sibling-search",
                        "terms": ["mental model", "structural sibling"],
                    }
                ],
            },
        ],
    }
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    workspace = str(workspace_path)
    base_observed = {
        "observationStatus": "observed",
        "blockerKind": "",
        "entryFile": f"{workspace}/AGENTS.md",
        "loadedInstructionFiles": [f"{workspace}/AGENTS.md"],
        "loadedSupportingFiles": [],
        "routingDecision": {
            "selectedSkill": "issue",
            "bootstrapHelper": "none",
            "workSkill": "issue",
            "selectedSupport": "none",
            "firstToolCall": "none",
            "reasonSummary": "issue resolution names the mental model and structural sibling search beyond keyword or proximity matches",
        },
    }
    fixture_results = {
        "concept-pass": {
            **base_observed,
            "summary": "Names the mental model and structural sibling search beyond keyword/proximity matching.",
        },
        "concept-fail": {
            **base_observed,
            "summary": "Names only the mental model.",
            "routingDecision": {
                **base_observed["routingDecision"],
                "reasonSummary": "Names only the mental model.",
            },
        },
    }
    fixture_path = tmp_path / "fixture-results.json"
    output_path = tmp_path / "instruction-surface-inputs.json"
    artifact_dir = tmp_path / "artifacts"
    fixture_path.write_text(json.dumps(fixture_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            "node",
            "scripts/agent-runtime/run-local-eval-test.mjs",
            "--repo-root",
            str(ROOT),
            "--workspace",
            workspace,
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

    assert result.returncode == 1
    assert "Concept assertion failure" in result.stderr
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    by_id = {item["evaluationId"]: item for item in packet["evaluations"]}
    passing = by_id["concept-pass"]["conceptAssertions"][0]
    assert passing["status"] == "passed"
    assert passing["missingTerms"] == []
    assert by_id["concept-pass"]["requiredConcepts"][0]["sourceFields"] == [
        "summary",
        "routingDecision.reasonSummary",
    ]
    failing = by_id["concept-fail"]["conceptAssertions"][0]
    assert failing["status"] == "failed"
    assert failing["missingTerms"] == ["structural sibling"]


def test_issue_sibling_search_fixtures_emit_passing_required_concept_assertions(tmp_path: Path) -> None:
    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    workspace = str(workspace_path)
    fixture_results = {
        "issue-146-mental-model-sibling-search": {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": "The causal review must name the mental model and scan structural sibling patterns beyond keyword and proximity matches.",
            "entryFile": f"{workspace}/AGENTS.md",
            "loadedInstructionFiles": [
                f"{workspace}/skills/public/issue/SKILL.md",
                f"{workspace}/skills/public/issue/references/causal-review.md",
            ],
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": "issue",
                "bootstrapHelper": "none",
                "workSkill": "issue",
                "selectedSupport": "none",
                "firstToolCall": "none",
                "reasonSummary": "The issue skill requires mental model sibling search beyond keyword or proximity matching.",
            },
        },
        "issue-148-mental-model-sibling-search": {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": "The issue resolution requires recurrence-focused review, names the mental model, and scans structural sibling patterns beyond keyword and proximity matches.",
            "entryFile": f"{workspace}/AGENTS.md",
            "loadedInstructionFiles": [
                f"{workspace}/skills/public/issue/SKILL.md",
                f"{workspace}/skills/public/issue/references/causal-review.md",
            ],
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": "issue",
                "bootstrapHelper": "none",
                "workSkill": "issue",
                "selectedSupport": "none",
                "firstToolCall": "none",
                "reasonSummary": "The recurrence-focused review must preserve mental model structural sibling search beyond keyword/proximity matches.",
            },
        },
    }
    fixture_path = tmp_path / "fixture-results.json"
    fixture_path.write_text(json.dumps(fixture_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for cases_path in (
        ROOT / "evals" / "cautilus" / "issue-146-sibling-search.fixture.json",
        ROOT / "evals" / "cautilus" / "issue-148-sibling-search.fixture.json",
    ):
        output_path = tmp_path / f"{cases_path.stem}.observed.json"
        artifact_dir = tmp_path / f"{cases_path.stem}.artifacts"
        result = subprocess.run(
            [
                "node",
                "scripts/agent-runtime/run-local-eval-test.mjs",
                "--repo-root",
                str(ROOT),
                "--workspace",
                workspace,
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
        assertion = packet["evaluations"][0]["conceptAssertions"][0]
        assert assertion["status"] == "passed"
        assert assertion["missingTerms"] == []


def test_instruction_surface_runner_normalizes_markdown_link_entry_file(tmp_path: Path) -> None:
    cases = {
        "schemaVersion": "cautilus.evaluation_cases.v1",
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

    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    workspace = str(workspace_path)
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
            "scripts/agent-runtime/run-local-eval-test.mjs",
            "--repo-root",
            str(ROOT),
            "--workspace",
            workspace,
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
