from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.quality_gates import seeding_support as seeds
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.quality_gates.seeding_support import git


def test_install_committed_repo_is_a_copy_with_no_test_time_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    files = {"README.md": "# seed\n", "src/app.py": "x = 1\n"}
    first = install_committed_repo(tmp_path / "one", files)
    assert git(first, "rev-parse", "--abbrev-ref", "HEAD") == "main"
    launches: list[tuple[str, ...]] = []
    original = seeds._run

    def wrapped(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            launches.append(tuple(str(part) for part in argv))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(seeds, "_run", wrapped)
    monkeypatch.setattr(subprocess, "run", wrapped)
    second = install_committed_repo(tmp_path / "two", files)
    assert launches == []
    assert (second / "README.md").read_text(encoding="utf-8") == "# seed\n"
    assert (second / "src/app.py").read_text(encoding="utf-8") == "x = 1\n"
    assert git(first, "rev-parse", "HEAD") == git(second, "rev-parse", "HEAD")


def test_install_committed_repo_keeps_executable_bits_without_test_time_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    files = {"bin/run.sh": "#!/bin/sh\necho ok\n", "README.md": "# seed\n"}
    first = install_committed_repo(
        tmp_path / "one", files, executable=("bin/run.sh",)
    )
    assert (first / "bin" / "run.sh").stat().st_mode & 0o111
    launches: list[tuple[str, ...]] = []
    original = seeds._run

    def wrapped(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            launches.append(tuple(str(part) for part in argv))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(seeds, "_run", wrapped)
    monkeypatch.setattr(subprocess, "run", wrapped)
    second = install_committed_repo(
        tmp_path / "two", files, executable=("bin/run.sh",)
    )
    assert launches == []
    assert (second / "bin" / "run.sh").stat().st_mode & 0o111
    assert git(first, "rev-parse", "HEAD") == git(second, "rev-parse", "HEAD")


def test_install_committed_repo_refuses_a_non_empty_destination(tmp_path: Path) -> None:
    dest = tmp_path / "repo"
    dest.mkdir()
    (dest / "stray.txt").write_text("nope\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty"):
        install_committed_repo(dest, {"README.md": "# seed\n"})
