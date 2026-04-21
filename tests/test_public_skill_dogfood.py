from __future__ import annotations

import json
import shutil
from pathlib import Path

from .test_quality_artifact import run_script

ROOT = Path(__file__).resolve().parents[1]


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


def seed_skill(repo: Path, skill_id: str, *, description: str, adapter: bool) -> None:
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
    if adapter:
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "adapter.example.yaml", skill_dir / "adapter.example.yaml")
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "scripts" / "resolve_adapter.py", scripts_dir / "resolve_adapter.py")
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "scripts" / "init_adapter.py", scripts_dir / "init_adapter.py")


def scaffold_case(repo: Path, skill_id: str) -> dict[str, object]:
    result = run_script(
        "scripts/suggest-public-skill-dogfood.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        skill_id,
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    return payload["matrix"][0]


def base_registry(repo: Path) -> dict[str, object]:
    scaffold = scaffold_case(repo, "demo")
    return {
        "schema_version": 1,
        "review_required_skills": ["demo"],
        "cases": [
            {
                **scaffold,
                "review_status": "reviewed",
                "reviewed_on": "2026-04-16",
                "observed_evidence": ["Manual review confirmed the demo routing."],
            }
        ],
    }


def test_validate_public_skill_dogfood_passes_for_current_real_registry() -> None:
    result = run_script("scripts/validate-public-skill-dogfood.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "Validated public skill dogfood registry" in result.stdout


def test_validate_public_skill_dogfood_checks_current_scaffold_drift(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.", adapter=False)
    registry = base_registry(repo)
    registry["cases"][0]["prompt"] = "Drifted prompt."
    write_registry(repo, registry)

    result = run_script("scripts/validate-public-skill-dogfood.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "drifted from current scaffold" in result.stderr


def test_validate_public_skill_dogfood_requires_reviewed_case_for_required_skill(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.", adapter=False)
    registry = base_registry(repo)
    registry["cases"] = []
    write_registry(repo, registry)

    result = run_script("scripts/validate-public-skill-dogfood.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required reviewed dogfood case" in result.stderr


def test_validate_public_skill_dogfood_requires_observed_evidence_for_reviewed_case(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    seed_skill(repo, "demo", description="Improve the demo skill first.", adapter=False)
    registry = base_registry(repo)
    registry["cases"][0]["observed_evidence"] = []
    write_registry(repo, registry)

    result = run_script("scripts/validate-public-skill-dogfood.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "observed_evidence" in result.stderr
