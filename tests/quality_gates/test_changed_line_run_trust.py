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


def test_probe_run_trust_exposes_the_resolved_revision_pair(
    tmp_path: Path, monkeypatch
) -> None:
    pair = ("a" * 40, "a" * 40)
    monkeypatch.setattr(trust, "_resolve_pair", lambda *_args, **_kwargs: pair)
    monkeypatch.setattr(trust, "_worktree_status_paths", lambda *_args, **_kwargs: [])

    probe = trust.probe_run_trust(tmp_path, "analyzed", set())

    assert probe.resolved_pair == pair


def test_pin_reuses_the_trust_probe_revision_pair(tmp_path: Path, monkeypatch) -> None:
    pair = ("a" * 40, "b" * 40)

    def forbidden(_repo_root: Path, args: list[str]) -> list[str]:
        raise AssertionError(args)

    monkeypatch.setattr(trust, "_git_lines", forbidden)
    monkeypatch.setattr(trust, "_git_lines_or_none", forbidden)
    monkeypatch.setattr(trust, "changed_pool_fingerprint", lambda *_args, **_kwargs: "fp")

    pinned = trust._pin_run_state(tmp_path, "base", "analyzed", resolved_pair=pair)

    assert pinned["resolved_head_sha"] == pair[0]
    assert pinned["head_commit"] == pair[1]
    assert pinned["pool_fingerprint"] == "fp"
