from __future__ import annotations

from pathlib import Path

from tests.quality_gates.repo_shapes import install_committed_repo

from .support import ROOT, run_script


def test_python_filenames_use_snake_case() -> None:
    result = run_script("scripts/check_python_filenames.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_python_filenames_ignore_gitignored_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            ".gitignore": "scripts/GeneratedName.py\n",
            "scripts/kept_name.py": "print('ok')\n",
        },
    )
    (repo / "scripts" / "GeneratedName.py").write_text("print('ignored')\n", encoding="utf-8")

    result = run_script("scripts/check_python_filenames.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
