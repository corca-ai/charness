"""Tests for the #258 staged-reversion pre-commit gate.

The gate (`scripts/check_staged_reversion.py`) flags only the unambiguous
phantom: ``index != HEAD`` while ``worktree == HEAD`` (a staged blob present in
neither the commit nor the working copy). It must NOT flag a legitimate full
stage, a mode-only stage, a new-file add, or a genuine deletion.
"""
from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

from .support import run_script

csr = importlib.import_module("scripts.check_staged_reversion")


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    return repo


def _commit(repo: Path, name: str, content: str) -> None:
    (repo / name).write_text(content, encoding="utf-8")
    _git(repo, "add", name)
    _git(repo, "commit", "-qm", f"add {name}")


def _stage_phantom(repo: Path) -> None:
    """HEAD == v2, index == v1 (staged reversion), worktree == v2 == HEAD."""
    _commit(repo, "f.py", "v2\n")
    (repo / "f.py").write_text("v1\n", encoding="utf-8")
    _git(repo, "add", "f.py")
    (repo / "f.py").write_text("v2\n", encoding="utf-8")


def test_phantom_modified_reversion_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _stage_phantom(repo)
    findings = csr.find_staged_reversions(str(repo))
    assert [f.case for f in findings] == ["modified-reversion-phantom"]
    assert findings[0].path == "f.py"
    assert "git add" in findings[0].recovery


def test_legit_full_stage_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "v1\n")
    (repo / "f.py").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.py")  # index == worktree == v2 != HEAD
    assert csr.find_staged_reversions(str(repo)) == []


def test_mode_only_stage_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "v1\n")
    (repo / "f.py").chmod(0o755)
    _git(repo, "add", "f.py")  # same blob, only the mode changed
    assert csr.find_staged_reversions(str(repo)) == []


def test_new_file_add_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "a.py", "x\n")
    (repo / "b.py").write_text("new\n", encoding="utf-8")
    _git(repo, "add", "b.py")
    assert csr.find_staged_reversions(str(repo)) == []


def test_genuine_deletion_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "v1\n")
    _git(repo, "rm", "-q", "f.py")  # index AND worktree both gone
    assert csr.find_staged_reversions(str(repo)) == []


def test_staged_deletion_phantom_is_flagged(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "v1\n")
    _git(repo, "rm", "--cached", "-q", "f.py")  # index deletes; worktree keeps v1 == HEAD
    findings = csr.find_staged_reversions(str(repo))
    assert [f.case for f in findings] == ["staged-deletion-phantom"]


def test_clean_tree_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "v1\n")
    assert csr.find_staged_reversions(str(repo)) == []


def test_cli_blocks_phantom(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _stage_phantom(repo)
    result = run_script("scripts/check_staged_reversion.py", "--repo-root", str(repo))
    assert result.returncode == 1, result.stdout
    assert "BLOCKED" in result.stdout
    assert "f.py" in result.stdout


def test_cli_flag_bypass_allows(tmp_path: Path, capsys) -> None:
    repo = _repo(tmp_path)
    _stage_phantom(repo)
    assert csr.main(["--repo-root", str(repo), "--allow-staged-reversion"]) == 0
    assert "allowed" in capsys.readouterr().out


def test_cli_env_bypass_allows(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = _repo(tmp_path)
    _stage_phantom(repo)
    monkeypatch.setenv("CHARNESS_ALLOW_STAGED_REVERSION", "1")
    assert csr.main(["--repo-root", str(repo)]) == 0
    assert "allowed" in capsys.readouterr().out


def test_clean_tree_cli_exit_zero(tmp_path: Path, capsys) -> None:
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "v1\n")
    assert csr.main(["--repo-root", str(repo)]) == 0
    assert "clean" in capsys.readouterr().out
