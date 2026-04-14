from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_quality_skill_carries_explicit_skill_ergonomics_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    ergonomics = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-ergonomics.md"
    ).read_text(encoding="utf-8")
    skill_quality = (
        ROOT / "skills" / "public" / "quality" / "references" / "skill-quality.md"
    ).read_text(encoding="utf-8")

    assert "inventory_skill_ergonomics.py" in skill_text
    assert "skill ergonomics" in skill_text
    assert "mode/option pressure" in skill_text
    assert "taste policing" in skill_text
    assert "less is more" in ergonomics
    assert "progressive disclosure" in ergonomics
    assert "model is smart" in ergonomics
    assert "Treat these as prompts, not automatic failures." in ergonomics
    assert "trigger overlap or undertrigger risk" in skill_quality
    assert "repeated prose ritual" in skill_quality


def test_quality_skill_carries_cli_ergonomics_smells_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    cli_smells = (
        ROOT / "skills" / "public" / "quality" / "references" / "cli-ergonomics-smells.md"
    ).read_text(encoding="utf-8")

    assert "inventory_cli_ergonomics.py" in skill_text
    assert "flat help-list" in skill_text
    assert "multiple archetype schema namespaces" in skill_text
    assert "Flat `--help` Lists" in cli_smells
    assert "Cross-Archetype Schema Leakage" in cli_smells
    assert "command-archetypes.json" in cli_smells
