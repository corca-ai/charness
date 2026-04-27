from __future__ import annotations

from pathlib import Path

from .support import run_script


def test_migrate_backtick_file_refs_skips_portable_skill_bodies(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    skill_dir = repo / "skills" / "public" / "demo"
    docs_dir.mkdir(parents=True)
    skill_dir.mkdir(parents=True)
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (repo / "README.md").write_text("See `docs/guide.md`.\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text("See `docs/guide.md`.\n", encoding="utf-8")

    result = run_script("scripts/migrate_backtick_file_refs.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "[`docs/guide.md`](./docs/guide.md)" in (repo / "README.md").read_text(encoding="utf-8")
    assert "`docs/guide.md`" in (skill_dir / "SKILL.md").read_text(encoding="utf-8")
