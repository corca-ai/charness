"""Committed-ref packet selection stays exact and actionable."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tests.quality_gates.repo_shapes import install_two_commit_repo
from tests.quality_gates.support import run_script
from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "skills/public/critique/scripts/prepare_packet.py"
RUN_REVIEW = ROOT / "skills/public/critique/scripts/run_review.py"
RUN_REVIEW_MODULE = load_script_module("run_review_under_test", RUN_REVIEW)

_PACKET_ADAPTER = (
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
    "    content: smoke\n"
)


def _committed_packet_repo(repo: Path) -> str:
    install_two_commit_repo(
        repo,
        {
            "reviewed.txt": "before\n",
            ".agents/critique-adapter.yaml": _PACKET_ADAPTER,
        },
        {
            "reviewed.txt": "after\n",
            "charness-artifacts/critique/prior-packet.json": (
                '{"kind":"charness.critique_prepare_packet"}\n'
            ),
        },
        first_message="base",
        second_message="change with prior packet",
    )
    return "HEAD"


def run_review(*args: str):
    return run_loaded_script_main("run_review.py", RUN_REVIEW_MODULE, *args)


def test_default_committed_packet_refusal_lists_omitted_paths_and_remedy(
    tmp_path: Path,
) -> None:
    changed_ref = _committed_packet_repo(tmp_path)
    result = run_script(
        str(PREPARE),
        "--repo-root",
        str(tmp_path),
        "--slug",
        "default-refusal",
        "--commit",
        changed_ref,
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
    result = run_review(
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
    result = run_review(
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
    result = run_script(
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
    )

    payload = yaml.safe_load(result.stdout)
    assert result.returncode == 1
    assert payload["missing_paths"] == [
        "charness-artifacts/critique/prior-packet.json"
    ]
    assert payload["unexpected_paths"] == ["not-in-ref.txt"]
    assert "not-in-ref.txt" in payload["error"]
