from __future__ import annotations

import json
from pathlib import Path

from tests.quality_gates.support import run_script


def _seed_skill(repo: Path, skill_id: str, output_shape_body: str) -> None:
    skill_dir = repo / "skills" / "public" / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_id}\ndescription: demo\n---\n\n# {skill_id}\n\n## Output Shape\n\n{output_shape_body}\n",
        encoding="utf-8",
    )


def test_survey_flags_classifier_schema_without_validator(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_skill(
        repo,
        "demo",
        "- F1 | bin: act-before-ship | evidence: strong | action: fix | note: x\n",
    )
    result = run_script("scripts/validate_skill_output_schemas.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    demo = next(row for row in payload["skills"] if row["skill"] == "demo")
    assert demo["classifier_schema"] is True
    assert demo["gap"] is True
    assert payload["gap_count"] == 1


def test_survey_clears_gap_when_validator_file_exists(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_skill(
        repo,
        "demo",
        "- Q1 | urgency: must-resolve | depends-on: null | action: spec | note: x\n",
    )
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "validate_demo_artifact.py").write_text("# stub\n", encoding="utf-8")
    result = run_script("scripts/validate_skill_output_schemas.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    demo = next(row for row in payload["skills"] if row["skill"] == "demo")
    assert demo["classifier_schema"] is True
    assert demo["gap"] is False
    assert demo["validator"] == "validate_demo_artifact.py"


def test_survey_ignores_prose_only_output_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_skill(repo, "demo", "- `Concept`\n- `Next Step`\n- plain prose bullet\n")
    result = run_script("scripts/validate_skill_output_schemas.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    demo = next(row for row in payload["skills"] if row["skill"] == "demo")
    assert demo["classifier_schema"] is False
    assert demo["gap"] is False


def test_survey_repo_is_clean(tmp_path: Path) -> None:
    # The real repo must have no classifier-bearing Output Shape without a validator.
    result = run_script("scripts/validate_skill_output_schemas.py", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["gap_count"] == 0, payload