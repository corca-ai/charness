from __future__ import annotations

import json
from pathlib import Path

from .charness_cli.support import ROOT
from .test_quality_artifact import run_script


def seed_repo(tmp_path: Path, artifact_body: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "cautilus-adapters").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "skills" / "public" / "impl").mkdir(parents=True)
    (repo / "charness-artifacts" / "cautilus").mkdir(parents=True)
    (repo / "docs" / "public-skill-validation.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "tiers": {
                    "smoke-only": [],
                    "hitl-recommended": [],
                    "evaluator-required": ["impl"],
                },
                "adapter_requirements": {
                    "required": ["impl"],
                    "adapter-free": [],
                },
                "fallback_policy": {
                    "allow": ["impl"],
                    "visible": [],
                    "block": [],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "skills" / "public" / "impl" / "SKILL.md").write_text("# Impl\n", encoding="utf-8")
    (repo / ".agents" / "cautilus-adapters" / "chatbot-proposals.yaml").write_text("version: 1\n", encoding="utf-8")
    if artifact_body is not None:
        (repo / "charness-artifacts" / "cautilus" / "latest.md").write_text(artifact_body, encoding="utf-8")
    return repo


def test_validate_cautilus_proof_requires_artifact_for_prompt_changes(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
    )
    assert result.returncode == 1
    assert "require refreshing `charness-artifacts/cautilus/latest.md`" in result.stderr


def test_validate_cautilus_proof_requires_ab_compare_for_improve_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "- claim: `improve`",
                "",
                "## Validation Goal",
                "",
                "- goal: `improve`",
                "- reason: demo",
                "",
                "## Change Intent",
                "",
                "- prompt_affecting_change",
                "- skill_core_change",
                "- scenario_review_change",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus instruction-surface test --repo-root .`",
                "",
                "## Regression Proof",
                "",
                "- instruction-surface result: 1 passed / 0 failed / 0 blocked",
                "",
                "## Scenario Review",
                "",
                "- scenario: impl request still routes through impl and keeps adapter-sensitive review visible",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 1
    assert "`## A/B Compare` is required when `goal: improve`" in result.stderr


def test_validate_cautilus_proof_accepts_preserve_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "- claim: `preserve`",
                "",
                "## Validation Goal",
                "",
                "- goal: `preserve`",
                "- reason: demo",
                "",
                "## Change Intent",
                "",
                "- prompt_affecting_change",
                "- skill_core_change",
                "- scenario_review_change",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus instruction-surface test --repo-root .`",
                "",
                "## Regression Proof",
                "",
                "- instruction-surface result: 1 passed / 0 failed / 0 blocked",
                "",
                "## Scenario Review",
                "",
                "- scenario: impl request still routes through impl and keeps adapter-sensitive review visible",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 0, result.stderr


def test_validate_cautilus_proof_treats_named_cautilus_adapter_as_prompt_affecting(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        ".agents/cautilus-adapters/chatbot-proposals.yaml",
    )
    assert result.returncode == 1
    assert "require refreshing `charness-artifacts/cautilus/latest.md`" in result.stderr


def test_plan_cautilus_proof_recommends_skill_dogfood_and_scenario_followups() -> None:
    result = run_script(
        "scripts/plan_cautilus_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/create-skill/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["changed_public_skills"] == ["create-skill"]
    recommendation = payload["skill_validation_recommendations"][0]
    assert recommendation["skill_id"] == "create-skill"
    assert recommendation["validation_tier"] == "evaluator-required"
    assert any("docs/public-skill-dogfood.json" in note for note in recommendation["notes"])
    assert any(
        "python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id create-skill --json" == item
        for item in payload["recommended_followups"]
    )
    assert any("evals/cautilus/scenarios.json" in item for item in payload["recommended_followups"])


def test_plan_cautilus_proof_fails_closed_when_public_skill_policy_is_invalid(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "skills" / "public" / "demo").mkdir(parents=True)
    (repo / "docs" / "public-skill-validation.json").write_text("{not json\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    result = run_script(
        "scripts/plan_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/demo/SKILL.md",
        "--json",
    )

    assert result.returncode == 1
    assert "public-skill validation policy invalid while planning Cautilus proof" in result.stderr


def test_plan_cautilus_proof_adaptive_runs_without_ask_for_scenario_review() -> None:
    result = run_script(
        "scripts/plan_cautilus_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/create-skill/SKILL.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["run_mode"] == "adaptive"
    assert payload["must_ask_before_running"] is False
    assert payload["scenario_registry_review_required"] is True
    assert payload["next_action"] == "run-proof-and-refresh-artifact"
