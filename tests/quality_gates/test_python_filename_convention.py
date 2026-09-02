from __future__ import annotations

from pathlib import Path

from tests.quality_gates.repo_shapes import install_committed_repo

from .support import ROOT, run_script


def test_python_filenames_use_snake_case() -> None:
    result = run_script("scripts/gates/check_python_filenames.py", "--repo-root", str(ROOT))
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

    result = run_script("scripts/gates/check_python_filenames.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_python_filename_gate_rejects_a_colliding_script_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            "scripts/packaging/__init__.py": "VALUE = 1\n",
        },
    )

    result = run_script("scripts/gates/check_python_filenames.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "scripts/packaging" in result.stderr
    assert "importable module 'packaging'" in result.stderr
