from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_init_repo_seed_retro_memory_writes_adapter_and_digest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script("skills/public/init-repo/scripts/seed_retro_memory.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["created"] == {"adapter": True, "summary": True, "gitignore": True}

    adapter_text = (repo / ".agents" / "retro-adapter.yaml").read_text(encoding="utf-8")
    summary_text = (repo / "charness-artifacts" / "retro" / "recent-lessons.md").read_text(encoding="utf-8")
    gitignore_text = (repo / ".gitignore").read_text(encoding="utf-8")
    assert "summary_path: charness-artifacts/retro/recent-lessons.md" in adapter_text
    assert "auto_session_trigger_surfaces: []" in adapter_text
    assert "auto_session_trigger_path_globs: []" in adapter_text
    assert "repo: repo" in adapter_text
    assert "No durable retro summary yet." in summary_text
    assert ".charness/retro/" in gitignore_text


def test_init_repo_seed_retro_memory_preserves_existing_gitignore(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text("node_modules/\n.charness/retro/\n", encoding="utf-8")

    result = run_script("skills/public/init-repo/scripts/seed_retro_memory.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["created"]["gitignore"] is False
    assert (repo / ".gitignore").read_text(encoding="utf-8") == "node_modules/\n.charness/retro/\n"


def test_init_repo_skill_mentions_retro_memory_scaffold() -> None:
    skill_text = (ROOT / "skills" / "public" / "init-repo" / "SKILL.md").read_text(encoding="utf-8")
    default_surfaces_text = (
        ROOT / "skills" / "public" / "init-repo" / "references" / "default-surfaces.md"
    ).read_text(encoding="utf-8")
    reference_text = (
        ROOT / "skills" / "public" / "init-repo" / "references" / "retro-memory-seam.md"
    ).read_text(encoding="utf-8")

    assert "retro-memory-seam.md" in skill_text
    assert "seed_retro_memory.py" in skill_text
    assert "recent-lessons.md" in skill_text
    assert "recent-lessons.md" in default_surfaces_text
    assert ".agents/retro-adapter.yaml" in reference_text
    assert "recent-lessons.md" in reference_text
