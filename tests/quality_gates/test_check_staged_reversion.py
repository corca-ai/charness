"""Tests for the #258 staged-reversion pre-commit gate.

The gate (`scripts/check_staged_reversion.py`) flags only the unambiguous
phantom: ``index != HEAD`` while ``worktree == HEAD`` (a staged blob present in
neither the commit nor the working copy). It must NOT flag a legitimate full
stage, a mode-only stage, a new-file add, or a genuine deletion.
"""
from __future__ import annotations

import importlib
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from .git_fixture_support import init_git_repo
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
    init_git_repo(repo)
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
    # ...and the two cases must not collapse to one message: `git add` appears in
    # BOTH, so asserting only that would stay green if `_recovery` were flattened.
    # The deletion branch exists to name the `git rm --cached` reading instead of
    # telling the operator to undo the untrack they meant to make.
    assert "--cached" not in findings[0].recovery


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
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "blocked"
    assert [finding["path"] for finding in payload["findings"]] == ["f.py"]
    # The blocking REASON travelled only in the deleted human banner; a payload that
    # blocks without saying why is a gate nobody can act on.
    assert "silently re-introduce removed code" in payload["detail"]


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


# --- git could not establish the scope (A5) ------------------------------------
# The index enumeration IS this gate's scope: if git cannot read it, an empty
# path list is indistinguishable from "nothing staged". The gate must refuse
# rather than print a clean verdict over a scope it never read.


def test_non_repo_root_raises_instead_of_returning_empty(tmp_path: Path) -> None:
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()
    with pytest.raises(RuntimeError):
        csr.find_staged_reversions(str(not_a_repo))


def test_non_repo_root_cli_is_unestablished_not_clean(tmp_path: Path, capsys) -> None:
    """The refusal half: exit 1, and the word `clean` appears NOWHERE in what the
    operator reads. A gate that cannot read the index must not put a clean verdict in
    front of anyone, in any field."""
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()
    assert csr.main(["--repo-root", str(not_a_repo)]) == 1
    out = capsys.readouterr().out
    assert "clean" not in out
    # ...and the operator is told how to make the index readable again, which lived
    # only in the deleted human branch.
    assert "safe.directory" in out


def test_non_repo_root_cli_payload_is_unestablished(tmp_path: Path, capsys) -> None:
    """The payload half: a machine reader sees the distinct `unestablished` state with
    the underlying git error, not an empty finding list it would read as clean."""
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()
    assert csr.main(["--repo-root", str(not_a_repo)]) == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["state"] == "unestablished"
    assert payload["error"]


def test_dubious_ownership_does_not_report_clean_over_a_real_phantom(
    tmp_path: Path,
) -> None:
    """git exits 128 on a dubious-ownership repo (a common container/CI state).

    Pre-fix this printed {"state": "clean"} / exit 0 while a real staged
    reversion sat in the index -- the exact silent re-commit #258 exists to stop.
    """
    repo = _repo(tmp_path)
    _stage_phantom(repo)
    # Sanity: the phantom is genuinely there when git can read the repo.
    assert [f.case for f in csr.find_staged_reversions(str(repo))] == [
        "modified-reversion-phantom"
    ]

    env = {**os.environ, "GIT_TEST_ASSUME_DIFFERENT_OWNER": "1"}
    if _git_probe(repo, env).returncode == 0:
        pytest.skip("this git build does not honor GIT_TEST_ASSUME_DIFFERENT_OWNER")

    result = run_script(
        "scripts/check_staged_reversion.py", "--repo-root", str(repo), env=env
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert yaml.safe_load(result.stdout)["state"] == "unestablished"


def _git_probe(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), "status", "--short"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_a_deletion_phantom_recovery_names_the_untrack_reading(tmp_path: Path) -> None:
    """The discriminating half of the per-case recovery split."""
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "v1\n")
    _git(repo, "rm", "--cached", "-q", "f.py")

    recovery = csr.find_staged_reversions(str(repo))[0].recovery

    assert "--cached" in recovery
    assert csr._ENV_BYPASS in recovery


def test_an_unhashable_worktree_file_is_unestablished_not_dropped(tmp_path: Path) -> None:
    """A present-but-unhashable worktree copy is not the same fact as "absent".

    `None` from `_worktree_blob` MEANS "not on disk" -- it is what tells a deletion
    phantom from a modified one. Mapping a failed `hash-object` to `None` made a
    real phantom silently vanish (`None == head_blob` is False), so the gate printed
    clean over the exact corruption it exists to catch.
    """
    repo = _repo(tmp_path)
    _stage_phantom(repo)  # a genuine phantom is present first...
    assert len(csr.find_staged_reversions(str(repo))) == 1

    # ...then make the worktree copy a dangling symlink: lexists is True, so the
    # absent-on-disk early return is skipped, and hash-object fails.
    (repo / "f.py").unlink()
    (repo / "f.py").symlink_to(repo / "does-not-exist")

    with pytest.raises(RuntimeError):
        csr.find_staged_reversions(str(repo))


def test_an_unmerged_path_is_skipped_rather_than_read_as_a_phantom(tmp_path: Path) -> None:
    """Record [0] of a conflicted path is stage 1 (the merge base), not the index.

    Reading it as the staged blob reported `modified-reversion-phantom` over a
    normal mid-merge state. There is no stage 0 for a conflicted path and `git
    commit` refuses one anyway, so the honest answer is to skip it.
    """
    repo = _repo(tmp_path)
    _commit(repo, "f.py", "base\n")
    _git(repo, "checkout", "-q", "-b", "side")
    _commit(repo, "f.py", "side\n")
    _git(repo, "checkout", "-q", "-")
    _commit(repo, "f.py", "main\n")
    conflict = subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "merge", "side"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert conflict.returncode != 0, "fixture must produce a real conflict"
    # Resolve toward HEAD in the worktree WITHOUT staging: worktree == HEAD, and
    # stage 1 (the base) differs from HEAD -- the shape that used to be flagged.
    (repo / "f.py").write_text("main\n", encoding="utf-8")

    assert csr.find_staged_reversions(str(repo)) == []


def test_git_being_unusable_is_unestablished_not_clean(tmp_path: Path, monkeypatch) -> None:
    """`git` absent, or a cwd that cannot be entered, raises OSError before any
    returncode exists. Swallowing it would produce the same empty staged list a
    clean repo does — the fail-open this row closed, arriving by another door.
    """

    def _boom(*_args, **_kwargs):
        raise FileNotFoundError("No such file or directory: 'git'")

    monkeypatch.setattr(csr.subprocess, "run", _boom)

    with pytest.raises(RuntimeError) as excinfo:
        csr._staged_paths(str(tmp_path))
    assert "git" in str(excinfo.value)
