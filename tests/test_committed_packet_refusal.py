"""Committed-ref packet selection stays exact and actionable."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from tests.quality_gates.git_fixture_support import init_git_repo

ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "skills/public/critique/scripts/prepare_packet.py"
RUN_REVIEW = ROOT / "skills/public/critique/scripts/run_review.py"


def _git(repo: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", "-c", "user.email=test@example.com", "-c", "user.name=Test", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _committed_packet_repo(repo: Path) -> str:
    init_git_repo(repo)
    (repo / "reviewed.txt").write_text("before\n", encoding="utf-8")
    (repo / ".agents").mkdir()
    (repo / ".agents/critique-adapter.yaml").write_text(
        "version: 1\n"
        "repo: packet-fixture\n"
        "reviewer_runner:\n"
        "  mode: file-backed-worker\n"
        "  backend: codex_exec\n"
        "  timeout_seconds: 5\n"
        "packet_sections:\n"
        "  - id: smoke\n"
        "    title: Smoke\n"
        "    content_kind: static\n"
        "    content: smoke\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "base")

    (repo / "reviewed.txt").write_text("after\n", encoding="utf-8")
    packet = repo / "charness-artifacts/critique/prior-packet.json"
    packet.parent.mkdir(parents=True)
    packet.write_text('{"kind":"charness.critique_prepare_packet"}\n', encoding="utf-8")
    _git(repo, "add", "reviewed.txt", str(packet.relative_to(repo)))
    _git(repo, "commit", "-q", "-m", "change with prior packet")
    return "HEAD"


def test_default_committed_packet_refusal_lists_omitted_paths_and_remedy(
    tmp_path: Path,
) -> None:
    changed_ref = _committed_packet_repo(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(PREPARE),
            "--repo-root",
            str(tmp_path),
            "--slug",
            "default-refusal",
            "--commit",
            changed_ref,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    payload = yaml.safe_load(result.stdout)
    packet_path = tmp_path / "charness-artifacts/critique/default-refusal-packet.json"
    assert result.returncode == 1
    assert payload["reason_code"] == "changed-ref-path-mismatch"
    assert payload["declared_paths"] == ["reviewed.txt"]
    assert payload["changed_ref_paths"] == [
        "charness-artifacts/critique/prior-packet.json",
        "reviewed.txt",
    ]
    assert payload["missing_paths"] == [
        "charness-artifacts/critique/prior-packet.json"
    ]
    assert payload["unexpected_paths"] == []
    assert payload["auto_excluded_paths"] == payload["missing_paths"]
    assert "--reviewed-paths-file <manifest>" in payload["error"]
    assert payload["remedy"] in payload["error"]
    assert not packet_path.exists()


def test_explicit_manifest_route_binds_prior_packet_without_self_inclusion(
    tmp_path: Path,
) -> None:
    changed_ref = _committed_packet_repo(tmp_path)
    manifest = tmp_path / "reviewed-paths.txt"
    manifest.write_text(
        "reviewed.txt\ncharness-artifacts/critique/prior-packet.json\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(RUN_REVIEW),
            "--repo-root",
            str(tmp_path),
            "--scope",
            "committed packet",
            "--lens",
            "operability",
            "--attempt-id",
            "manifest-route",
            "--commit",
            changed_ref,
            "--reviewed-paths-file",
            str(manifest.relative_to(tmp_path)),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 0, result.stderr
    packet_path = tmp_path / payload["paths"]["packet"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    identity = packet["reviewed_input_identity"]
    assert identity["reviewed_paths"] == [
        "charness-artifacts/critique/prior-packet.json",
        "reviewed.txt",
    ]
    assert identity["auto_excluded_paths"] == []
    assert "manifest-route-packet.json" not in identity["reviewed_paths"]
    assert payload["packet_verification"]["status"] == "current"


def test_semantic_wrapper_preserves_default_refusal_details(tmp_path: Path) -> None:
    changed_ref = _committed_packet_repo(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(RUN_REVIEW),
            "--repo-root",
            str(tmp_path),
            "--scope",
            "committed packet",
            "--lens",
            "operability",
            "--attempt-id",
            "wrapper-refusal",
            "--commit",
            changed_ref,
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 2
    assert payload["reason_code"] == "changed-ref-path-mismatch"
    assert payload["missing_paths"] == [
        "charness-artifacts/critique/prior-packet.json"
    ]
    assert "--reviewed-paths-file <manifest>" in payload["remedy"]
    assert payload["details"]["prepare"]["reason_code"] == payload["reason_code"]


def test_committed_refusal_reports_extra_declared_paths_too(tmp_path: Path) -> None:
    changed_ref = _committed_packet_repo(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(PREPARE),
            "--repo-root",
            str(tmp_path),
            "--slug",
            "extra-refusal",
            "--commit",
            changed_ref,
            "--reviewed-path",
            "reviewed.txt",
            "--reviewed-path",
            "not-in-ref.txt",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["missing_paths"] == [
        "charness-artifacts/critique/prior-packet.json"
    ]
    assert payload["unexpected_paths"] == ["not-in-ref.txt"]
    assert "not-in-ref.txt" in payload["error"]
