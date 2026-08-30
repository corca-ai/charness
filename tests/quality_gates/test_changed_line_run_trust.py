from __future__ import annotations

from pathlib import Path

from scripts import changed_line_run_trust as trust


def test_git_lines_empty_outside_git_repo(tmp_path: Path) -> None:
    assert trust.uncommitted_pool_changes(tmp_path, {"scripts/foo.py"}) == []


def test_git_lines_handles_missing_git_binary(tmp_path: Path, monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise OSError("git not found")

    monkeypatch.setattr(trust.subprocess, "run", boom)
    assert trust._git_lines(tmp_path, ["status"]) == []
    assert trust._head_resolves_to_head(tmp_path, "some-ref") is False


def test_porcelain_status_paths_cover_tracked_untracked_and_rename_destination() -> None:
    payload = (
        b" M scripts/edited.py\0"
        b"?? scripts/new.py\0"
        b"R  scripts/new-name.py\0scripts/old-name.py\0"
        b"A  scripts/f\xc3\xb6.py\0"
    )

    assert trust._parse_status_paths(payload) == [
        "scripts/edited.py",
        "scripts/new.py",
        "scripts/new-name.py",
        "scripts/fö.py",
    ]


def test_revision_pair_uses_one_git_snapshot(tmp_path: Path, monkeypatch) -> None:
    calls: list[list[str]] = []

    def resolve(_repo_root: Path, args: list[str]) -> list[str]:
        calls.append(args)
        return ["a" * 40, "a" * 40]

    monkeypatch.setattr(trust, "_git_lines_or_none", resolve)

    assert trust._head_resolves_to_head(tmp_path, "release-ref") is True
    assert calls == [["rev-parse", "release-ref", "HEAD"]]
