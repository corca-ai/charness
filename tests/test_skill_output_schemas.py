from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_validate_skill_output_schemas = import_repo_module(
    ROOT / "scripts" / "validate_skill_output_schemas.py",
    "scripts.validate_skill_output_schemas",
)


def _seed_skill(repo: Path, skill_id: str, output_shape_body: str) -> None:
    skill_dir = repo / "skills" / "public" / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_id}\ndescription: demo\n---\n\n# {skill_id}\n\n## Output Shape\n\n{output_shape_body}\n",
        encoding="utf-8",
    )


def _survey_payload(repo: Path) -> dict[str, object]:
    rows = _validate_skill_output_schemas.survey(repo)
    gaps = [row for row in rows if row["gap"]]
    return {"skills": rows, "gap_count": len(gaps)}


def test_survey_flags_classifier_schema_without_validator(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_skill(
        repo,
        "demo",
        "- F1 | bin: act-before-ship | evidence: strong | action: fix | note: x\n",
    )
    payload = _survey_payload(repo)
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
    payload = _survey_payload(repo)
    demo = next(row for row in payload["skills"] if row["skill"] == "demo")
    assert demo["classifier_schema"] is True
    assert demo["gap"] is False
    assert demo["validator"] == "validate_demo_artifact.py"


def test_survey_ignores_prose_only_output_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_skill(repo, "demo", "- `Concept`\n- `Next Step`\n- plain prose bullet\n")
    payload = _survey_payload(repo)
    demo = next(row for row in payload["skills"] if row["skill"] == "demo")
    assert demo["classifier_schema"] is False
    assert demo["gap"] is False


def test_survey_repo_is_clean() -> None:
    # The real repo must have no classifier-bearing Output Shape without a validator.
    payload = _survey_payload(ROOT)
    assert payload["gap_count"] == 0, payload


def test_survey_main_emits_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_skill_output_schemas.py", "--repo-root", str(ROOT), "--json"],
    )
    assert _validate_skill_output_schemas.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["gap_count"] == 0, payload
