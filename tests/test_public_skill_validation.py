from __future__ import annotations

import json
import shutil
from pathlib import Path

from .test_quality_artifact import run_script

ROOT = Path(__file__).resolve().parents[1]


def with_fallback_policy(policy: dict[str, object]) -> dict[str, object]:
    updated = json.loads(json.dumps(policy))
    updated.setdefault(
        "fallback_policy",
        {
            "allow": [],
            "visible": [],
            "block": [],
        },
    )
    return updated


def seed_repo(tmp_path: Path, *, policy: dict[str, object]) -> Path:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    public_root = repo / "skills" / "public"
    docs_dir.mkdir(parents=True)
    public_root.mkdir(parents=True)
    (docs_dir / "public-skill-validation.json").write_text(
        json.dumps(with_fallback_policy(policy), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return repo


def seed_skill(repo: Path, skill_id: str, *, adapter: bool) -> None:
    skill_dir = repo / "skills" / "public" / skill_id
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {skill_id}",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "## References",
                "",
                "- `references/demo.md`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    references_dir = skill_dir / "references"
    references_dir.mkdir()
    (references_dir / "demo.md").write_text("# Demo\n", encoding="utf-8")
    if adapter:
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "adapter.example.yaml", skill_dir / "adapter.example.yaml")
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "scripts" / "resolve_adapter.py", scripts_dir / "resolve_adapter.py")
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "scripts" / "init_adapter.py", scripts_dir / "init_adapter.py")


def test_validate_public_skill_validation_requires_full_partition(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    result = run_script("scripts/validate-public-skill-validation.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "does not classify every public skill" in result.stderr
    assert "`demo-b`" in result.stderr
    assert "`tiers.smoke-only`" in result.stderr
    assert "`tiers.hitl-recommended`" in result.stderr
    assert "`tiers.evaluator-required`" in result.stderr
    assert "suggest-public-skill-validation.py" in result.stderr


def test_validate_public_skill_validation_reports_missing_adapter_requirement_bucket(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a", "demo-b"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a", "demo-b"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    result = run_script("scripts/validate-public-skill-validation.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "adapter_requirements does not classify every public skill" in result.stderr
    assert "`demo-b`" in result.stderr
    assert "`adapter_requirements.required`" in result.stderr
    assert "`adapter_requirements.adapter-free`" in result.stderr
    assert "suggest-public-skill-validation.py" in result.stderr


def test_validate_public_skill_validation_requires_adapter_contract_for_required_skill(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=False)

    result = run_script("scripts/validate-public-skill-validation.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "adapter-required skill is missing `adapter.example.yaml`" in result.stderr


def test_validate_public_skill_validation_rejects_adapter_helpers_for_adapter_free_skill(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": [],
                "adapter-free": ["demo-a"],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)

    result = run_script("scripts/validate-public-skill-validation.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "adapter-free skill should not ship `adapter.example.yaml`" in result.stderr


def test_suggest_public_skill_validation_reports_missing_bucket_choices(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    result = run_script("scripts/suggest-public-skill-validation.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["missing_tiers"] == ["demo-b"]
    assert payload["missing_adapter_requirements"] == ["demo-b"]
    assert payload["missing_fallback_policy"] == ["demo-b"]
    assert payload["suggestions"] == [
        {
            "skill_id": "demo-b",
            "missing_fields": {
                "tiers": True,
                "adapter_requirements": True,
                "fallback_policy": True,
            },
            "choose_one_of": {
                "tiers": [
                    "tiers.smoke-only",
                    "tiers.hitl-recommended",
                    "tiers.evaluator-required",
                ],
                "adapter_requirements": [
                    "adapter_requirements.required",
                    "adapter_requirements.adapter-free",
                ],
                "fallback_policy": [
                    "fallback_policy.allow",
                    "fallback_policy.visible",
                    "fallback_policy.block",
                ],
            },
        }
    ]

    human = run_script("scripts/suggest-public-skill-validation.py", "--repo-root", str(repo))
    assert human.returncode == 1
    assert "`demo-b`" in human.stdout
    assert "`tiers.hitl-recommended`" in human.stdout
    assert "`adapter_requirements.adapter-free`" in human.stdout
    assert "`fallback_policy.visible`" in human.stdout
