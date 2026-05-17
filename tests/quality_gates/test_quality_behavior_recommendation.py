from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_quality_behavior_recommendation_emits_cautilus_robustness_contract() -> None:
    result = subprocess.run(
        [
            "python3",
            "skills/public/quality/scripts/recommend_behavior_test.py",
            "--behavior-seam",
            "handoff-resumption",
            "--subject-ref",
            "skills/public/handoff/SKILL.md",
            "--risk-focus",
            "resume after compacted work",
            "--deterministic-gap",
            "static docs cannot prove multi-turn recovery behavior",
            "--source-evidence-ref",
            "charness-artifacts/spec/quality-cautilus-behavior-testing-contract.md",
            "--mutation-kind",
            "stimulus",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schemaVersion"] == "charness.quality.behavior_test_recommendation.v1"
    assert payload["state"] == "recommend_only"
    assert payload["cautilusContract"]["requestSchema"] == "cautilus.robustness_request.v1"
    assert payload["cautilusContract"]["planSchema"] == "cautilus.robustness_plan.v1"
    assert payload["cautilusContract"]["reportSchema"] == "cautilus.robustness_report.v1"
    assert "recover" in payload["cautilusContract"]["expectedRelations"]
    assert "inconclusive" in payload["cautilusContract"]["relationStatuses"]
    assert payload["suggestedRequest"]["requestedMutationKinds"] == ["stimulus"]
    assert "caseResults.relationStatus" in payload["expectedResultFields"]


def test_quality_behavior_recommendation_can_render_markdown_gate() -> None:
    result = subprocess.run(
        [
            "python3",
            "skills/public/quality/scripts/recommend_behavior_test.py",
            "--behavior-seam",
            "skill-routing",
            "--subject-ref",
            "skills/public/find-skills/SKILL.md",
            "--risk-focus",
            "wrong skill selected for support-backed tasks",
            "--deterministic-gap",
            "static trigger checks cannot prove multi-turn routing judgment",
            "--source-evidence-ref",
            "docs/public-skill-dogfood.json",
            "--markdown",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "- active NON_AUTOMATABLE: recommend Cautilus robustness proof" in result.stdout
    assert "Cautilus request: `cautilus.robustness_request.v1`" in result.stdout
    assert "state: `recommend_only`" in result.stdout


def test_quality_behavior_recommendation_executed_requires_report_ref() -> None:
    result = subprocess.run(
        [
            "python3",
            "skills/public/quality/scripts/recommend_behavior_test.py",
            "--behavior-seam",
            "handoff-resumption",
            "--subject-ref",
            "skills/public/handoff/SKILL.md",
            "--risk-focus",
            "resume after compacted work",
            "--deterministic-gap",
            "static docs cannot prove multi-turn recovery behavior",
            "--state",
            "executed",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--state executed requires --report-ref" in result.stderr
