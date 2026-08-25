"""Parent-owned lesson sessions cannot be opened independently by workers."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pytest

from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import lesson_session_boundary as boundary
from scripts import open_lesson_session


def _parent(tmp_path: Path) -> tuple[Path, Path, bytes]:
    output = tmp_path / "charness-artifacts/retro"
    output.mkdir(parents=True)
    bundle = b"Lesson selection preview (1/1 eligible):\n- lesson-a \\u2014 use the measured path\n"
    bundle_path = output / "lesson-session-receipts" / "parent.md"
    bundle_path.parent.mkdir()
    bundle_path.write_bytes(bundle)
    snapshot = {
        "kind": "charness.lesson-selection-preview",
        "schema_version": 1,
        "selection_policy_version": 1,
        "seed": "parent",
        "eligible_count": 1,
        "bucket_counts": {"recent": 1, "value": 0, "uncertainty": 0, "archive": 0, "archive_fallback_uncertainty": 0},
        "lesson_ids": ["lesson-a"],
    }
    snapshot_sha = hashlib.sha256(
        json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    receipt = continuity.build_receipt(
        session_id="parent",
        snapshot_sha256=snapshot_sha,
        stdout_bytes=bundle,
        emitted_at="2026-08-25T00:00:00Z",
    )
    receipt_path = output / "lesson-session-receipts" / "parent.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    ledger = {
        "session_events": [{"session_id": "parent", "snapshot": snapshot, "snapshot_sha256": snapshot_sha}]
    }
    (output / "lesson-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
    return tmp_path, receipt_path, bundle


def test_worker_inherits_immutable_parent_bundle_and_writes_only_lane_receipt(tmp_path: Path) -> None:
    repo, _receipt, bundle = _parent(tmp_path)
    ledger_before = (repo / "charness-artifacts/retro/lesson-ledger.json").read_bytes()
    context, lane = boundary.inherit_worker_session(
        repo,
        bundle_path="charness-artifacts/retro/lesson-session-receipts/parent.md",
        lane_id="lane-a",
        owner_id="worker-a",
        session_id="parent",
    )
    assert context.session_id == "parent"
    assert lane == repo / ".charness/lesson-lanes/lane-a/receipt.json"
    assert json.loads(lane.read_text(encoding="utf-8"))["writes_enabled"] is False
    assert (repo / "charness-artifacts/retro/lesson-ledger.json").read_bytes() == ledger_before
    assert (repo / "charness-artifacts/retro/lesson-session-receipts/parent.md").read_bytes() == bundle


def test_worker_bundle_mutation_is_refused(tmp_path: Path) -> None:
    repo, _receipt, _bundle = _parent(tmp_path)
    context = boundary.load_parent_session(repo, session_id="parent")
    context.bundle_path.write_bytes(b"changed")
    with pytest.raises(boundary.LessonSessionBoundaryError, match="immutable"):
        boundary.load_parent_session(repo, session_id="parent")


def test_worker_write_fence_refuses_global_lesson_paths(tmp_path: Path) -> None:
    with pytest.raises(boundary.LessonSessionBoundaryError, match="parent-owned"):
        boundary.validate_lane_writes(
            tmp_path,
            ["scripts/worker.py", "charness-artifacts/retro/lesson-ledger.json"],
            lane_id="lane-a",
        )
    accepted = boundary.validate_lane_writes(
        tmp_path,
        ["charness-artifacts/retro/lesson-ledger.json"],
        assigned_paths=["charness-artifacts/retro/lesson-ledger.json"],
        owner_role="parent",
    )
    assert accepted["ok"] is True


def test_open_session_worker_mode_cannot_mutate_parent_ledger(tmp_path: Path) -> None:
    with pytest.raises(boundary.LessonSessionBoundaryError, match="cannot open or mutate"):
        open_lesson_session.open_session(
            repo_root=tmp_path,
            session_id="worker",
            seed="worker",
            stdout=io.BytesIO(),
            worker_mode=True,
        )
