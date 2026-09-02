from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.public_skill_dogfood_lib import build_matrix
from scripts.public_skill_dogfood_validation_lib import (
    ValidationError,
    load_registry,
    validate_registry,
)
from scripts.public_skill_validation_lib import ValidationError as PolicyValidationError
from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
_suggest_public_skill_dogfood = load_script_module(
    "suggest_public_skill_dogfood_under_test",
    ROOT / "scripts" / "suggest_public_skill_dogfood.py",
)


def run_suggest_public_skill_dogfood(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    del monkeypatch, capsys
    result = run_loaded_script_main("suggest_public_skill_dogfood.py", _suggest_public_skill_dogfood, *args)
    return SimpleNamespace(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)


def seed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    public_root = repo / "skills" / "public"
    docs_dir.mkdir(parents=True)
    public_root.mkdir(parents=True)
    (docs_dir / "public-skill-validation.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "tiers": {
                    "smoke-only": [],
                    "hitl-recommended": [],
                    "evaluator-required": ["demo"],
                },
                "adapter_requirements": {
                    "required": [],
                    "adapter-free": ["demo"],
                },
                "fallback_policy": {
                    "allow": ["demo"],
                    "visible": [],
                    "block": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def write_registry(repo: Path, registry: dict[str, object]) -> None:
    (repo / "docs" / "public-skill-dogfood.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def seed_skill(repo: Path, skill_id: str, *, description: str) -> None:
    skill_dir = repo / "skills" / "public" / skill_id
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {skill_id}",
                f'description: "{description}"',
                "---",
                "",
                "# Demo",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def base_registry(repo: Path) -> dict[str, object]:
    return {
        "schema_version": 1,
        "review_required_skills": ["demo"],
        "cases": [
            {
                "skill_id": "demo",
                "prompt": "Review the demo skill as a consumer.",
                "acceptance_evidence": [
                    "routes the prompt to `demo`",
                    "returns a reviewable result",
                ],
            }
        ],
    }


def test_validate_public_skill_dogfood_passes_for_current_real_registry() -> None:
    validate_registry(load_registry(ROOT), ROOT)


def test_validate_public_skill_dogfood_accepts_registry_owned_prompt_and_evidence(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    registry = base_registry(repo)
    registry["cases"][0]["prompt"] = "A reviewed consumer prompt chosen for this repo."
    registry["cases"][0]["acceptance_evidence"] = ["The consumer result is directly reviewable."]
    write_registry(repo, registry)

    assert validate_registry(load_registry(repo), repo)["cases"] == registry["cases"]


def test_validate_public_skill_dogfood_requires_reviewed_case_for_required_skill(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    registry = base_registry(repo)
    registry["cases"] = []
    write_registry(repo, registry)

    with pytest.raises(ValidationError, match="missing required dogfood case"):
        validate_registry(load_registry(repo), repo)

    with pytest.raises(ValueError, match="registry is missing case.*demo"):
        build_matrix(repo, ["demo"])


def test_validate_public_skill_dogfood_rejects_historical_case_fields(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    registry = base_registry(repo)
    registry["cases"][0]["observed_evidence"] = ["Historical review detail."]
    write_registry(repo, registry)

    with pytest.raises(ValidationError, match="unexpected field.*observed_evidence"):
        validate_registry(load_registry(repo), repo)


def test_suggest_public_skill_dogfood_cli_emits_requested_matrix(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    write_registry(repo, base_registry(repo))

    result = run_suggest_public_skill_dogfood(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--skill-id",
        "demo",
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert set(payload["matrix"][0]) == {"skill_id", "prompt", "acceptance_evidence"}


def test_suggest_public_skill_dogfood_reports_policy_absence_as_not_applicable(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "consumer"
    (repo / "skills" / "support" / "x").mkdir(parents=True)

    result = run_suggest_public_skill_dogfood(
        monkeypatch, capsys, "--repo-root", str(repo), "--detail"
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["applicability"] == "not-applicable-missing-public-skill-validation-policy"
    assert payload["policy_path"] == "docs/public-skill-validation.json"
    assert payload["matrix"] == []


def test_build_matrix_rejects_a_policy_path_that_is_not_a_regular_file(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    (repo / "docs" / "public-skill-validation.json").mkdir(parents=True)

    with pytest.raises(PolicyValidationError, match="missing `docs/public-skill-validation.json`"):
        build_matrix(repo, [])


def test_policy_absence_is_typed_in_root_human_output(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "consumer"
    (repo / "skills" / "support" / "x").mkdir(parents=True)

    root_result = run_suggest_public_skill_dogfood(monkeypatch, capsys, "--repo-root", str(repo))
    assert root_result.returncode == 0, root_result.stderr
    assert "not-applicable-missing-public-skill-validation-policy" in root_result.stdout


def test_suggest_public_skill_dogfood_cli_covers_json_human_and_unknown_paths(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Keep the CLI output branches in-process for changed-line coverage."""
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    write_registry(repo, base_registry(repo))

    json_result = run_suggest_public_skill_dogfood(
        monkeypatch, capsys, "--repo-root", str(repo), "--skill-id", "demo", "--detail"
    )
    assert json_result.returncode == 0
    assert yaml.safe_load(json_result.stdout)["matrix"][0]["skill_id"] == "demo"

    human_result = run_suggest_public_skill_dogfood(
        monkeypatch, capsys, "--repo-root", str(repo), "--skill-id", "demo"
    )
    assert human_result.returncode == 0
    assert "Public skill consumer dogfood matrix:" in human_result.stdout

    unknown_result = run_suggest_public_skill_dogfood(
        monkeypatch, capsys, "--repo-root", str(repo), "--skill-id", "missing"
    )
    assert unknown_result.returncode == 1
    assert "Unknown public skill id(s): `missing`" in unknown_result.stderr


def test_suggest_cli_uses_registry_owned_prompt_without_warning(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    registry = base_registry(repo)
    registry["cases"][0]["prompt"] = "Use the reviewed prompt from the registry."
    write_registry(repo, registry)

    result = run_suggest_public_skill_dogfood(
        monkeypatch, capsys, "--repo-root", str(repo), "--skill-id", "demo", "--detail"
    )
    assert result.returncode == 0, result.stderr
    row = yaml.safe_load(result.stdout)["matrix"][0]
    assert set(row) == {"skill_id", "prompt", "acceptance_evidence"}
    assert row["prompt"] == "Use the reviewed prompt from the registry."
    assert result.stderr == ""


def test_registry_owned_row_carries_no_fallback_flag_or_warning() -> None:
    report = build_matrix(ROOT, ["prove"])
    row = report["matrix"][0]
    assert set(row) == {"skill_id", "prompt", "acceptance_evidence"}
    assert "frontmatter" not in row["prompt"]


def test_format_human_renders_registry_owned_case_without_warning(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    write_registry(repo, base_registry(repo))
    from scripts.public_skill_dogfood_lib import format_human

    report = build_matrix(repo, ["demo"])
    rendered = format_human(report)
    assert "Review the demo skill as a consumer." in rendered
    assert "WARNING" not in rendered


def test_quality_skill_cli_copy_uses_registry_without_warning(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    write_registry(repo, base_registry(repo))
    module = load_script_module(
        "suggest_public_skill_dogfood_copy_under_test",
        ROOT / "skills" / "public" / "quality" / "scripts" / "suggest_public_skill_dogfood.py",
    )
    result = run_loaded_script_main(
        "suggest_public_skill_dogfood.py",
        module,
        "--repo-root",
        str(repo),
        "--skill-id",
        "demo",
        "--detail",
    )
    assert result.returncode == 0, result.stderr
    assert set(yaml.safe_load(result.stdout)["matrix"][0]) == {
        "skill_id",
        "prompt",
        "acceptance_evidence",
    }
    assert result.stderr == ""
