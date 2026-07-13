from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

from .support import ROOT

_render_skill_routing = import_repo_module(
    ROOT / "skills/public/setup/scripts/render_skill_routing.py",
    "skills.public.setup.scripts.render_skill_routing",
)


def run_render_skill_routing(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["render_skill_routing.py", *args])
    returncode = _render_skill_routing.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_setup_render_skill_routing_defaults_to_compact_mode(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["recommended_action"] == "create_agents_with_skill_routing"
    assert payload["skill_routing_mode"] == "compact"
    assert payload["skill_routing_mode_source"] == "default"
    assert payload["listed_skill_ids"] == []
    # 2026-07-04 revision: session start routes directly instead of always
    # The hook/context path no longer invokes a public semantic router.
    # discovery or a missing/stale/unclear route.
    assert "At session start, a pickup follows docs/handoff.md" in payload["markdown"]
    assert "charness catalog list --repo-root <repo> --json" in payload["markdown"]
    assert "installed skill metadata and model judgment" in payload["markdown"]
    assert "SessionStart hook" in payload["markdown"]
    assert "release-note style summary or chat-ready human update" not in payload["markdown"]


def test_setup_render_skill_routing_suggests_add_block_for_mature_agents(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["agents_has_skill_routing"] is False
    assert payload["recommended_action"] == "add_skill_routing_block"


def test_setup_render_skill_routing_reviews_drifted_existing_block(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Agents\n\n## Skill Routing\n\nFor task-oriented sessions, use local judgment.\n",
        encoding="utf-8",
    )

    result = run_render_skill_routing(monkeypatch, capsys, "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["agents_has_skill_routing"] is True
    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["recommended_action"] == "review_existing_skill_routing"
    assert any("charness catalog list --repo-root <repo> --json" in item for item in payload["missing_expected_snippets"])


def test_setup_render_skill_routing_leaves_semantically_complete_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "A pickup follows docs/handoff.md `## Workflow Trigger`; ordinary requests use installed skill metadata and model judgment.",
                "Use the read-only `charness catalog list --repo-root . --json` inventory when hidden availability is unclear.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout and operator reading tests route through `quality`.",
                "The SessionStart hook may inject this context; it remains context-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"
    assert payload["missing_expected_snippets"] == []
