from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.core.git_status_snapshot import GitStatusError
from scripts.core.git_status_snapshot import capture as capture_status
from scripts.core.git_status_snapshot import parse as parse_status
from scripts.core.repo_file_listing import git_list_repo_files
from scripts.worktree import checkout_view
from scripts.worktree.checkout_view import FactsCheckout, GitCheckout
from tests.quality_gates.repo_shapes import install_committed_repo


def _status_payload(oid: bytes = b"a" * 40) -> bytes:
    return (
        b"# branch.oid " + oid + b"\0"
        b"# branch.head main\0"
        b"1 .M N... 100644 100644 100644 " + oid + b" " + oid + b" scripts/edited.py\0"
        b"? scripts/new.py\0"
    )


def test_facts_checkout_does_not_spawn_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args, **_kwargs):
        raise AssertionError("facts checkout must not ask Git")

    monkeypatch.setattr(subprocess, "run", forbidden)
    oid = "a" * 40
    files = [tmp_path / "scripts" / "edited.py"]
    view = FactsCheckout(tmp_path, status=parse_status(_status_payload()), files=files)
    assert view.status().head_oid == oid
    assert view.status().dirty_destination_paths() == ["scripts/edited.py", "scripts/new.py"]
    assert view.list_files() == files
    with pytest.raises(GitStatusError, match="no status snapshot"):
        FactsCheckout(tmp_path).status()


def test_git_checkout_reuses_status_for_the_same_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = parse_status(_status_payload())
    calls = 0

    def observed(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        return snapshot

    monkeypatch.setattr(checkout_view, "capture_status", observed)
    view = GitCheckout(tmp_path)
    assert view.status() is view.status()
    assert calls == 1
    view.status(ignored=True)
    assert calls == 2


def test_git_checkout_roundtrip_matches_git_observation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(repo, {"tracked.py": "base\n"})
    (repo / "dirty.py").write_text("x\n", encoding="utf-8")
    view = GitCheckout(repo)
    assert view.status() == capture_status(repo)
    assert view.list_files() == git_list_repo_files(repo)


def test_moment_and_tracked_membership_project_from_injected_facts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_args, **_kwargs):
        raise AssertionError("facts projections must not ask Git")

    monkeypatch.setattr(subprocess, "run", forbidden)
    snapshot = parse_status(_status_payload())
    moment = checkout_view.moment_from_status(snapshot)
    assert moment.head_oid == "a" * 40
    assert moment.branch == "main"
    assert moment.populations["untracked"] == ["scripts/new.py"]
    tracked = tmp_path / "scripts" / "edited.py"
    view = FactsCheckout(tmp_path, status=snapshot, files=[tracked])
    assert checkout_view.path_is_tracked(view, "scripts/edited.py") is True
    assert checkout_view.path_is_tracked(view, "scripts/new.py") is False
    from scripts.reviewed_input_worktree import WorkingTreeSnapshot

    tree = WorkingTreeSnapshot.from_status(snapshot)
    assert tree.branch_oid == "a" * 40
    assert tree.untracked_paths == frozenset({"scripts/new.py"})
    assert tree.unstaged_dirty is True
