"""Tests for the #258 staged-reversion pre-commit gate.

The gate (`scripts/hooks/check_staged_reversion.py`) flags only the unambiguous
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

from tests.quality_gates.repo_shapes import install_committed_repo

from .git_fixture_support import init_git_repo
from .support import run_script

csr = importlib.import_module("scripts.hooks.check_staged_reversion")


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


def _committed(tmp_path: Path, name: str, content: str) -> Path:
    return install_committed_repo(tmp_path / "repo", {name: content})


def _stage_phantom(tmp_path: Path) -> Path:
    """HEAD == v2, index == v1 (staged reversion), worktree == v2 == HEAD."""
    repo = _committed(tmp_path, "f.py", "v2\n")
    (repo / "f.py").write_text("v1\n", encoding="utf-8")
    _git(repo, "add", "f.py")
    (repo / "f.py").write_text("v2\n", encoding="utf-8")
    return repo


def test_classify_reversion_reads_the_three_blob_fingerprint() -> None:
    modified = csr.classify_reversion("f.py", head_blob="h", index_blob="i", worktree_blob="h")
    assert modified is not None
    assert modified.case == "modified-reversion-phantom"
    assert "--cached" not in modified.recovery

    deletion = csr.classify_reversion("f.py", head_blob="h", index_blob=None, worktree_blob="h")
    assert deletion is not None
    assert deletion.case == "staged-deletion-phantom"
    assert "--cached" in deletion.recovery

    assert csr.classify_reversion("f.py", head_blob="h", index_blob="w", worktree_blob="w") is None
    assert csr.classify_reversion("f.py", head_blob="h", index_blob="h", worktree_blob="h") is None
    assert (
        csr.classify_reversion("f.py", head_blob="h", index_blob=None, worktree_blob=None) is None
    )
    assert csr.classify_reversion("b.py", head_blob=None, index_blob="n", worktree_blob="n") is None
    assert (
        csr.classify_reversion(
            "f.py", head_blob="h", index_blob="i", worktree_blob="h", unmerged=True
        )
        is None
    )
    assert (
        csr.classify_reversion(
            "sub", head_blob="h", index_blob="i", worktree_blob="h", gitlink=True
        )
        is None
    )


def test_find_staged_reversions_classifies_injected_triples_without_git(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args, **_kwargs):
        raise AssertionError("injected triples must not ask Git")

    monkeypatch.setattr(csr, "_git", forbidden)
    findings = csr.find_staged_reversions(
        "/unused",
        triples=[
            {
                "path": "f.py",
                "head_blob": "h",
                "index_blob": "i",
                "worktree_blob": "h",
            },
            {
                "path": "ok.py",
                "head_blob": "h",
                "index_blob": "h",
                "worktree_blob": "h",
            },
        ],
    )
    assert [item.path for item in findings] == ["f.py"]
    assert findings[0].case == "modified-reversion-phantom"


def test_phantom_modified_reversion_is_flagged_and_blocks_cli(tmp_path: Path) -> None:
    repo = _stage_phantom(tmp_path)
    findings = csr.find_staged_reversions(str(repo))
    assert [f.case for f in findings] == ["modified-reversion-phantom"]
    assert findings[0].path == "f.py"
    assert "git add" in findings[0].recovery
    assert "--cached" not in findings[0].recovery
    result = run_script("scripts/hooks/check_staged_reversion.py", "--repo-root", str(repo))
    assert result.returncode == 1, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["state"] == "blocked"
    assert [finding["path"] for finding in payload["findings"]] == ["f.py"]
    assert "silently re-introduce removed code" in payload["detail"]


def test_mode_only_stage_is_the_same_blob(tmp_path: Path) -> None:
    """Mode-only stages keep the blob; Git must not invent a phantom hash."""
    repo = _committed(tmp_path, "f.py", "v1\n")
    (repo / "f.py").chmod(0o755)
    _git(repo, "add", "f.py")  # same blob, only the mode changed
    assert csr.find_staged_reversions(str(repo)) == []


def test_staged_deletion_phantom_is_flagged(tmp_path: Path) -> None:
    repo = _committed(tmp_path, "f.py", "v1\n")
    _git(repo, "rm", "--cached", "-q", "f.py")  # index deletes; worktree keeps v1 == HEAD
    findings = csr.find_staged_reversions(str(repo))
    assert [f.case for f in findings] == ["staged-deletion-phantom"]


def test_cli_bypass_allows_without_a_repo(monkeypatch, capsys) -> None:
    assert csr.main(["--repo-root", "/nonexistent", "--allow-staged-reversion"]) == 0
    assert "allowed" in capsys.readouterr().out
    monkeypatch.setenv("CHARNESS_ALLOW_STAGED_REVERSION", "1")
    assert csr.main(["--repo-root", "/nonexistent"]) == 0
    assert "allowed" in capsys.readouterr().out


# --- git could not establish the scope (A5) ------------------------------------
# The index enumeration IS this gate's scope: if git cannot read it, an empty
# path list is indistinguishable from "nothing staged". The gate must refuse
# rather than print a clean verdict over a scope it never read.


def test_non_repo_root_is_unestablished_not_clean(tmp_path: Path, capsys) -> None:
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()
    with pytest.raises(RuntimeError):
        csr.find_staged_reversions(str(not_a_repo))
    assert csr.main(["--repo-root", str(not_a_repo)]) == 1
    out = capsys.readouterr().out
    assert "clean" not in out
    assert "safe.directory" in out
    payload = yaml.safe_load(out)
    assert payload["state"] == "unestablished"
    assert payload["error"]


def test_dubious_ownership_does_not_report_clean_over_a_real_phantom(
    tmp_path: Path,
) -> None:
    """git exits 128 on a dubious-ownership repo (a common container/CI state).

    Pre-fix this printed {"state": "clean"} / exit 0 while a real staged
    reversion sat in the index -- the exact silent re-commit #258 exists to stop.
    """
    repo = _stage_phantom(tmp_path)
    # Sanity: the phantom is genuinely there when git can read the repo.
    assert [f.case for f in csr.find_staged_reversions(str(repo))] == ["modified-reversion-phantom"]

    env = {**os.environ, "GIT_TEST_ASSUME_DIFFERENT_OWNER": "1"}
    if _git_probe(repo, env).returncode == 0:
        pytest.skip("this git build does not honor GIT_TEST_ASSUME_DIFFERENT_OWNER")

    result = run_script(
        "scripts/hooks/check_staged_reversion.py", "--repo-root", str(repo), env=env
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
    repo = _committed(tmp_path, "f.py", "v1\n")
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
    repo = _stage_phantom(tmp_path)  # a genuine phantom is present first...
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
        csr._staged_raw_diff(str(tmp_path))
    assert "git" in str(excinfo.value)
