from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from scripts import reviewed_input_identity as identity_lib
from scripts import reviewed_input_verification as verification_lib


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def _init_repo(repo: Path) -> None:
    _git(repo, "init")
    (repo / "reviewed.txt").write_text("one\n", encoding="utf-8")
    _git(repo, "add", "reviewed.txt")
    _git(repo, "commit", "-m", "first")
    (repo / "reviewed.txt").write_text("two\n", encoding="utf-8")
    _git(repo, "commit", "-am", "second")


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


@pytest.mark.parametrize(
    ("payload", "identity_sha", "reason"),
    [
        (b"not-json", "x", "reviewed packet is not valid JSON"),
        (json.dumps({"kind": "wrong"}).encode(), "x", "reviewed packet has the wrong kind"),
        (json.dumps({"kind": "critique-prepare-packet"}).encode(), "x", "reviewed packet has no reviewed input identity"),
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
    ],
)
def test_packet_binding_rejects_malformed_payloads(
    tmp_path: Path, payload: bytes, identity_sha: str, reason: str
) -> None:
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
