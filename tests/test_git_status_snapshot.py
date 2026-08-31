from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import git_status_snapshot as status
from tests.quality_gates.git_fixture_support import init_git_repo


def test_parse_projects_head_dirty_deleted_and_rename_destination() -> None:
    oid = b"a" * 40
    payload = (
        b"# branch.oid " + oid + b"\0"
        b"# branch.head main\0"
        b"# branch.upstream origin/main\0"
        b"1 .M N... 100644 100644 100644 " + oid + b" " + oid + b" edited.py\0"
        b"1 D. N... 100644 000000 000000 " + oid + b" " + (b"0" * 40) + b" gone.py\0"
        b"2 R. N... 100644 100644 100644 " + oid + b" " + oid + b" R100 renamed.py\0"
        b"old.py\0"
        b"? new.py\0"
        b"! .cache\0"
    )
    snapshot = status.parse(payload)
    assert snapshot.head_oid == oid.decode("ascii")
    assert snapshot.branch == "main"
    assert snapshot.dirty_destination_paths() == ["edited.py", "gone.py", "renamed.py", "new.py"]
    assert snapshot.deleted_paths() == frozenset({"gone.py"})
    assert snapshot.populations() == {
        "tracked": ["edited.py", "gone.py", "old.py", "renamed.py"],
        "untracked": ["new.py"],
        "ignored": [".cache"],
    }
    assert snapshot.staged_or_unstaged_dirty() == (True, True)
    assert snapshot.untracked_paths() == frozenset({"new.py"})


def test_parse_rejects_malformed_and_duplicate_oids() -> None:
    with pytest.raises(status.GitStatusError, match="unexpected git status record"):
        status.parse(b"x\0")
    with pytest.raises(status.GitStatusError, match="multiple branch OIDs"):
        status.parse(b"# branch.oid " + b"a" * 40 + b"\0# branch.oid " + b"b" * 40 + b"\0")
    with pytest.raises(status.GitStatusError, match="unexpected git status record"):
        status.parse(b"2 R. N... 100644 100644 100644 " + b"a" * 40 + b" " + b"a" * 40 + b" R100 renamed.py\0")


def test_status_args_vary_the_observation_not_the_parser() -> None:
    assert status.status_args() == (
        "status",
        "--porcelain=v2",
        "--branch",
        "--untracked-files=all",
        "-z",
    )
    assert status.status_args(ignored=True)[-2:] == ("--ignored=matching", "-z")
    assert status.status_args(branch=False, untracked="no", no_renames=True) == (
        "status",
        "--porcelain=v2",
        "--no-renames",
        "--untracked-files=no",
        "-z",
    )


def test_capture_reads_a_real_checkout_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    (repo / "tracked.py").write_text("dirty\n", encoding="utf-8")
    (repo / "extra.py").write_text("new\n", encoding="utf-8")
    calls: list[tuple[str, ...]] = []
    original = subprocess.run

    def wrapped(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            calls.append(tuple(str(part) for part in argv[1:]))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", wrapped)
    snapshot = status.capture(repo)
    assert calls == [status.status_args()]
    assert snapshot.head_oid is not None
    assert "tracked.py" in snapshot.dirty_destination_paths()
    assert "extra.py" in snapshot.untracked_paths()
