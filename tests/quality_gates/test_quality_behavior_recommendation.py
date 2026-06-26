from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "skills/public/quality/scripts/recommend_behavior_test.py"
_recommend_behavior_test = import_repo_module(ROOT / SCRIPT, "skills.public.quality.scripts.recommend_behavior_test")


def run_recommend_behavior_test(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [SCRIPT, *args])
    code = _recommend_behavior_test.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_quality_behavior_recommendation_emits_cautilus_robustness_contract(monkeypatch, capsys) -> None:
    result = run_recommend_behavior_test(
        monkeypatch,
        capsys,
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


def test_quality_behavior_recommendation_can_render_markdown_gate(monkeypatch, capsys) -> None:
    result = run_recommend_behavior_test(
        monkeypatch,
        capsys,
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
    )

    assert result.returncode == 0, result.stderr
    assert "- active NON_AUTOMATABLE: recommend Cautilus robustness proof" in result.stdout
    assert "Cautilus request: `cautilus.robustness_request.v1`" in result.stdout
    assert "state: `recommend_only`" in result.stdout


def test_quality_behavior_recommendation_executed_requires_report_ref() -> None:
    result = subprocess.run(
        [
            "python3",
            SCRIPT,
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
