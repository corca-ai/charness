from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.core.repo_file_listing import (
    RepoFileSnapshot,
    bind_subject_listing,
    unbind_subject_listing,
)
from tests.quality_gates.repo_shapes import install_committed_repo

from .seeding_support import load_module
from .support import ROOT

_LIB = load_module(
    "git_inventory_lib_discovery_under_test",
    ROOT / "skills" / "public" / "quality" / "scripts" / "git_inventory_lib.py",
    register=True,
)


def test_visible_repo_files_does_not_launch_git_on_a_plain_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "plain"
    repo.mkdir()
    (repo / "a.py").write_text("x\n", encoding="utf-8")
    launches: list[tuple[str, ...]] = []
    original = subprocess.run

    def wrapped(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            launches.append(tuple(str(part) for part in argv[1:]))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", wrapped)
    assert _LIB.visible_repo_files(repo) is None
    assert launches == []


def test_visible_repo_files_require_git_refuses_a_plain_directory_without_git(
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
    with pytest.raises(_LIB.GitFileListingError, match="Git discovery preflight"):
        _LIB.visible_repo_files(repo, require_git=True)
    assert launches == []


def test_visible_repo_files_lists_a_real_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(repo, {"tracked.py": "x\n"})
    files = _LIB.visible_repo_files(repo)
    assert files is not None
    assert repo / "tracked.py" in files


def test_visible_repo_files_reuses_a_bound_subject_listing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tracked = repo / "tracked.py"
    tracked.write_text("x\n", encoding="utf-8")
    calls = 0

    # The module object the lib's snapshot class was defined in, not whatever
    # `scripts.core.repo_file_listing` names right now: an earlier eviction in the
    # same worker can leave the package attribute on a different object, and a
    # patch on that one reaches nothing (the #779 push refusal).
    listing = sys.modules[RepoFileSnapshot.__module__]

    def counted(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        return [tracked]

    monkeypatch.setattr(listing, "git_list_repo_files", counted)
    bind_subject_listing(RepoFileSnapshot(repo, require_git=True))
    try:
        first = _LIB.visible_repo_files(repo, require_git=True)
        second = _LIB.visible_repo_files(repo, require_git=True)
        assert first == second == {tracked}
        assert calls == 1
    finally:
        unbind_subject_listing(repo, require_git=True)
