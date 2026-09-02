from __future__ import annotations

from pathlib import Path

from scripts.setup.setup_host_docs_lib import normalize_host_docs, render_agents_template


def _normalize(repo: Path, *, execute: bool = False, compact: bool = False) -> dict[str, object]:
    return normalize_host_docs(repo, execute=execute, compact=compact)


def test_setup_creates_a_minimal_agents_file_and_symlink(tmp_path: Path) -> None:
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
    assert written_agents == render_agents_template()
    assert len(written_agents.splitlines()) <= 9
    assert "## Skill Routing" not in written_agents
    assert "## Commit Discipline" not in written_agents
    assert "neither is a fallback" in written_agents
    assert "host's fast tier" in written_agents
    assert "keep that choice across compaction" in written_agents
    assert (repo / "CLAUDE.md").is_symlink()
    assert (repo / "CLAUDE.md").readlink() == Path("AGENTS.md")


def test_existing_agents_is_preserved_without_compact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    original = "# Agents\n\nLocal policy.\n"
    (repo / "AGENTS.md").write_text(original, encoding="utf-8")

    completed = _normalize(repo, execute=True)

    assert [item["action"] for item in completed["actions"]] == [
        "keep_agents",
        "create_claude_symlink",
    ]
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == original
    assert (repo / "CLAUDE.md").is_symlink()


def test_compact_is_a_digest_bound_explicit_replacement(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    original = "# Agents\n\n" + ("A long local paragraph.\n" * 20)
    (repo / "AGENTS.md").write_text(original, encoding="utf-8")

    planned = _normalize(repo, compact=True)
    action = planned["actions"][0]
    assert action["action"] == "replace_agents_with_compact_template"
    assert action["before_sha256"] != action["after_sha256"]
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == original

    completed = _normalize(repo, execute=True, compact=True)
    assert completed["status"] == "completed"
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == render_agents_template()


def test_setup_keeps_existing_agents_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "CLAUDE.md").symlink_to("AGENTS.md")

    completed = _normalize(repo, execute=True)

    assert [item["action"] for item in completed["actions"]] == [
        "keep_agents",
        "keep_claude_symlink",
    ]
    assert (repo / "CLAUDE.md").readlink() == Path("AGENTS.md")


def test_setup_blocks_real_claude_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "CLAUDE.md").write_text("# Claude\n\nSpecific policy.\n", encoding="utf-8")

    payload = _normalize(repo, execute=True)

    assert payload["status"] == "blocked"
    assert payload["blocked"][0]["path"] == "CLAUDE.md"
    assert not (repo / "AGENTS.md").exists()
