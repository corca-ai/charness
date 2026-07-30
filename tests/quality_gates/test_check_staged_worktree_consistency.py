"""Tests for the staged-vs-worktree consistency pre-commit gate (audit row A6).

Two fail-open defects this file pins:

1. A path staged and then DELETED on disk used to exit 0. The unstaged-side
   query filtered on ``ACM``, which excludes ``D`` -- and a deleted file is
   exactly the case worktree-walking validators skip entirely, so the staged
   blob would commit having been checked by nothing.
2. ``CHARNESS_ALLOW_PARTIAL_STAGE=0`` -- the spelling an operator uses to turn
   the bypass OFF -- used to turn it ON, because the value was only tested for
   truthiness as a string.

The gate must still pass a clean full stage, a fully staged deletion, and an
unstaged-only deletion.
"""
from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

import pytest

cswc = importlib.import_module("scripts.check_staged_worktree_consistency")


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
    (repo / "f.txt").write_text("v1\n", encoding="utf-8")
    (repo / "g.txt").write_text("g1\n", encoding="utf-8")
    _git(repo, "add", "f.txt", "g.txt")
    _git(repo, "commit", "-qm", "init")
    return repo


def test_staged_then_deleted_on_disk_is_flagged(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()  # index holds v2; worktree holds nothing
    assert cswc.find_stale_staged(repo) == ["f.txt"]
    assert cswc.main(["--repo-root", str(repo)]) == 1


def test_staged_then_edited_is_flagged(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    (repo / "f.txt").write_text("v3\n", encoding="utf-8")
    assert cswc.find_stale_staged(repo) == ["f.txt"]
    assert cswc.main(["--repo-root", str(repo)]) == 1


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "", "  ", "FALSE"])
def test_falsy_env_values_do_not_enable_the_bypass(
    tmp_path: Path, monkeypatch, value: str
) -> None:
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()
    monkeypatch.setenv(cswc.ALLOW_ENV, value)
    assert cswc.allow_partial_stage() is False
    assert cswc.main(["--repo-root", str(repo)]) == 1


@pytest.mark.parametrize("value", ["1", "true", "YES", " on "])
def test_truthy_env_values_enable_the_bypass(
    tmp_path: Path, monkeypatch, value: str
) -> None:
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    (repo / "f.txt").write_text("v3\n", encoding="utf-8")
    monkeypatch.setenv(cswc.ALLOW_ENV, value)
    assert cswc.allow_partial_stage() is True
    assert cswc.main(["--repo-root", str(repo)]) == 0


def test_clean_full_stage_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.txt")  # index == worktree
    assert cswc.find_stale_staged(repo) == []
    assert cswc.main(["--repo-root", str(repo)]) == 0


def test_fully_staged_deletion_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    _git(repo, "rm", "-q", "f.txt")  # deletion staged AND applied on disk
    assert cswc.find_stale_staged(repo) == []
    assert cswc.main(["--repo-root", str(repo)]) == 0


def test_unstaged_only_deletion_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "g.txt").unlink()  # nothing staged for g.txt
    assert cswc.find_stale_staged(repo) == []
    assert cswc.main(["--repo-root", str(repo)]) == 0


def test_staged_then_typechanged_on_disk_is_flagged(tmp_path: Path, monkeypatch) -> None:
    """A status letter allowlist is the wrong shape for an intersection question.

    The first repair widened `--diff-filter` from `ACM` to `ACMRD`, closing the
    deletion case one letter at a time and leaving `T` (typechange) hidden by the
    same mechanism: stage an edit, then replace the file with a symlink, and the
    unstaged side reports `T`, which `ACMRD` drops. The gate then passed a staged
    blob that no worktree-walking validator ever inspected.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    repo = _repo(tmp_path)
    (repo / "f.txt").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", "f.txt")
    (repo / "f.txt").unlink()
    (repo / "f.txt").symlink_to("/etc/hostname")

    assert cswc.find_stale_staged(repo) == ["f.txt"]
    assert cswc.main(["--repo-root", str(repo)]) == 1


def test_a_git_failure_is_unestablished_not_clean(tmp_path: Path, monkeypatch, capsys) -> None:
    """The gate's whole scope comes from two git queries. An empty answer from a
    failed git is indistinguishable from "nothing staged", so it must refuse.

    Pinned at the CLI, not just the library: `find_stale_staged` raising is worth
    nothing if `main` were later "hardened" to swallow it back into exit 0.
    """
    monkeypatch.delenv(cswc.ALLOW_ENV, raising=False)
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()

    with pytest.raises(RuntimeError):
        cswc.find_stale_staged(not_a_repo)

    assert cswc.main(["--repo-root", str(not_a_repo)]) == 1
    err = capsys.readouterr().err
    assert "UNESTABLISHED" in err
    assert "safe.directory" in err  # the remedy, not a bare traceback
