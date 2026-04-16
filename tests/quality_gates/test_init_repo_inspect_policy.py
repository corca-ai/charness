from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def _run_inspect(repo: Path) -> dict[str, object]:
    result = run_script("skills/public/init-repo/scripts/inspect_repo.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_init_repo_inspect_repo_flags_targeted_missing_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "PARTIAL"
    assert payload["partial_kind"] == "targeted_missing_surface"
    assert payload["missing_surfaces"] == ["operator_acceptance"]


def test_init_repo_inspect_repo_matches_default_surfaces_case_insensitively(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / "install.md").write_text("# Install\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["path"] == "docs/ROADMAP.md"
    assert payload["surfaces"]["install"]["path"] == "install.md"


def test_init_repo_inspect_repo_honors_adapter_surface_overrides(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "master-plan.md").write_text("# Plan\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: repo", "surfaces:", "  roadmap: docs/master-plan.md", "  uninstall: null", ""]),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["path"] == "docs/master-plan.md"
    assert payload["surfaces"]["roadmap"]["source"] == "adapter"
    assert payload["surfaces"]["uninstall"]["kind"] == "acknowledged_missing"


def test_init_repo_inspect_repo_excludes_acknowledged_missing_core_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")
    (repo / ".agents" / "init-repo-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: repo", "surfaces:", "  roadmap: null", ""]),
        encoding="utf-8",
    )

    payload = _run_inspect(repo)

    assert payload["repo_mode"] == "NORMALIZE"
    assert payload["missing_surfaces"] == []
    assert payload["surfaces"]["roadmap"]["kind"] == "acknowledged_missing"


def test_init_repo_render_skill_routing_names_concrete_triggers(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_script("skills/public/init-repo/scripts/render_skill_routing.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["recommended_action"] == "create_agents_with_skill_routing"
    assert "gather" in payload["public_skills"]
    assert "find-skills" in payload["public_skills"]
    assert "Slack thread, Notion page, Google Docs, GitHub content, arbitrary URL" in payload["markdown"]
    assert "named support/helper, or hidden capability lookup" in payload["markdown"]


def test_init_repo_render_skill_routing_suggests_add_block_for_mature_agents(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    result = run_script("skills/public/init-repo/scripts/render_skill_routing.py", "--repo-root", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["agents_has_skill_routing"] is False
    assert payload["recommended_action"] == "add_skill_routing_block"


def _seed_source_guard_repo(repo: Path, adapter_lines: list[str]) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n\nA sentence that is guarded.\n", encoding="utf-8")
    (repo / "docs" / "spec.md").write_text(
        "\n".join(
            [
                "# Spec",
                "",
                "| path | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | A sentence that is guarded. |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / ".agents" / "init-repo-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")


def test_init_repo_inspect_warns_for_column_wrap_fixed_source_guards(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_source_guard_repo(repo, ["version: 1", "repo: repo", "prose_wrap_policy: column"])

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["status"] == "requires_override"
    assert payload["prose_wrap"]["source_guard_count"] == 1
    assert payload["prose_wrap"]["warnings"][0]["type"] == "column_wrap_fixed_guard_requires_override"


def test_init_repo_inspect_accepts_column_wrap_when_matcher_normalizes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_source_guard_repo(
        repo,
        [
            "version: 1",
            "repo: repo",
            "prose_wrap_policy: column",
            "source_guard_matcher:",
            "  normalize_whitespace: true",
        ],
    )

    payload = _run_inspect(repo)

    assert payload["prose_wrap"]["status"] == "ok"
    assert payload["prose_wrap"]["matcher_normalizes_whitespace"] is True


def test_init_repo_inspect_reports_malformed_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "init-repo-adapter.yaml").write_text("- not-a-dict\n", encoding="utf-8")

    payload = _run_inspect(repo)

    assert payload["adapter"]["found"] is True
    assert payload["adapter"]["valid"] is False
    assert payload["adapter"]["warnings"][0]["type"] == "adapter_root_not_mapping"
