from __future__ import annotations

import json
from pathlib import Path

from .support import run_script

SCRIPT = "skills/public/quality/scripts/validate_skill_ergonomics.py"


def _seed_repo(tmp_path: Path, *, rules: list[str]) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "skills" / "public" / "demo" / "references").mkdir(parents=True)
    (repo / "skills" / "public" / "steady" / "references").mkdir(parents=True)
    adapter_lines = [
        "version: 1",
        "repo: testrepo",
        "output_dir: skill-outputs/quality",
    ]
    if rules:
        adapter_lines.append("skill_ergonomics_gate_rules:")
        for rule in rules:
            adapter_lines.append(f"  - {rule}")
    else:
        adapter_lines.append("skill_ergonomics_gate_rules: []")
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / "skills" / "public" / "steady" / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "Mode choice matters in this mode-heavy workflow.",
                "Another mode note keeps the mode pressure explicit.",
                "This option should probably be inference instead of an option.",
                "A second option mention keeps option pressure visible.",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "skills" / "public" / "steady" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: steady",
                'description: "Steady skill."',
                "---",
                "",
                "# Steady",
                "",
                "Use this when the repo needs a stable skill.",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def test_skill_ergonomics_gate_no_rules_passes(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=[])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["rules"] == []
    assert payload["violations"] == []


def test_skill_ergonomics_gate_fails_when_opted_in_rule_matches(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, rules=["mode_option_pressure_terms"])
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["rules"] == ["mode_option_pressure_terms"]
    assert payload["violations"][0]["rule"] == "mode_option_pressure_terms"
    assert payload["violations"][0]["skill_id"] == "demo"
    plain = run_script(SCRIPT, "--repo-root", str(repo))
    assert plain.returncode == 1
    assert "mode_option_pressure_terms" in plain.stdout
    assert "skills/public/demo/SKILL.md" in plain.stdout


def test_skill_ergonomics_gate_ignores_mode_option_terms_inside_fences(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: skill-outputs/quality",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
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
                "## Bootstrap",
                "",
                "```bash",
                "echo mode option mode option",
                "```",
                "",
                "## References",
                "",
                "- `references/note.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == []


def test_skill_ergonomics_gate_fails_when_opted_in_progressive_disclosure_risk_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: skill-outputs/quality",
                "skill_ergonomics_gate_rules:",
                "  - progressive_disclosure_risk",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    filler = [f"filler line {index}" for index in range(90)]
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
                *filler,
                "",
                "## References",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["rules"] == ["progressive_disclosure_risk"]
    assert payload["violations"][0]["rule"] == "progressive_disclosure_risk"
