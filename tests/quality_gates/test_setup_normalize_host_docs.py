from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def _normalize(repo: Path, *args: str) -> dict[str, object]:
    result = run_script(
        "skills/public/setup/scripts/normalize_host_docs.py",
        "--repo-root",
        str(repo),
        *args,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


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

    completed = _normalize(repo, "--execute")

    assert completed["status"] == "completed"
    assert (repo / "AGENTS.md").read_text(encoding="utf-8").startswith("# Agents\n")
    assert "## Skill Routing" in (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "## Subagent Delegation" in (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert (repo / "CLAUDE.md").is_symlink()
    assert (repo / "CLAUDE.md").readlink() == Path("AGENTS.md")


def test_setup_normalize_host_docs_existing_agents_creates_symlink_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n\nExisting policy.\n", encoding="utf-8")

    completed = _normalize(repo, "--execute")

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

    completed = _normalize(repo, "--execute")

    assert [item["action"] for item in completed["actions"]] == [
        "keep_agents",
        "keep_claude_symlink",
    ]
    assert (repo / "CLAUDE.md").readlink() == Path("AGENTS.md")


def test_setup_normalize_host_docs_blocks_real_claude_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "CLAUDE.md").write_text("# Claude\n\nSpecific policy.\n", encoding="utf-8")

    result = run_script("skills/public/setup/scripts/normalize_host_docs.py", "--repo-root", str(repo), "--execute")
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["blocked"][0]["path"] == "CLAUDE.md"
    assert not (repo / "AGENTS.md").exists()
