from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_setup_render_skill_routing_defaults_to_compact_mode(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_script("skills/public/setup/scripts/render_skill_routing.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["recommended_action"] == "create_agents_with_skill_routing"
    assert payload["skill_routing_mode"] == "compact"
    assert payload["skill_routing_mode_source"] == "default"
    assert "find-skills" in payload["public_skills"]
    assert payload["listed_skill_ids"] == ["find-skills"]
    assert "At session startup in this repo, call the shared/public charness skill `find-skills` once before broader exploration" in payload["markdown"]
    assert "default map of installed public skills, support skills, synced support surfaces, and integrations" in payload["markdown"]
    assert 'find-skills --recommend-for-task "<task>"' in payload["markdown"]
    assert "before ad hoc shell or tool use" in payload["markdown"]
    assert "choose the durable work skill that best matches the request" in payload["markdown"]
    assert "External URLs or source links that should become working context" in payload["markdown"]
    assert "route through `gather` before summarizing, implementing, or deciding" in payload["markdown"]
    assert "release-note style summary or chat-ready human update" not in payload["markdown"]


def test_setup_render_skill_routing_suggests_add_block_for_mature_agents(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    result = run_script("skills/public/setup/scripts/render_skill_routing.py", "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["agents_has_skill_routing"] is False
    assert payload["recommended_action"] == "add_skill_routing_block"


def test_setup_render_skill_routing_reviews_drifted_existing_block(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Agents\n\n## Skill Routing\n\nFor task-oriented sessions, use local judgment.\n",
        encoding="utf-8",
    )

    result = run_script("skills/public/setup/scripts/render_skill_routing.py", "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["agents_has_skill_routing"] is True
    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["recommended_action"] == "review_existing_skill_routing"
    assert (
        "At session startup in this repo, call the shared/public charness skill `find-skills` once before broader exploration."
        in payload["missing_expected_snippets"]
    )
