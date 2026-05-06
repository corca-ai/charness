from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_success_criteria_review_is_shared_and_wired_to_shaping_skills() -> None:
    shared = (
        ROOT / "skills" / "shared" / "references" / "success-criteria-review.md"
    ).read_text(encoding="utf-8")
    ideation = (ROOT / "skills" / "public" / "ideation" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    spec = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(encoding="utf-8")
    narrative = (ROOT / "skills" / "public" / "narrative" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    create_skill = (
        ROOT / "skills" / "public" / "create-skill" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "preparade-style thinking" in shared
    assert "criteria, checks, or" in shared and "tripwires" in shared
    assert "bounded fresh-eye subagent" in shared
    assert "../../shared/references/success-criteria-review.md" in ideation
    assert "../../shared/references/success-criteria-review.md" in spec
    assert "../../shared/references/success-criteria-review.md" in narrative
    assert "../../shared/references/success-criteria-review.md" in create_skill
    assert "first successful trigger" in create_skill
    assert "intended reader action" in narrative
