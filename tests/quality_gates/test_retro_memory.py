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
    skill_text = (ROOT / "skills" / "public" / "retro" / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (
        ROOT / "skills" / "public" / "retro" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    lessons_text = (ROOT / "charness-artifacts" / "retro" / "recent-lessons.md").read_text(encoding="utf-8")

    assert "charness-artifacts/" in AGENTS
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
    assert "charness update --repo-root . --no-pull --skip-cli-install" in development_text


def test_agents_carries_only_the_compact_parallel_routing_cue() -> None:
    """The cue and the route stay in the router; the mechanics stay with the owner.

    This used to pin the lane-availability rule's own wording inside `AGENTS.md`,
    which made the router the second place that rule lived -- the exact "second
    operating manual" its own second sentence forbids. The escape being guarded is
    the rule going MISSING, not the rule being in `AGENTS.md`, so each phrase is
    asserted against `docs/parallel-execution.md` (which declares itself the owner)
    and refused in the router.
    """
    # Both pages hard-wrap prose, so a phrase straddles a newline in whichever
    # page happens to break there. Matching the raw text made the assertion a
    # test of the wrap column rather than of where the rule lives.
    def _flat(text: str) -> str:
        return " ".join(text.lower().split())

    agents_text = _flat(AGENTS)
    owner_text = _flat((ROOT / "docs" / "parallel-execution.md").read_text(encoding="utf-8"))

    assert "independent investigation" in agents_text
    assert "final verification" in agents_text
    assert "docs/parallel-execution.md" in agents_text
    assert "live tool inventory" in agents_text

    for mechanic in ("explicit inventory absence", "invocation rejection", "host error"):
        assert mechanic in owner_text
        assert mechanic not in agents_text

    assert "## subagent delegation" not in agents_text
