from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from scripts.public_skill_dogfood_lib import build_matrix
from scripts.public_skill_dogfood_validation_lib import (
    ValidationError,
    load_registry,
    validate_registry,
)
from scripts.public_skill_validation_lib import ValidationError as PolicyValidationError

ROOT = Path(__file__).resolve().parents[1]
_suggest_public_skill_dogfood = import_repo_module(
    ROOT / "scripts" / "suggest_public_skill_dogfood.py",
    "scripts.suggest_public_skill_dogfood",
)


def run_suggest_public_skill_dogfood(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["suggest_public_skill_dogfood.py", *args])
    try:
        returncode = _suggest_public_skill_dogfood.main()
    except SystemExit as exc:
        returncode = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


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


def scaffold_case(repo: Path, skill_id: str) -> dict[str, object]:
    payload = build_matrix(repo, [skill_id])
    return payload["matrix"][0]


def base_registry(repo: Path) -> dict[str, object]:
    scaffold = scaffold_case(repo, "demo")
    return {
        "schema_version": 1,
        "review_required_skills": ["demo"],
        "cases": [
            {
                **scaffold,
            }
        ],
    }


def test_validate_public_skill_dogfood_passes_for_current_real_registry() -> None:
    validate_registry(load_registry(ROOT), ROOT)


def test_validate_public_skill_dogfood_checks_current_scaffold_drift(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    registry = base_registry(repo)
    registry["cases"][0]["prompt"] = "Drifted prompt."
    write_registry(repo, registry)

    with pytest.raises(ValidationError, match="drifted from current scaffold"):
        validate_registry(load_registry(repo), repo)


def test_validate_public_skill_dogfood_requires_reviewed_case_for_required_skill(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    registry = base_registry(repo)
    registry["cases"] = []
    write_registry(repo, registry)

    with pytest.raises(ValidationError, match="missing required dogfood case"):
        validate_registry(load_registry(repo), repo)


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


def test_suggest_cli_warns_on_description_fallback_prompt(tmp_path: Path, monkeypatch, capsys) -> None:
    # The seeded `demo` skill has no PROMPT_HINTS entry, so its scaffold prompt
    # is the frontmatter description; the row must say so and the CLI must warn
    # (advisory only -- exit stays 0). This is the gap that left `prove` with
    # an unrealistic prompt until 2026-07-17.
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")

    result = run_suggest_public_skill_dogfood(
        monkeypatch, capsys, "--repo-root", str(repo), "--skill-id", "demo", "--detail"
    )
    assert result.returncode == 0, result.stderr
    row = yaml.safe_load(result.stdout)["matrix"][0]
    assert set(row) == {"skill_id", "prompt", "acceptance_evidence"}
    assert "frontmatter-description fallback" in result.stderr


def test_prompt_hinted_row_carries_no_fallback_flag_or_warning() -> None:
    report = build_matrix(ROOT, ["prove"])
    row = report["matrix"][0]
    assert set(row) == {"skill_id", "prompt", "acceptance_evidence"}
    from scripts.public_skill_dogfood_lib import prompt_fallback_warnings

    assert prompt_fallback_warnings(report) == []


def test_format_human_renders_fallback_warning_line(tmp_path: Path) -> None:
    # Covers the format_human WARNING branch the changed-line mutation gate
    # flagged as uncovered (release quality run, 2026-07-17).
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    from scripts.public_skill_dogfood_lib import format_human

    report = build_matrix(repo, ["demo"])
    rendered = format_human(report)
    assert "WARNING: prompt is the frontmatter-description fallback" in rendered
    assert "add a realistic consumer prompt" in rendered


def test_quality_skill_cli_copy_emits_fallback_stderr_warning(tmp_path: Path) -> None:
    # The quality-skill wrapper is a portable copy of the root CLI; its stderr
    # advisory line must fire the same way (uncovered-line gate, 2026-07-17).
    import subprocess

    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills" / "public" / "quality" / "scripts" / "suggest_public_skill_dogfood.py"),
            "--repo-root",
            str(repo),
            "--skill-id",
            "demo",
            "--detail",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert set(yaml.safe_load(result.stdout)["matrix"][0]) == {
        "skill_id",
        "prompt",
        "acceptance_evidence",
    }
    assert "frontmatter-description fallback" in result.stderr
