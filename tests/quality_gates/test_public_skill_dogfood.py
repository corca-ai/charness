from __future__ import annotations

from pathlib import Path

import yaml

from scripts.gates_support.public_skill_dogfood_lib import build_matrix

from .support import ROOT, run_script


def test_public_skill_dogfood_matrix_reports_prompt_artifact_and_evidence() -> None:
    payload = build_matrix(ROOT, ["achieve", "quality"])
    matrix = {row["skill_id"]: row for row in payload["matrix"]}

    achieve = matrix["achieve"]
    assert set(achieve) == {"skill_id", "prompt", "acceptance_evidence"}
    assert any("Goal Draft" in item for item in achieve["acceptance_evidence"])

    quality = matrix["quality"]
    assert set(quality) == {"skill_id", "prompt", "acceptance_evidence"}
    assert any("consumer prompt" in item for item in quality["acceptance_evidence"])


def test_public_skill_dogfood_wrappers_match_root_script() -> None:
    commands = [
        "scripts/gates/suggest_public_skill_dogfood.py",
        "skills/public/quality/scripts/suggest_public_skill_dogfood.py",
    ]
    payloads = []
    for command in commands:
        result = run_script(
            command,
            "--repo-root",
            str(ROOT),
            "--skill-id",
            "achieve",
            "--skill-id",
            "quality",
            "--detail",
        )
        assert result.returncode == 0, result.stderr
        payloads.append(yaml.safe_load(result.stdout))

    assert payloads[1] == payloads[0]


def test_public_skill_dogfood_wrappers_report_missing_policy_without_a_traceback(tmp_path: Path) -> None:
    consumer = tmp_path / "consumer"
    (consumer / "skills" / "support" / "x").mkdir(parents=True)
    commands = [
        "scripts/gates/suggest_public_skill_dogfood.py",
        "skills/public/quality/scripts/suggest_public_skill_dogfood.py",
        "plugins/charness/skills/quality/scripts/suggest_public_skill_dogfood.py",
    ]

    for command in commands:
        result = run_script(command, "--repo-root", str(consumer), "--detail")
        assert result.returncode == 0, result.stderr
        assert "Traceback" not in result.stderr
        payload = yaml.safe_load(result.stdout)
        assert payload["applicability"] == "not-applicable-missing-public-skill-validation-policy"
        assert payload["matrix"] == []

    root_json = run_script(commands[0], "--repo-root", str(consumer), "--detail")
    assert root_json.returncode == 0, root_json.stderr
    assert yaml.safe_load(root_json.stdout)["applicability"] == "not-applicable-missing-public-skill-validation-policy"

    human = run_script(commands[1], "--repo-root", str(consumer))
    assert human.returncode == 0, human.stderr
    assert "not-applicable-missing-public-skill-validation-policy" in human.stdout


def test_build_matrix_reports_missing_policy_directly(tmp_path: Path) -> None:
    consumer = tmp_path / "consumer"
    consumer.mkdir()

    payload = build_matrix(consumer, ["quality"])

    assert payload["applicability"] == "not-applicable-missing-public-skill-validation-policy"
    assert payload["matrix"] == []


def test_dogfood_markdown_keeps_contract_prose_without_case_list() -> None:
    markdown = (ROOT / "docs" / "public-skill-dogfood.md").read_text(encoding="utf-8")
    assert "## Current Required Reviewed Skills" not in markdown
    assert "Canonical machine-readable consumer-dogfood state" in markdown
    assert "## Review Posture" in markdown
