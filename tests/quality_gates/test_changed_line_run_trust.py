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


def test_porcelain_status_snapshot_covers_head_untracked_and_rename_destination() -> None:
    oid = b"a" * 40
    payload = (
        b"# branch.oid " + oid + b"\0"
        b"# branch.head main\0"
        b"1 .M N... 100644 100644 100644 " + oid + b" " + oid + b" scripts/edited.py\0"
        b"? scripts/new.py\0"
        b"2 R. N... 100644 100644 100644 " + oid + b" " + oid + b" R100 scripts/new-name.py\0"
        b"scripts/old-name.py\0"
        b"1 A. N... 100644 100644 100644 " + oid + b" " + oid + b" scripts/f\xc3\xb6.py\0"
    )
    snapshot = trust._parse_status_snapshot(payload)
    assert snapshot.head_oid == oid.decode("ascii")
    assert snapshot.paths == [
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
    oid = "a" * 40
    monkeypatch.setattr(
        trust,
        "_worktree_trust_snapshot",
        lambda *_args, **_kwargs: trust.WorktreeTrustSnapshot([], oid),
    )

    probe = trust.probe_run_trust(tmp_path, oid, set())

    assert probe.resolved_pair == (oid, oid)


def test_probe_run_trust_does_not_rev_parse_a_sha_already_on_the_status_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
    analyzed = "b" * 40
    live = "a" * 40
    monkeypatch.setattr(
        trust,
        "_worktree_trust_snapshot",
        lambda *_args, **_kwargs: trust.WorktreeTrustSnapshot([], live),
    )

    def forbidden(_repo_root: Path, args: list[str]) -> list[str]:
        raise AssertionError(args)

    monkeypatch.setattr(trust, "_git_lines_or_none", forbidden)
    probe = trust.probe_run_trust(tmp_path, analyzed, set())
    assert probe.resolved_pair == (analyzed, live)
    assert probe.unestablished_kind == trust.SCOPE_MISMATCH


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
