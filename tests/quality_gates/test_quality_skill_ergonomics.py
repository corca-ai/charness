from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_skill_ergonomics_reports_advisory_flags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
        "",
        "Use this when the repo needs a demo skill.",
        "",
        "Mode choice matters in this mode-heavy workflow.",
        "Another mode note keeps the mode pressure explicit.",
        "This option should probably be inference instead of an option.",
        "A second option mention keeps option pressure visible.",
        "",
        "## Bootstrap",
        "",
        "```bash",
        "echo first",
        "```",
        "",
        "```bash",
        "echo second",
        "```",
        "",
        "```bash",
        "echo third",
        "```",
        "",
    ]
    lines.extend(f"- filler line {index}" for index in range(90))
    (skill_dir / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_script(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(repo),
        "--max-core-lines",
        "20",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    skill = payload["skills"][0]
    assert skill["skill_id"] == "demo"
    assert skill["skill_type"] == "public"
    assert skill["skill_path"] == "skills/public/demo/SKILL.md"
    assert set(skill["heuristics"]) == {
        "long_core",
        "progressive_disclosure_risk",
        "mode_pressure_terms_present",
        "option_pressure_terms_present",
        "code_fence_without_helper_script",
    }
    assert skill["bootstrap_fence_count"] == 3
    assert skill["review_prompts"]
