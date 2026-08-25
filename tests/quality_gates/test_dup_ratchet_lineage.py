"""Consumer-boundary regression tests for duplicate-lineage provenance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .test_dup_ratchet import (
    _code_family,
    _consumer_repo,
    _doc_inventory,
    _run_gate,
    _run_inproc,
    _verdict,
    _write_json,
    baseline_lib,
    fingerprint,
)


@pytest.mark.parametrize(
    "overlay",
    [
        {},
        {
            "schemaVersion": "charness.quality.dup_review.v1",
            "fixable_ceiling": 0,
            "entries": {},
        },
        {
            "schemaVersion": "charness.quality.dup_review.v1",
            "fixable_ceiling": 0,
            "entries": [{"surface": "code", "id": "known1"}],
        },
    ],
)
def test_malformed_review_overlay_is_not_lineage_approval(
    tmp_path: Path, overlay: dict,
) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    (repo / "q" / "dup-review.json").write_text(json.dumps(overlay), encoding="utf-8")
    result = _run_gate(repo, tmp_path, code_ids=["known1"])
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = _verdict(result)
    assert verdict["status"] == "degraded"
    assert verdict["lineage_approval_eligible"] is False
    assert any("overlay integrity" in message for message in verdict["messages"])


def test_lineage_approval_requires_stamped_producer_identity(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",), intentional_code=("known1",))
    code_json = _write_json(
        tmp_path / "code.json",
        {
            "status": "findings",
            "tool_version": "0.20.0",
            "families": [_code_family("known1", ["known1"])],
        },
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(
        repo,
        "--code-inventory",
        str(code_json),
        "--doc-inventory",
        str(doc_json),
    )
    assert report["status"] == "clean"
    assert report["lineage_readiness"]["status"] == "unavailable"
    assert report["lineage_identity"]["status"] == "unknown"
    assert report["lineage_approval_eligible"] is False
    assert any("baseline scanner version stamp is missing" in message for message in report["messages"])


def test_lineage_approval_refuses_clean_scanner_version_skew(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",), intentional_code=("known1",))
    (repo / "q" / "dup-ratchet-baseline.json").write_text(
        json.dumps(
            baseline_lib.build_gate_baseline(
                {"known1": ["known1"]},
                member_paths={"known1": ["src/a.py"]},
                tool_version="0.19.0",
                algo_version=fingerprint.FINGERPRINT_ALGO_VERSION,
            )
        ),
        encoding="utf-8",
    )
    code_json = _write_json(
        tmp_path / "code.json",
        {
            "status": "findings",
            "tool_version": "0.20.0",
            "families": [_code_family("known1", ["known1"])],
        },
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(
        repo,
        "--code-inventory",
        str(code_json),
        "--doc-inventory",
        str(doc_json),
    )
    assert report["status"] == "clean"
    assert report["lineage_readiness"]["status"] == "ready"
    assert report["version_skew"]
    assert report["lineage_identity"]["status"] == "unknown"
    assert report["lineage_approval_eligible"] is False


def test_lineage_approval_refuses_clean_fingerprint_algorithm_skew(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",), intentional_code=("known1",))
    (repo / "q" / "dup-ratchet-baseline.json").write_text(
        json.dumps(
            baseline_lib.build_gate_baseline(
                {"known1": ["known1"]},
                member_paths={"known1": ["src/a.py"]},
                tool_version="0.20.0",
                algo_version="1",
            )
        ),
        encoding="utf-8",
    )
    code_json = _write_json(
        tmp_path / "code.json",
        {
            "status": "findings",
            "tool_version": "0.20.0",
            "families": [_code_family("known1", ["known1"])],
        },
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(
        repo,
        "--code-inventory",
        str(code_json),
        "--doc-inventory",
        str(doc_json),
    )
    assert report["status"] == "clean"
    assert report["lineage_readiness"]["status"] == "ready"
    assert report["algo_skew"]
    assert report["lineage_identity"]["status"] == "unknown"
    assert report["lineage_approval_eligible"] is False


def test_lineage_approval_requires_established_identity_but_can_pass(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",), intentional_code=("known1",))
    (repo / "q" / "dup-ratchet-baseline.json").write_text(
        json.dumps(
            baseline_lib.build_gate_baseline(
                {"known1": ["known1"]},
                member_paths={"known1": ["src/a.py"]},
                tool_version="0.20.0",
                algo_version=fingerprint.FINGERPRINT_ALGO_VERSION,
            )
        ),
        encoding="utf-8",
    )
    code_json = _write_json(
        tmp_path / "code.json",
        {
            "status": "findings",
            "tool_version": "0.20.0",
            "families": [_code_family("known1", ["known1"])],
        },
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(
        repo,
        "--code-inventory",
        str(code_json),
        "--doc-inventory",
        str(doc_json),
    )
    assert report["lineage_readiness"]["status"] == "ready"
    assert report["lineage_identity"]["status"] == "established"
    assert report["lineage_approval_eligible"] is True
