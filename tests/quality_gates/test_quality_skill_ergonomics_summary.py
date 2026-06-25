from __future__ import annotations

import json
from pathlib import Path

from .skill_ergonomics_support import run_inventory_skill_ergonomics as _run


def test_inventory_skill_ergonomics_summary_keeps_review_payload_compact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
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
                "Use this when the repo needs a demo skill.",
                "Mode choice matters in this mode-heavy workflow.",
                "Another mode note keeps the mode pressure explicit.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run("--repo-root", str(repo), "--summary")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["checked_skill_count"] == 1
    assert payload["heuristic_finding_count"] == 1
    assert payload["prose_review_status"] == "required"
    assert payload["advisories"][0]["advisory_id"] == "skill_ergonomics_prose_review_required"
    assert payload["skills_with_heuristics"] == [
        {
            "skill_id": "demo",
            "skill_type": "public",
            "skill_path": "skills/public/demo/SKILL.md",
            "core_nonempty_lines": 4,
            "reference_file_count": 0,
            "script_file_count": 0,
            "heuristics": ["mode_pressure_terms_present"],
            "subcheck_counts": {
                "core_overfill": 0,
                "mode_option_pressure": 1,
                "prose_ritual": 0,
                "path_ambiguity": 0,
                "package_issue_anchor": 0,
                "package_dated_incident": 0,
                "host_surface_reference": 0,
                "reference_discoverability": 0,
            },
        }
    ]
    assert "skills" not in payload
    assert "review_prompts" not in result.stdout
