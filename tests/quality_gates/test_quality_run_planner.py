from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/plan_quality_run.py"


def _run_plan(repo: Path) -> dict[str, object]:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_quality_run_plan_excludes_skill_refs_when_repo_has_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")

    plan = _run_plan(repo)

    assert plan["next_action"] == "read_primer_refs"
    assert plan["gate_plan"] == "report_first"
    assert plan["skills_in_scope"] is False
    refs = plan["required_primer_refs"]
    assert "references/quality-lenses.md" in refs
    assert "references/skill-quality.md" not in refs
    assert "references/skill-ergonomics.md" not in refs


def test_quality_run_plan_includes_skill_refs_for_skill_authoring_repo(tmp_path: Path) -> None:
    repo = tmp_path / "skill_repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "Use this when a demo skill is needed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    plan = _run_plan(repo)

    assert plan["skills_in_scope"] is True
    assert plan["sample_skill_paths"] == ["skills/public/demo/SKILL.md"]
    assert "references/skill-quality.md" in plan["required_primer_refs"]
    assert "references/skill-ergonomics.md" in plan["required_primer_refs"]
    assert any("before broad gates" in barrier for barrier in plan["phase_barriers"])
    assert any("before fixing" in barrier for barrier in plan["phase_barriers"])


def test_quality_run_plan_detects_plugin_only_skill_authoring_repo(tmp_path: Path) -> None:
    repo = tmp_path / "plugin_repo"
    skill_dir = repo / "plugins" / "acme" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    plan = _run_plan(repo)

    assert plan["skills_in_scope"] is True
    assert plan["sample_skill_paths"] == ["plugins/acme/skills/demo/SKILL.md"]
    assert "references/skill-quality.md" in plan["required_primer_refs"]
    assert "references/skill-ergonomics.md" in plan["required_primer_refs"]


def test_quality_run_plan_lists_all_on_demand_reference_triggers(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()

    plan = _run_plan(repo)

    triggers = plan["on_demand_trigger_map"]
    assert len(triggers) == 27
    assert "references/adapter-contract.md" in triggers
    assert "references/dup-ratchet.md" in triggers
    assert "references/unit-test-quality.md" in triggers
