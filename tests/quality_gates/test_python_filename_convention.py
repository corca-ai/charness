from __future__ import annotations

from pathlib import Path

from .support import ROOT, init_git_repo, run_script


def test_python_filenames_use_snake_case() -> None:
    result = run_script("scripts/check_python_filenames.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_python_filenames_ignore_gitignored_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".gitignore").write_text("scripts/GeneratedName.py\n", encoding="utf-8")
    (repo / "scripts" / "kept_name.py").write_text("print('ok')\n", encoding="utf-8")
    (repo / "scripts" / "GeneratedName.py").write_text("print('ignored')\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "scripts/kept_name.py")

    result = run_script("scripts/check_python_filenames.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
