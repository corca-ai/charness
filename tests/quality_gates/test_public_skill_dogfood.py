from __future__ import annotations

import json

from .support import ROOT, run_script


def test_public_skill_dogfood_matrix_reports_prompt_artifact_and_evidence() -> None:
    result = run_script(
        "scripts/suggest-public-skill-dogfood.py",
        "--repo-root",
        str(ROOT),
        "--skill-id",
        "handoff",
        "--skill-id",
        "quality",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    matrix = {row["skill_id"]: row for row in payload["matrix"]}

    handoff = matrix["handoff"]
    assert handoff["expected_skill"] == "handoff"
    assert handoff["expected_artifact"] == "docs/handoff.md"
    assert handoff["validation_tier"] == "evaluator-required"
    assert handoff["adapter_requirement"] == "required"
    assert any("workflow trigger" in item for item in handoff["acceptance_evidence"])

    quality = matrix["quality"]
    assert quality["expected_skill"] == "quality"
    assert quality["expected_artifact"] == "charness-artifacts/quality/latest.md"
    assert quality["validation_tier"] == "hitl-recommended"
    assert quality["adapter_requirement"] == "required"
    assert any("consumer prompt" in item for item in quality["acceptance_evidence"])


def test_public_skill_dogfood_wrappers_match_root_script() -> None:
    commands = [
        "scripts/suggest-public-skill-dogfood.py",
        "skills/public/quality/scripts/suggest_public_skill_dogfood.py",
        "plugins/charness/skills/quality/scripts/suggest_public_skill_dogfood.py",
    ]
    payloads = []
    for command in commands:
        result = run_script(
            command,
            "--repo-root",
            str(ROOT),
            "--skill-id",
            "handoff",
            "--skill-id",
            "quality",
            "--json",
        )
        assert result.returncode == 0, result.stderr
        payloads.append(json.loads(result.stdout))

    assert payloads[1] == payloads[0]
    assert payloads[2] == payloads[0]
