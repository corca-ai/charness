from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

from .test_quality_artifact import cautilus_supports, run_script

ROOT = Path(__file__).resolve().parents[1]
requires_cautilus = pytest.mark.skipif(
    not cautilus_supports("discover", "scenarios", "propose"),
    reason="cautilus with the `discover scenarios propose` surface is required for live chatbot proposal eval tests",
)

_RUN_EVALS = load_script_module(
    "run_evals_for_test",
    ROOT / "scripts" / "run_evals.py",
)

_VALIDATE_SCENARIOS = load_script_module(
    "validate_cautilus_scenarios_for_test",
    ROOT / "scripts" / "validate_cautilus_scenarios.py",
)


def _run_evals(*args: str):
    return run_loaded_script_main(
        "run_evals.py",
        _RUN_EVALS,
        *args,
        cli_error_names=("EvalError", "ValidationError", "ExportError"),
        cli_error_types=(_RUN_EVALS.EvalError, json.JSONDecodeError, shutil.Error),
    )


def _run_validate_scenarios(*args: str):
    return run_loaded_script_main("validate_cautilus_scenarios.py", _VALIDATE_SCENARIOS, *args)


def test_run_evals_supports_scenario_filter() -> None:
    result = _run_evals(
        "--repo-root",
        str(ROOT),
        "--scenario-id", "skill-valid",
        "--scenario-id", "doc-links-valid",
        "--jobs", "2",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.index("PASS skill-valid") < result.stdout.index("PASS doc-links-valid")
    assert "Ran 2 eval scenario(s)." in result.stdout


def test_run_evals_sequential_jobs_and_rejects_negative_jobs() -> None:
    result = _run_evals(
        "--repo-root",
        str(ROOT),
        "--scenario-id",
        "skill-valid",
        "--scenario-id",
        "doc-links-valid",
        "--jobs",
        "1",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.index("PASS skill-valid") < result.stdout.index("PASS doc-links-valid")

    rejected = _run_evals("--repo-root", str(ROOT), "--jobs", "-1")
    assert rejected.returncode == 1
    assert "--jobs must be zero or a positive integer" in rejected.stderr


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
    result = _run_validate_scenarios("--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_issue_evaluator_profile_includes_sibling_search_concept_fixture() -> None:
    registry = json.loads((ROOT / "evals" / "cautilus" / "scenarios.json").read_text(encoding="utf-8"))
    issue_entry = next(
        entry
        for entry in registry["profiles"]["evaluator-required"]["skills"]
        if entry["skill_id"] == "issue"
    )

    assert "issue-sibling-search-concept-fixtures" in issue_entry["scenario_ids"]


@requires_cautilus
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
