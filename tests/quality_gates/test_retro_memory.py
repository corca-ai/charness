from __future__ import annotations

import json

from .support import ROOT, run_script


def test_retro_adapter_exposes_recent_lessons_summary_path() -> None:
    result = run_script("skills/public/retro/scripts/resolve_adapter.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["data"]["summary_path"] == "charness-artifacts/retro/recent-lessons.md"


def test_retro_memory_surfaces_reference_recent_lessons_digest() -> None:
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    handoff_text = (ROOT / "docs" / "handoff.md").read_text(encoding="utf-8")
    skill_text = (ROOT / "skills" / "public" / "retro" / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    lessons_text = (ROOT / "charness-artifacts" / "retro" / "recent-lessons.md").read_text(encoding="utf-8")

    assert "charness-artifacts/retro/recent-lessons.md" in agents_text
    assert "recent-lessons.md" in handoff_text
    assert "summary_path" in skill_text
    assert "summary_path" in contract_text
    assert "Repeat Traps" in lessons_text
    assert "Next-Time Checklist" in lessons_text
    assert "## Sources" in lessons_text
    assert "charness-artifacts/retro/" in lessons_text


def test_agents_keeps_dogfood_detail_in_development_doc() -> None:
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    development_text = (ROOT / "docs" / "development.md").read_text(encoding="utf-8")

    assert "docs/development.md" in agents_text
    assert "--skip-cli-install" not in agents_text
    assert "~/.agents/src/charness/charness update" not in agents_text
    assert "--skip-cli-install" in development_text
    assert "~/.agents/src/charness/charness update" in development_text


def test_agents_carries_bounded_subagent_delegation_rule() -> None:
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()

    assert "already delegated" in agents_text
    assert "second user message asking for delegation" in agents_text
    assert "same-agent pass" in agents_text
