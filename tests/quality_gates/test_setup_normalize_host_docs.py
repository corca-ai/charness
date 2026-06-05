from __future__ import annotations

from pathlib import Path

from scripts.setup_host_docs_lib import normalize_host_docs


def _routing_payload(_: Path) -> dict[str, object]:
    return {"markdown": "## Skill Routing\n\nUse `find-skills` first.\n"}


def _normalize(repo: Path, *, execute: bool = False) -> dict[str, object]:
    return normalize_host_docs(repo, skill_routing_payload=_routing_payload, execute=execute)


def test_setup_normalize_host_docs_creates_agents_and_claude_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    planned = _normalize(repo)
    assert planned["status"] == "planned"
    assert [item["action"] for item in planned["actions"]] == [
        "write_agents",
        "create_claude_symlink",
    ]
    assert not (repo / "AGENTS.md").exists()

    completed = _normalize(repo, execute=True)

    assert completed["status"] == "completed"
    written_agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert written_agents.startswith("# Agents\n")
    assert "## Skill Routing" in written_agents
    assert "## Subagent Delegation" in written_agents
    # #317 seed: the greenfield write path emits the compact commit-discipline
    # block so a long autonomous run does not leave work uncommitted.
    assert "## Commit Discipline" in written_agents
    assert "Commit meaningful work slices as they finish" in written_agents
    assert (repo / "CLAUDE.md").is_symlink()
    assert (repo / "CLAUDE.md").readlink() == Path("AGENTS.md")


def test_setup_normalize_host_docs_existing_agents_creates_symlink_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    completed = _normalize(repo, execute=True)

    assert [item["action"] for item in completed["actions"]] == [
        "keep_agents",
        "create_claude_symlink",
    ]
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "# Agents\n\nExisting policy.\n"
    assert (repo / "CLAUDE.md").is_symlink()


def test_setup_normalize_host_docs_keeps_existing_agents_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")
    (repo / "CLAUDE.md").symlink_to("AGENTS.md")

    completed = _normalize(repo, execute=True)

    assert [item["action"] for item in completed["actions"]] == [
        "keep_agents",
        "keep_claude_symlink",
    ]
    assert (repo / "CLAUDE.md").readlink() == Path("AGENTS.md")


def test_setup_normalize_host_docs_blocks_real_claude_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "CLAUDE.md").write_text("# Claude\n\nSpecific policy.\n", encoding="utf-8")

    payload = _normalize(repo, execute=True)

    assert payload["status"] == "blocked"
    assert payload["blocked"][0]["path"] == "CLAUDE.md"
    assert not (repo / "AGENTS.md").exists()
