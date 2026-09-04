"""Commit-msg release-lane receipt check."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.hooks import check_release_lane_receipt as receipt_mod
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


def test_evaluate_refuses_when_paths_or_tree_cannot_be_read() -> None:
    code, text = evaluate(
        repo_root=Path("."),
        commit_message="touch scripts\n",
        paths=None,
        tree="abc123",
        receipt=None,
    )
    assert code == 2
    assert "could not read staged paths" in text
    code, text = evaluate(
        repo_root=Path("."),
        commit_message="touch scripts\n",
        paths=["scripts/foo.py"],
        tree=None,
        receipt=None,
    )
    assert code == 2
    assert "could not read the staged tree" in text


def test_load_receipt_returns_none_for_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "last-release-receipt.json"
    path.write_text("{not json", encoding="utf-8")
    assert receipt_mod.load_receipt(path) is None
    assert receipt_mod.load_receipt(tmp_path / "missing.json") is None


def test_main_reads_the_commit_message_and_git_index(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text("docs only\n\nSlice-reopen: coverage\n", encoding="utf-8")
    monkeypatch.setattr(receipt_mod, "staged_paths", lambda _root: ["docs/foo.md"])
    monkeypatch.setattr(receipt_mod, "index_tree", lambda _root: "abc123")
    monkeypatch.setattr(receipt_mod, "load_receipt", lambda _path: None)
    assert receipt_mod.main(["--repo-root", str(repo), "--commit-msg-file", str(msg)]) == 0


def test_main_returns_two_when_the_commit_message_is_unreadable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    missing = tmp_path / "no-such-msg"
    assert receipt_mod.main(["--repo-root", str(repo), "--commit-msg-file", str(missing)]) == 2


def test_git_helpers_return_none_on_nonzero(monkeypatch, tmp_path: Path) -> None:
    class Result:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(receipt_mod, "run_process", lambda *args, **kwargs: Result())
    assert receipt_mod._git(tmp_path, "status") is None
    assert receipt_mod.staged_paths(tmp_path) is None
    assert receipt_mod.index_tree(tmp_path) is None
    assert receipt_mod.last_receipt_path(tmp_path) == tmp_path / receipt_mod.LAST_RECEIPT_RELATIVE
