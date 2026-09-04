"""Commit-msg release-lane receipt check."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.hooks.check_release_lane_receipt import evaluate, receipt_matches_index

PASSING = {
    "surface": "quality",
    "status": "pass",
    "effective_exit_code": 0,
    "details": {
        "release": True,
        "full_queue": True,
        "index_tree": "abc123",
    },
}


def test_slice_reopen_is_admitted_without_a_receipt() -> None:
    code, text = evaluate(
        repo_root=Path("."),
        commit_message="slice work\n\nSlice-reopen: task-run\n",
        paths=["scripts/foo.py"],
        tree="abc123",
        receipt=None,
    )
    assert code == 0
    assert "Slice-reopen" in text


def test_unscoped_paths_do_not_require_a_receipt() -> None:
    code, text = evaluate(
        repo_root=Path("."),
        commit_message="tests only\n",
        paths=["tests/test_foo.py"],
        tree="abc123",
        receipt=None,
    )
    assert code == 0
    assert text == ""


def test_scoped_paths_without_a_matching_receipt_are_refused() -> None:
    code, text = evaluate(
        repo_root=Path("."),
        commit_message="fix doctor\n",
        paths=["scripts/worktree/worktree_doctor_checks.py"],
        tree="abc123",
        receipt=None,
    )
    assert code == 2
    assert "without a release-lane receipt" in text
    assert "Slice-reopen:" in text


def test_matching_receipt_is_admitted() -> None:
    code, text = evaluate(
        repo_root=Path("."),
        commit_message="fix doctor\n",
        paths=["scripts/worktree/worktree_doctor_checks.py", "docs/worktree-prepare.md"],
        tree="abc123",
        receipt=PASSING,
    )
    assert code == 0
    assert "matches the staged tree" in text


def test_receipt_for_a_different_tree_is_refused() -> None:
    assert receipt_matches_index(PASSING, "abc123") is True
    assert receipt_matches_index(PASSING, "def456") is False


def test_stale_json_receipt_is_not_a_match(tmp_path: Path) -> None:
    path = tmp_path / "last-release-receipt.json"
    path.write_text(json.dumps({"surface": "quality", "status": "fail"}), encoding="utf-8")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert receipt_matches_index(payload, "abc123") is False
