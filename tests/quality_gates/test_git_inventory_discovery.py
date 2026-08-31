from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .git_fixture_support import init_git_repo
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
    repo.mkdir()
    (repo / "tracked.py").write_text("x\n", encoding="utf-8")
    init_git_repo(repo, "tracked.py")
    files = _LIB.visible_repo_files(repo)
    assert files is not None
    assert repo / "tracked.py" in files
