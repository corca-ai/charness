from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import git_checkout as checkout
from scripts.git_status_snapshot import GitStatusError
from scripts.git_status_snapshot import capture as capture_status
from tests.quality_gates.git_fixture_support import init_git_repo


def test_plain_directory_is_not_discoverable_and_is_not_a_local_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "plain"
    repo.mkdir()
    assert checkout.discoverable(repo) is False
    assert checkout.local_checkout(repo) is False
    assert checkout.head_oid_from_files(repo) is None


def test_empty_git_directory_is_not_discoverable(tmp_path: Path) -> None:
    repo = tmp_path / "empty"
    repo.mkdir()
    (repo / ".git").mkdir()
    assert checkout.discoverable(repo) is False
    assert checkout.local_checkout(repo) is False


def test_bare_repository_signature_is_discoverable(tmp_path: Path) -> None:
    repo = tmp_path / "bare.git"
    (repo / "objects").mkdir(parents=True)
    (repo / "refs").mkdir()
    (repo / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    assert checkout.discoverable(repo) is True
    assert checkout.local_checkout(repo) is False


def test_real_checkout_projects_discoverable_local_and_head(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "tracked.py").write_text("base\n", encoding="utf-8")
    init_git_repo(repo, "tracked.py")
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    assert checkout.discoverable(repo) is True
    assert checkout.local_checkout(repo) is True
    head = checkout.head_oid_from_files(repo)
    assert head is not None
    expected = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert head == expected
    identity = checkout.identity_from_files(repo)
    assert identity is not None
    assert identity.repo_root == repo.resolve()
    assert identity.git_dir == (repo / ".git").resolve()
    assert identity.common_dir == (repo / ".git").resolve()
    assert identity.head_oid == expected
    nested = repo / "sub"
    nested.mkdir()
    assert checkout.worktree_root_from_files(nested) == repo.resolve()


def test_discovery_env_admits_git_but_refuses_file_projections(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "plain"
    repo.mkdir()
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "elsewhere"))
    assert checkout.discoverable(repo) is True
    assert checkout.local_checkout(repo) is False
    assert checkout.head_oid_from_files(repo) is None


def test_status_capture_does_not_spawn_git_when_undiscoverable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "plain"
    repo.mkdir()
    launches: list[tuple[str, ...]] = []
    original = subprocess.run

    def wrapped(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            launches.append(tuple(str(part) for part in argv[1:]))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", wrapped)
    with pytest.raises(GitStatusError, match="Git discovery preflight"):
        capture_status(repo)
    assert launches == []
