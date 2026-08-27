from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import import_repo_module
from scripts.setup_skill_routing_lib import (
    skill_routing_declares_charness_management,
    skill_routing_semantically_complete,
)

from .support import ROOT

_render_skill_routing = import_repo_module(
    ROOT / "skills/public/setup/scripts/render_skill_routing.py",
    "skills.public.setup.scripts.render_skill_routing",
)


def test_renderer_emits_the_parent_cursor_progressive_disclosure_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    payload = _render_skill_routing.build_payload(repo)

    assert payload["recommended_action"] == "create_agents_with_skill_routing"
    assert payload["skill_routing_mode"] == "compact"
    assert payload["listed_skill_ids"] == []
    markdown = payload["markdown"]
    assert "Start an active Goal Run only from the exact `/goal #<parent>` objective" in markdown
    assert "parent cursor selects the next child" in markdown
    assert "AGENTS.md -> docs/index.md" in markdown
    assert "docs/index.md" in markdown


def test_the_shipped_routing_block_is_accepted_by_both_readers() -> None:
    markdown, _ = _render_skill_routing._render_skill_routing()
    body = markdown.partition("## Skill Routing")[2]

    assert skill_routing_declares_charness_management(body) is True
    assert skill_routing_semantically_complete(body) is True


def test_a_repo_with_a_complete_custom_block_is_left_as_is(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Agents",
                "",
                "## Skill Routing",
                "",
                "Start an active Goal Run from the exact `/goal #<parent>` objective; the parent cursor selects the next child.",
                "Choose the matching workflow directly from installed skill metadata and model judgment.",
                "Use the read-only `charness catalog list --repo-root .` inventory when hidden availability is unclear.",
                "If the command returns a nonzero status, report the command failure.",
                "External URLs and source links route through `gather` before deciding.",
                "Validation closeout goes through `quality`.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_matches_compact_block"] is False
    assert payload["skill_routing_semantically_complete"] is True
    assert payload["recommended_action"] == "leave_as_is"


def test_a_drifted_custom_block_is_reported_for_review(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(
        "# Agents\n\n## Skill Routing\n\nUse local judgment.\n",
        encoding="utf-8",
    )

    payload = _render_skill_routing.build_payload(repo)

    assert payload["skill_routing_semantically_complete"] is False
    assert payload["recommended_action"] == "review_existing_skill_routing"
    assert payload["missing_expected_snippets"]
