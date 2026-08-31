from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts import reviewed_input_identity as identity_lib
from scripts import reviewed_input_nonblob
from scripts.git_status_snapshot import status_args


def test_initialized_gitlink_uses_one_checked_out_snapshot_query(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    submodule_root = repo_root / "sub"
    submodule_root.mkdir(parents=True)
    calls: list[tuple[Path, tuple[str, ...]]] = []
    index_commit = "index-commit"
    checked_out_commit = "checked-out-commit"

    def fake_git_bytes_optional(root: Path, *args: str) -> bytes | None:
        calls.append((root, args))
        if args == ("ls-files", "-s", "--", "sub"):
            return f"160000 {index_commit} 0\tsub\n".encode()
        if args == ("rev-parse", "--show-toplevel", "HEAD"):
            return f"{submodule_root}\n{checked_out_commit}\n".encode()
        if args == ("status", "--porcelain"):
            return b""
        raise AssertionError(args)

    monkeypatch.setattr(reviewed_input_nonblob, "_git_bytes_optional", fake_git_bytes_optional)

    assert reviewed_input_nonblob._gitlink_commit(repo_root, "sub", None) == checked_out_commit
    # THREE queries, and the list is exact on purpose. The name still holds: the toplevel
    # and the commit are ONE `rev-parse`, not two. The cleanliness probe is a third
    # OBSERVATION, not a repeat -- a gitlink binds only the checked-out commit, so a dirty
    # worktree is a fact the snapshot cannot carry. Admitting it by widening this list is
    # correct; loosening the list to "at least these" would give up the budget entirely.
    assert calls == [
        (repo_root, ("ls-files", "-s", "--", "sub")),
        (submodule_root, ("rev-parse", "--show-toplevel", "HEAD")),
        (submodule_root, ("status", "--porcelain")),
    ]


@pytest.mark.parametrize("snapshot", [None, b"/another/repo\nchecked-out-commit\n"])
def test_gitlink_snapshot_keeps_index_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, snapshot: bytes | None
) -> None:
    repo_root = tmp_path / "repo"
    submodule_root = repo_root / "sub"
    submodule_root.mkdir(parents=True)
    index_commit = "index-commit"

    def fake_git_bytes_optional(_root: Path, *args: str) -> bytes | None:
        if args == ("ls-files", "-s", "--", "sub"):
            return f"160000 {index_commit} 0\tsub\n".encode()
        if args == ("rev-parse", "--show-toplevel", "HEAD"):
            return snapshot
        raise AssertionError(args)

    monkeypatch.setattr(reviewed_input_nonblob, "_git_bytes_optional", fake_git_bytes_optional)

    assert reviewed_input_nonblob._gitlink_commit(repo_root, "sub", None) == index_commit


def test_identity_reuses_gitlink_snapshot_between_path_phases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    submodule_root = repo_root / "sub"
    submodule_root.mkdir(parents=True)
    git_calls: list[tuple[str, ...]] = []

    def fake_git_bytes(_root: Path, *args: str) -> bytes:
        if args == status_args():
            return b"# branch.oid " + (b"a" * 40) + b"\0"
        return b""

    def fake_git_bytes_optional(_root: Path, *args: str) -> bytes | None:
        git_calls.append(args)
        if args == ("ls-files", "-s", "-z", "--", "sub"):
            return b"160000 index-commit 0\tsub\0"
        if args == ("rev-parse", "--show-toplevel", "HEAD"):
            return f"{submodule_root}\nchecked-out-commit\n".encode()
        if args == ("status", "--porcelain"):
            return b""
        raise AssertionError(args)

    monkeypatch.setattr(identity_lib, "_git_bytes", fake_git_bytes)
    monkeypatch.setattr(reviewed_input_nonblob, "_git_bytes_optional", fake_git_bytes_optional)

    captured = identity_lib.build_reviewed_input_identity(
        repo_root=repo_root, reviewed_paths=["sub"]
    )

    assert captured["status"] == "captured"
    # The reuse claim is about the SNAPSHOT: `rev-parse --show-toplevel HEAD` appears once
    # across both path phases, not once per phase. The cleanliness probe rides along on the
    # same single pass, so it appears once too.
    assert git_calls == [
        ("ls-files", "-s", "-z", "--", "sub"),
        ("rev-parse", "--show-toplevel", "HEAD"),
        ("status", "--porcelain"),
    ]


def test_shared_gitlink_snapshot_across_two_builds_asks_git_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A caller building an identity and later re-deriving it -- the exact shape
    `verify_reviewed_input_identity` uses to check a capture is still current --
    shares one `gitlink_snapshot` rather than re-probing the SAME unmoved
    submodule a second time. `_review_paths`' own directory-sweep probe used to
    re-run regardless of what the shared memo already held: it built and threw
    away a fresh local snapshot every call, so the downstream cache check in
    `_gitlink_sha256` never got a chance to skip anything.
    """
    repo_root = tmp_path / "repo"
    submodule_root = repo_root / "sub"
    submodule_root.mkdir(parents=True)
    git_calls: list[tuple[str, ...]] = []

    def fake_git_bytes(_root: Path, *args: str) -> bytes:
        if args == status_args():
            return b"# branch.oid " + (b"a" * 40) + b"\0"
        return b""

    def fake_git_bytes_optional(_root: Path, *args: str) -> bytes | None:
        git_calls.append(args)
        if args == ("ls-files", "-s", "-z", "--", "sub"):
            return b"160000 index-commit 0\tsub\0"
        if args == ("rev-parse", "--show-toplevel", "HEAD"):
            return f"{submodule_root}\nchecked-out-commit\n".encode()
        if args == ("status", "--porcelain"):
            return b""
        if args == ("ls-files", "-s", "--", "sub"):
            return b"160000 index-commit 0\tsub\n"
        raise AssertionError(args)

    monkeypatch.setattr(identity_lib, "_git_bytes", fake_git_bytes)
    monkeypatch.setattr(reviewed_input_nonblob, "_git_bytes_optional", fake_git_bytes_optional)
    # `_working_tree_digest`'s own removed-submodule check calls the IDENTITY
    # module's `_git_bytes_optional` (a separate function from the nonblob
    # one above), so it needs the same fake to stay in `git_calls` too.
    monkeypatch.setattr(identity_lib, "_git_bytes_optional", fake_git_bytes_optional)

    gitlink_snapshot: dict = {}
    first = identity_lib.build_reviewed_input_identity(
        repo_root=repo_root, reviewed_paths=["sub"], gitlink_snapshot=gitlink_snapshot
    )
    git_calls.clear()
    second = identity_lib.build_reviewed_input_identity(
        repo_root=repo_root, reviewed_paths=["sub"], gitlink_snapshot=gitlink_snapshot
    )

    # Only the always-fresh disk-presence check that decides `deleted` remains;
    # the gitlink probe itself (listing, rev-parse, cleanliness) is not repeated.
    assert git_calls == [("ls-files", "-s", "--", "sub")]
    assert second["identity_sha256"] == first["identity_sha256"]
    entry = next(e for e in second["reviewed_content"] if e["path"] == "sub")
    assert entry["content_sha256"] == hashlib.sha256(b"gitlink\0checked-out-commit").hexdigest()
