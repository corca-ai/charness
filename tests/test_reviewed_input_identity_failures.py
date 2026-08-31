from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import reviewed_input_identity as identity_lib
from scripts import reviewed_input_verification as verification_lib
from scripts.git_status_snapshot import parse as parse_status
from scripts.reviewed_input_worktree import WorkingTreeSnapshot
from tests.quality_gates.repo_shapes import install_two_commit_repo


def _init_repo(repo: Path) -> None:
    install_two_commit_repo(
        repo,
        {"reviewed.txt": "one\n"},
        {"reviewed.txt": "two\n"},
        first_message="first",
        second_message="second",
    )


def test_changed_ref_range_and_empty_path_identity(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    ranged = identity_lib.build_reviewed_input_identity(
        repo_root=tmp_path, changed_ref="HEAD~1..HEAD"
    )
    with pytest.raises(ValueError, match="changed-ref path set"):
        identity_lib.build_reviewed_input_identity(
            repo_root=tmp_path, changed_ref="HEAD", reviewed_paths=[]
        )

    assert ranged["reviewed_paths"] == ["reviewed.txt"]
    assert ranged["reviewed_patch_sha256"] != hashlib.sha256(b"").hexdigest()


def test_worktree_content_os_error_is_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(identity_lib, "_checked_path", lambda *_args: (_ for _ in ()).throw(OSError()))
    assert identity_lib._worktree_content_sha256(tmp_path, "missing") is None


def test_clean_worktree_identity_skips_empty_patch_processes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repo(tmp_path)
    calls: list[tuple[str, ...]] = []
    original = identity_lib._git_bytes

    def observed(repo_root: Path, *args: str) -> bytes:
        calls.append(args)
        return original(repo_root, *args)

    monkeypatch.setattr(identity_lib, "_git_bytes", observed)
    captured = identity_lib.build_reviewed_input_identity(
        repo_root=tmp_path, reviewed_paths=["reviewed.txt"]
    )

    from scripts.git_status_snapshot import status_args

    assert captured["status"] == "captured"
    assert calls == [status_args()]


def test_committed_ref_identity_does_not_probe_is_inside_work_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repo(tmp_path)
    calls: list[tuple[str, ...]] = []
    original = identity_lib._git_bytes

    def observed(repo_root: Path, *args: str) -> bytes:
        calls.append(args)
        return original(repo_root, *args)

    monkeypatch.setattr(identity_lib, "_git_bytes", observed)
    captured = identity_lib.build_reviewed_input_identity(
        repo_root=tmp_path, changed_ref="HEAD"
    )
    assert captured["status"] == "captured"
    assert all(args[:2] != ("rev-parse", "--is-inside-work-tree") for args in calls)


def test_worktree_status_snapshot_parses_only_nul_untracked_records() -> None:
    branch_oid = b"a" * 40
    utf8_path = "目录/文件.txt".encode("utf-8")
    surrogate_path = b"invalid-\xff.txt"
    tracked_path = b"tracked-looking-untracked.txt"
    snapshot = WorkingTreeSnapshot.from_status(
        parse_status(
            b"# branch.oid "
            + branch_oid
            + b"\0# branch.head main\0? "
            + utf8_path
            + b"\0? "
            + surrogate_path
            + b"\0"
            + b"1 .M N... 100644 100644 100644 "
            + branch_oid
            + b" "
            + branch_oid
            + b" "
            + tracked_path
            + b"\0"
        )
    )

    assert snapshot.branch_oid == branch_oid.decode()
    assert snapshot.untracked_paths == {
        "目录/文件.txt",
        surrogate_path.decode("utf-8", errors="surrogateescape"),
    }
    assert snapshot.staged_dirty is False
    assert snapshot.unstaged_dirty is True


def test_status_snapshot_derives_only_conservative_patch_dirty_bits() -> None:
    oid = b"a" * 40
    cases = (
        (b"1 M. N... 100644 100644 100644 " + oid + b" " + oid + b" fixture", True, False),
        (b"1 .M N... 100644 100644 100644 " + oid + b" " + oid + b" fixture", False, True),
        (
            b"u UU N... 100644 100644 100644 100644 "
            + oid + b" " + oid + b" " + oid + b" fixture",
            True,
            True,
        ),
        (b"? untracked.txt", False, False),
    )
    for record, staged, unstaged in cases:
        snapshot = WorkingTreeSnapshot.from_status(
            parse_status(b"# branch.oid " + oid + b"\0" + record + b"\0")
        )
        assert snapshot.staged_dirty is staged, record
        assert snapshot.unstaged_dirty is unstaged, record


def test_unknown_status_record_fails_closed() -> None:
    from scripts.git_status_snapshot import GitStatusError

    with pytest.raises(GitStatusError, match="unexpected git status record"):
        parse_status(b"# branch.oid " + (b"a" * 40) + b"\0unknown\0")


def test_worktree_identity_makes_invalid_status_head_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outputs = (
        b"# branch.oid (initial)\0",
        b"# branch.head main\0",
        b"# branch.oid \0",
        b"# branch.oid " + (b"g" * 40) + b"\0",
        b"# branch.oid " + (b"0" * 40) + b"\0",
        b"# branch.oid " + (b"a" * 41) + b"\0",
    )
    for status_output in outputs:
        monkeypatch.setattr(identity_lib, "_git_bytes", lambda _root, *args, captured=status_output: captured)
        identity = identity_lib.build_reviewed_input_identity(
            repo_root=tmp_path, reviewed_paths=["reviewed.txt"]
        )
        assert identity["status"] == "unavailable", status_output
        assert "git status" in identity["reason"]


def test_non_repository_status_failure_returns_typed_unavailable_identity(
    tmp_path: Path,
) -> None:
    identity = identity_lib.build_reviewed_input_identity(
        repo_root=tmp_path, reviewed_paths=["reviewed.txt"]
    )

    assert identity["status"] == "unavailable"
    assert identity["substrate_mode"] == identity_lib.SUBSTRATE_WORKING_TREE
    assert "git status" in identity["reason"]


def test_auto_committed_ref_paths_are_swept_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def swept(*_args) -> list[str]:
        nonlocal calls
        calls += 1
        return ["reviewed.txt"]

    monkeypatch.setattr(identity_lib, "_auto_paths", swept)

    paths, excluded = identity_lib._review_paths(
        tmp_path,
        None,
        "HEAD",
        identity_lib.SUBSTRATE_COMMITTED_REF,
        None,
        None,
    )

    assert paths == ["reviewed.txt"]
    assert excluded == []
    assert calls == 1


def test_identity_reconstruction_failures(tmp_path: Path) -> None:
    assert verification_lib.verify_reviewed_input_identity(tmp_path, {"status": "unavailable"}) == (
        False,
        "reviewed input identity was unavailable when the packet was produced",
    )
    assert verification_lib.verify_reviewed_input_identity(
        tmp_path,
        {"status": "captured", "algorithm": "sha256-v2", "identity_sha256": "missing"},
    ) == (False, "declared reviewed inputs cover zero paths")
    ok, reason = verification_lib.verify_reviewed_input_identity(
        tmp_path,
        {
            "status": "captured",
            "algorithm": "sha256-v2",
            "reviewed_paths": 5,
            "identity_sha256": "missing",
        },
    )
    assert not ok
    assert reason.startswith("cannot reconstruct reviewed input identity:")


def _write_packet(tmp_path: Path, relative: str, payload: bytes) -> tuple[str, str]:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return relative, hashlib.sha256(payload).hexdigest()


def test_packet_binding_rejects_malformed_payloads(tmp_path: Path) -> None:
    cases = (
        (b"not-json", "x", "reviewed packet is not valid JSON"),
        (json.dumps({"kind": "wrong"}).encode(), "x", "reviewed packet has the wrong kind"),
        (
            json.dumps({"kind": "critique-prepare-packet"}).encode(),
            "x",
            "reviewed packet has no reviewed input identity",
        ),
        (
            json.dumps(
                {
                    "kind": "critique-prepare-packet",
                    "reviewed_input_identity": {"identity_sha256": "actual"},
                }
            ).encode(),
            "other",
            "artifact identity does not match the reviewed packet",
        ),
    )
    for payload, identity_sha, reason in cases:
        packet_path, digest = _write_packet(tmp_path, "packets/input.json", payload)
        assert verification_lib.verify_packet_binding(
            repo_root=tmp_path,
            packet_path=packet_path,
            packet_sha256=digest,
            identity_sha256=identity_sha,
            expected_kind="critique-prepare-packet",
        ) == (False, reason)


def test_packet_binding_rejects_outside_and_missing_paths(tmp_path: Path) -> None:
    assert verification_lib.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="../outside.json",
        packet_sha256="x",
        identity_sha256="x",
        expected_kind="critique-prepare-packet",
    ) == (False, "reviewed packet path resolves outside repo root")
    assert verification_lib.verify_packet_binding(
        repo_root=tmp_path,
        packet_path="missing.json",
        packet_sha256="x",
        identity_sha256="x",
        expected_kind="critique-prepare-packet",
    ) == (False, "reviewed packet does not exist: missing.json")


def test_artifact_binding_repo_fallbacks(tmp_path: Path) -> None:
    nested = tmp_path / "one/two/artifact.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("artifact", encoding="utf-8")
    fields = {"packet path": "missing.json", "packet sha256": "x", "identity sha256": "x"}

    assert verification_lib.verify_artifact_binding(
        nested, fields, expected_kind="critique-prepare-packet"
    )[1].startswith("reviewed packet does not exist")
    assert verification_lib.verify_artifact_binding(
        Path("/standalone.md"), fields, expected_kind="critique-prepare-packet"
    ) == (False, "cannot resolve repository root for reviewed input binding")


def test_declared_binding_reports_missing_fields(tmp_path: Path) -> None:
    assert verification_lib.verify_declared_binding(
        tmp_path / "artifact.md",
        {"packet path": "packet.json"},
        required=True,
        required_fields=verification_lib.ARTIFACT_REQUIRED_FIELDS,
        expected_kind="critique-prepare-packet",
    )[1].startswith("reviewed input identity missing fields:")
