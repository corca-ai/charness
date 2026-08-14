from __future__ import annotations

import sys
from types import SimpleNamespace

import yaml

from tests.script_loader import load_script_module

from .support import ROOT

AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

RETRO_RESOLVE_ADAPTER = load_script_module(
    "tests.quality_gates.retro_resolve_adapter",
    ROOT / "skills/public/retro/scripts/resolve_adapter.py",
)


def run_retro_resolve_adapter(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["resolve_adapter.py", *args])
    code = RETRO_RESOLVE_ADAPTER.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_retro_adapter_exposes_recent_lessons_summary_path(monkeypatch, capsys) -> None:
    result = run_retro_resolve_adapter(monkeypatch, capsys, "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["data"]["summary_path"] == "charness-artifacts/retro/recent-lessons.md"


def test_retro_memory_surfaces_reference_recent_lessons_digest() -> None:
    handoff_text = (ROOT / "docs" / "handoff.md").read_text(encoding="utf-8")
    skill_text = (ROOT / "skills" / "public" / "retro" / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    lessons_text = (ROOT / "charness-artifacts" / "retro" / "recent-lessons.md").read_text(encoding="utf-8")

    assert "charness-artifacts/retro/recent-lessons.md" in AGENTS
    assert "recent-lessons.md" in handoff_text
    assert "summary_path" in skill_text
    assert "summary_path" in contract_text
    assert "Repeat Traps" in lessons_text
    assert "Next-Time Checklist" in lessons_text
    assert "## Sources" in lessons_text
    assert "charness-artifacts/retro/" in lessons_text


def test_agents_keeps_dogfood_detail_in_development_doc() -> None:
    development_text = (ROOT / "docs" / "development.md").read_text(encoding="utf-8")

    assert "docs/development.md" in AGENTS
    assert "--skip-cli-install" not in AGENTS
    assert "~/.agents/src/charness/charness update" not in AGENTS
    assert "--skip-cli-install" in development_text
    assert "~/.agents/src/charness/charness update" in development_text


def test_agents_carries_bounded_subagent_delegation_rule() -> None:
    agents_text = AGENTS.lower()

    assert "subagent delegation" in agents_text
    assert "explicit user delegation request" in agents_text
    assert "bounded reviewer" in agents_text
