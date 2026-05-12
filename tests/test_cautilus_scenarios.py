from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .test_quality_artifact import run_script

ROOT = Path(__file__).resolve().parents[1]


def test_run_evals_supports_scenario_filter() -> None:
    result = run_script(
        "scripts/run_evals.py",
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


def test_validate_cautilus_scenarios_covers_eval_surface_wiring() -> None:
    result = run_script("scripts/validate_cautilus_scenarios.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_issue_evaluator_profile_includes_sibling_search_concept_fixture() -> None:
    registry = json.loads((ROOT / "evals" / "cautilus" / "scenarios.json").read_text(encoding="utf-8"))
    issue_entry = next(
        entry
        for entry in registry["profiles"]["evaluator-required"]["skills"]
        if entry["skill_id"] == "issue"
    )

    assert "issue-sibling-search-concept-fixtures" in issue_entry["scenario_ids"]


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
    assert payload["proposal_count"] == 12
    assert len(payload["candidate_keys"]) == 12
    assert payload["proposal_keys"][:5] == [
        "critique-canonical-subagent-followup",
        "handoff-workflow-trigger-followup",
        "find-skills-canonical-artifact-followup",
        "retro-structural-cause-followup",
        "gather-official-path-before-browser-followup",
    ]
    assert payload["attention_view_proposal_keys"] == [
        "critique-canonical-subagent-followup",
        "handoff-workflow-trigger-followup",
        "find-skills-canonical-artifact-followup",
        "retro-structural-cause-followup",
        "gather-official-path-before-browser-followup",
    ]
    assert payload["attention_view_selected_count"] == 5
    assert payload["attention_view_truncated"] is True
    assert payload["attention_view_fallback_used"] is False
    assert payload["proposal_telemetry"]["mergedCandidateCount"] == 12
    assert payload["proposal_telemetry"]["returnedProposalCount"] == 12
    assert sorted(payload["proposal_keys"]) == sorted(payload["candidate_keys"])
    assert payload["omitted_candidate_keys"] == []
    assert (output_dir / "latest.json").is_file()
    assert (output_dir / "latest.md").is_file()


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


def test_instruction_surface_codex_session_mode_is_configurable() -> None:
    script = """
        import { codexArgs } from './scripts/agent-runtime/run-local-eval-test.mjs';
        const base = { workspace: '/tmp/work', sandbox: 'read-only', codexSessionMode: 'ephemeral' };
        const persistent = { ...base, codexSessionMode: 'persistent' };
        console.log(JSON.stringify({
          defaultArgs: codexArgs(base, '/tmp/schema.json', '/tmp/output.json'),
          persistentArgs: codexArgs(persistent, '/tmp/schema.json', '/tmp/output.json')
        }));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "--ephemeral" in payload["defaultArgs"]
    assert "--ephemeral" not in payload["persistentArgs"]


def test_instruction_surface_codex_home_mode_inherit_preserves_host_home() -> None:
    script = """
        import { codexEnvironment } from './scripts/agent-runtime/run-local-eval-test.mjs';
        process.env.CODEX_HOME = '/tmp/inherited-codex-home';
        const runtime = codexEnvironment(
          { repoRoot: '/tmp/repo', codexHomeMode: 'inherit', codexHome: null },
          '/tmp/output'
        );
        console.log(JSON.stringify({
          codeHome: runtime.env.CODEX_HOME,
          telemetry: runtime.telemetry
        }));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["codeHome"] == "/tmp/inherited-codex-home"
    assert payload["telemetry"] == {
        "codex_home_mode": "inherit",
        "codex_home_isolated": False,
        "codex_home_path": "/tmp/inherited-codex-home",
    }


def test_instruction_surface_codex_home_override_uses_custom_home(tmp_path: Path) -> None:
    custom_home = tmp_path / "custom-codex-home"
    output_dir = tmp_path / "output"
    script = f"""
        import {{ codexEnvironment }} from './scripts/agent-runtime/run-local-eval-test.mjs';
        const runtime = codexEnvironment(
          {{ repoRoot: '/tmp/repo', codexHomeMode: 'isolated', codexHome: {json.dumps(str(custom_home))} }},
          {json.dumps(str(output_dir))}
        );
        console.log(JSON.stringify({{
          codeHome: runtime.env.CODEX_HOME,
          telemetry: runtime.telemetry
        }}));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["codeHome"] == str(custom_home)
    assert payload["telemetry"] == {
        "codex_home_mode": "custom",
        "codex_home_isolated": True,
        "codex_home_path": str(custom_home),
    }
    assert custom_home.is_dir()


def test_instruction_surface_codex_exec_isolates_codex_home_by_default(tmp_path: Path) -> None:
    stale_codex_home = tmp_path / "stale-codex-home"
    stale_skill = stale_codex_home / "plugins/cache/local/charness/0.5.21/skills/issue/SKILL.md"
    stale_skill.parent.mkdir(parents=True)
    stale_skill.write_text("# stale installed issue skill\n", encoding="utf-8")

    workspace_path = tmp_path / "workspace"
    workspace_path.mkdir()
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(
        json.dumps(
            {
                "schemaVersion": "cautilus.evaluation_cases.v1",
                "suiteId": "codex-home-isolation",
                "evaluations": [
                    {
                        "evaluationId": "repo-local-instruction-surface",
                        "prompt": "Route this request.",
                        "instructionSurface": {
                            "surfaceLabel": "repo-local",
                            "files": [
                                {
                                    "path": "AGENTS.md",
                                    "content": "# repo local instructions\n",
                                }
                            ],
                        },
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_codex = fake_bin / "codex"
    fake_codex.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys

output_file = sys.argv[sys.argv.index("-o") + 1]
stale_home = os.environ["STALE_CODEX_HOME"]
codex_home = os.environ.get("CODEX_HOME", "")
loaded = (
    [os.path.join(stale_home, "plugins/cache/local/charness/0.5.21/skills/issue/SKILL.md")]
    if codex_home == stale_home
    else [os.path.join(os.getcwd(), "AGENTS.md")]
)
with open(output_file, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": f"CODEX_HOME={codex_home}",
            "entryFile": os.path.join(os.getcwd(), "AGENTS.md"),
            "loadedInstructionFiles": loaded,
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": "none",
                "bootstrapHelper": "none",
                "workSkill": "none",
                "selectedSupport": "none",
                "firstToolCall": "none",
                "reasonSummary": "fake codex",
            },
        },
        handle,
    )
""",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)

    output_path = tmp_path / "observed.json"
    artifact_dir = tmp_path / "artifacts"
    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ.get('PATH', '')}",
        "CODEX_HOME": str(stale_codex_home),
        "STALE_CODEX_HOME": str(stale_codex_home),
    }
    result = subprocess.run(
        [
            "node",
            "scripts/agent-runtime/run-local-eval-test.mjs",
            "--repo-root",
            str(ROOT),
            "--workspace",
            str(workspace_path),
            "--cases-file",
            str(cases_path),
            "--output-file",
            str(output_path),
            "--artifact-dir",
            str(artifact_dir),
            "--backend",
            "codex_exec",
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    evaluation = packet["evaluations"][0]
    assert evaluation["loadedInstructionFiles"] == ["AGENTS.md"]
    assert stale_skill.as_posix() not in json.dumps(evaluation, ensure_ascii=False)
    assert evaluation["telemetry"]["codex_home_mode"] == "isolated"
    assert evaluation["telemetry"]["codex_home_isolated"] is True
    assert evaluation["telemetry"]["codex_home_path"] != str(stale_codex_home)


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
