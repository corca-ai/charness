from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

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
    payload = yaml.safe_load(result.stdout)
    assert payload["schemaVersion"] == "charness.quality.behavior_test_recommendation.v1"
    assert payload["state"] == "recommend_only"
    assert payload["cautilusContract"]["requestSchema"] == "cautilus.robustness_request.v1"
    assert payload["cautilusContract"]["planSchema"] == "cautilus.robustness_plan.v1"
    assert payload["cautilusContract"]["reportSchema"] == "cautilus.robustness_report.v1"
    assert "recover" in payload["cautilusContract"]["expectedRelations"]
    assert "inconclusive" in payload["cautilusContract"]["relationStatuses"]
    assert payload["suggestedRequest"]["requestedMutationKinds"] == ["stimulus"]
    assert "caseResults.relationStatus" in payload["expectedResultFields"]
    # recommend_only with no explicit --limitation gets the default caveat, and
    # generatedAt is truncated to whole seconds (no microseconds).
    assert payload["suggestedRequest"]["limitations"] == [
        "recommend-only: no live Cautilus run was requested or executed"
    ]
    assert payload["generatedAt"].endswith("Z")
    assert "." not in payload["generatedAt"]
    assert "executedReportRef" not in payload


def test_quality_behavior_recommendation_defaults_mutation_kind_to_stimulus(monkeypatch, capsys) -> None:
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
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["suggestedRequest"]["requestedMutationKinds"] == ["stimulus"]
    assert payload["suggestedRequest"]["sourceEvidenceRefs"] == []


def test_quality_behavior_recommendation_explicit_recommend_only_state_still_defaults_limitation() -> None:
    # Run out-of-process: an in-process --state value is the same interned
    # string literal as STATES' "recommend_only", which cannot distinguish
    # `==` from `is` on the build_payload branch condition.
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
            "recommend_only",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["suggestedRequest"]["limitations"] == [
        "recommend-only: no live Cautilus run was requested or executed"
    ]


@pytest.mark.parametrize("non_recommend_state", ["blocked", "unavailable"])
def test_quality_behavior_recommendation_non_recommend_only_state_has_no_default_limitation(
    monkeypatch, capsys, non_recommend_state: str
) -> None:
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
        "--state",
        non_recommend_state,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["suggestedRequest"]["limitations"] == []
    assert "executedReportRef" not in payload


def test_quality_behavior_recommendation_explicit_limitation_is_not_overridden(monkeypatch, capsys) -> None:
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
        "--limitation",
        "manual caveat",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["suggestedRequest"]["limitations"] == ["manual caveat"]


def test_quality_behavior_recommendation_executed_state_records_report_ref(monkeypatch, capsys) -> None:
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
        "--state",
        "executed",
        "--report-ref",
        "charness-artifacts/probe/cautilus-report.json",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "executed"
    assert payload["executedReportRef"] == "charness-artifacts/probe/cautilus-report.json"


def test_quality_behavior_recommendation_splits_comma_values_and_drops_empty_segments(
    monkeypatch, capsys
) -> None:
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
        "a,,b",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["suggestedRequest"]["sourceEvidenceRefs"] == ["a", "b"]


def test_quality_behavior_recommendation_can_render_markdown_gate(monkeypatch, capsys) -> None:
    result = run_recommend_behavior_test(
        monkeypatch,
        capsys,
        "--behavior-seam",
        "skill-routing",
        "--subject-ref",
        "skills/public/quality/SKILL.md",
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


def test_render_markdown_renders_every_field_with_populated_lists() -> None:
    payload = _recommend_behavior_test.build_payload(
        argparse.Namespace(
            behavior_seam="skill-routing",
            subject_ref="skills/public/quality/SKILL.md",
            intent="operator_behavior",
            risk_focus="wrong skill selected",
            deterministic_gap="static checks cannot prove routing judgment",
            source_evidence_ref=["docs/a.json", "docs/b.json"],
            mutation_kind=["stimulus", "implementation"],
            limitation=[],
            state="recommend_only",
            report_ref=None,
        )
    )

    rendered = _recommend_behavior_test.render_markdown(payload)

    assert rendered == "\n".join(
        [
            "- active NON_AUTOMATABLE: recommend Cautilus robustness proof for `skill-routing`.",
            "  - state: `recommend_only`",
            "  - deterministic gap: static checks cannot prove routing judgment",
            "  - Cautilus request: `cautilus.robustness_request.v1`",
            "  - Cautilus report: `cautilus.robustness_report.v1`",
            "  - subject: `skills/public/quality/SKILL.md`",
            "  - risk focus: wrong skill selected",
            "  - mutation kinds: stimulus, implementation",
            "  - source evidence: docs/a.json, docs/b.json",
        ]
    )


def test_render_markdown_reports_missing_when_lists_are_empty() -> None:
    payload = _recommend_behavior_test.build_payload(
        argparse.Namespace(
            behavior_seam="skill-routing",
            subject_ref="skills/public/quality/SKILL.md",
            intent="operator_behavior",
            risk_focus="wrong skill selected",
            deterministic_gap="static checks cannot prove routing judgment",
            source_evidence_ref=[],
            mutation_kind=[],
            limitation=[],
            state="recommend_only",
            report_ref=None,
        )
    )
    payload["suggestedRequest"]["requestedMutationKinds"] = []

    rendered = _recommend_behavior_test.render_markdown(payload)

    assert "  - mutation kinds: none" in rendered
    assert "  - source evidence: missing" in rendered


@pytest.mark.parametrize(
    "missing_flag",
    ["--behavior-seam", "--subject-ref", "--risk-focus", "--deterministic-gap"],
)
def test_build_parser_requires_every_core_flag(missing_flag: str) -> None:
    all_flags = {
        "--behavior-seam": "skill-routing",
        "--subject-ref": "skills/public/quality/SKILL.md",
        "--risk-focus": "wrong skill selected",
        "--deterministic-gap": "static checks cannot prove routing judgment",
    }
    argv: list[str] = []
    for flag, value in all_flags.items():
        if flag == missing_flag:
            continue
        argv.extend([flag, value])

    result = subprocess.run(
        ["python3", SCRIPT, *argv],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert missing_flag in result.stderr


def test_split_values_drops_blank_and_whitespace_only_segments() -> None:
    assert _recommend_behavior_test._split_values(["a, ,b", " "]) == ["a", "b"]


def test_quality_behavior_recommendation_summary_yaml_is_structured(monkeypatch, capsys) -> None:
    args = (
        "--behavior-seam", "skill-routing",
        "--subject-ref", "skills/public/quality/SKILL.md",
        "--risk-focus", "wrong skill selected",
        "--deterministic-gap", "static checks cannot prove routing judgment",
        "--summary",
    )
    yaml_result = run_recommend_behavior_test(monkeypatch, capsys, *args)
    assert yaml_result.returncode == 0
    assert yaml.safe_load(yaml_result.stdout)["behaviorSeam"] == "skill-routing"


@pytest.mark.parametrize("structured_mode", ["--summary", "--detail"])
def test_quality_behavior_recommendation_rejects_markdown_with_structured_mode(
    structured_mode: str,
) -> None:
    result = subprocess.run(
        [
            "python3",
            SCRIPT,
            "--behavior-seam",
            "skill-routing",
            "--subject-ref",
            "skills/public/quality/SKILL.md",
            "--risk-focus",
            "wrong skill selected",
            "--deterministic-gap",
            "static checks cannot prove routing judgment",
            "--markdown",
            structured_mode,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--markdown cannot be combined" in result.stderr


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
