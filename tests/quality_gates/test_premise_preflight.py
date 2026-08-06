from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts.premise_preflight_lib import PremiseError, run_preflight

ROOT = Path(__file__).resolve().parents[2]
SOURCE_CLI = ROOT / "scripts" / "check_premise_preflight.py"
PLUGIN_CLI = ROOT / "plugins" / "charness" / "scripts" / "check_premise_preflight.py"


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _comments_sha(comments: list[dict[str, Any]]) -> str:
    rendered = json.dumps(comments, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha(rendered.encode("utf-8"))


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _seed(tmp_path: Path) -> tuple[Path, Path, Path, dict[str, Any]]:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    (repo / "charness-artifacts" / "goals" / "example.md").write_text("# goal\n", encoding="utf-8")
    (repo / "src").mkdir()
    protected = repo / "src" / "target.txt"
    protected.write_text("original\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Premise Test")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "seed premise fixture")
    head = _git(repo, "rev-parse", "HEAD")
    comments = [{"id": 1, "body": "captured"}]
    body = "Issue body\n"
    issue = {
        "ok": True,
        "repo": "acme/charness",
        "number": 7,
        "comments_read": True,
        "comment_count": len(comments),
        "issue": {
            "number": 7,
            "body": body,
            "comments": comments,
            "state": "OPEN",
            "updatedAt": "2026-08-06T01:20:31Z",
        },
    }
    fixture_dir = repo / ".fixture"
    fixture_dir.mkdir()
    issue_path = fixture_dir / "issue-readback.json"
    issue_path.write_text(json.dumps(issue), encoding="utf-8")
    candidate = {
        "kind": "charness.premise-preflight",
        "schema_version": 1,
        "premise_id": "issue-7-slice-2",
        "repository": "acme/charness",
        "goal_path": "charness-artifacts/goals/example.md",
        "slice_id": "slice-2-premise-preflight",
        "decision_log": ".fixture/decisions.jsonl",
        "issue": {
            "number": 7,
            "expected_state": "OPEN",
            "captured": {
                "body_sha256": _sha(body.encode("utf-8")),
                "comments_sha256": _comments_sha(comments),
                "comment_count": len(comments),
                "updated_at": issue["issue"]["updatedAt"],
            },
        },
        "tree": {
            "captured_head_sha": head,
            "protected": [{"path": "src/target.txt", "sha256": _sha(b"original\n")}],
            "expected_missing": ["src/future.txt"],
        },
    }
    premise_path = fixture_dir / "premise.json"
    premise_path.write_text(json.dumps(candidate), encoding="utf-8")
    return repo, premise_path, issue_path, candidate


def _write_issue(path: Path, issue: dict[str, Any], **changes: Any) -> None:
    updated = json.loads(json.dumps(issue))
    updated["issue"].update(changes)
    path.write_text(json.dumps(updated), encoding="utf-8")


def test_valid_premise_is_accepted_and_persisted(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    result = run_preflight(repo, premise, issue)
    assert result["status"] == "accepted"
    assert result["decision"]["reason_codes"] == []
    assert result["decision"]["non_claim"].startswith("offline captured-readback")
    records = [json.loads(line) for line in (repo / ".fixture" / "decisions.jsonl").read_text().splitlines()]
    assert records[0]["attempt_id"] == result["decision"]["attempt_id"]
    assert records[0]["premise_id"] == "issue-7-slice-2"


def test_changed_issue_is_stale_and_a_refused_attempt_can_retry(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    original = json.loads(issue.read_text())
    _write_issue(issue, original, body="changed body\n")
    refused = run_preflight(repo, premise, issue)
    assert refused["status"] == "refused"
    assert refused["decision"]["reason_codes"] == ["stale_issue"]
    candidate["issue"]["captured"]["body_sha256"] = _sha(b"changed body\n")
    premise.write_text(json.dumps(candidate), encoding="utf-8")
    accepted = run_preflight(repo, premise, issue)
    assert accepted["status"] == "accepted"
    assert len((repo / ".fixture" / "decisions.jsonl").read_text().splitlines()) == 2


def test_invalid_issue_shape_does_not_append(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    data = json.loads(issue.read_text())
    del data["issue"]["comments"]
    issue.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(PremiseError, match="comments") as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "invalid_issue_readback"
    assert not (repo / ".fixture" / "decisions.jsonl").exists()


def test_same_count_different_comment_content_is_stale(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    data = json.loads(issue.read_text())
    data["issue"]["comments"][0]["body"] = "different"
    issue.write_text(json.dumps(data), encoding="utf-8")
    result = run_preflight(repo, premise, issue)
    assert result["decision"]["reason_codes"] == ["stale_issue"]


def test_issue_number_and_timestamp_types_are_refused(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    data = json.loads(issue.read_text())
    data["number"] = True
    data["issue"]["number"] = True
    issue.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(PremiseError) as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "invalid_issue_readback"

    data["number"] = 7
    data["issue"]["number"] = 7
    data["issue"]["updatedAt"] = "2026-08-06 01:20:31Z"
    issue.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(PremiseError) as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "invalid_issue_readback"


def test_worktree_and_index_drift_are_partial_repair(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    protected = repo / "src" / "target.txt"
    protected.write_text("worktree repair\n", encoding="utf-8")
    assert run_preflight(repo, premise, issue)["decision"]["reason_codes"] == ["partial_repair"]
    protected.write_text("index repair\n", encoding="utf-8")
    _git(repo, "add", "src/target.txt")
    protected.write_text("original\n", encoding="utf-8")
    result = run_preflight(repo, premise, issue)
    assert result["decision"]["reason_codes"] == ["partial_repair"]


def test_expected_missing_and_symlink_drift_are_partial_repair(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    (repo / "src" / "future.txt").symlink_to("target.txt")
    result = run_preflight(repo, premise, issue)
    assert result["decision"]["reason_codes"] == ["partial_repair"]
    assert result["decision"]["tree_observation"]["expected_missing"][0]["worktree_present"] is True


def test_staged_expected_missing_path_is_partial_repair(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    future = repo / "src" / "future.txt"
    future.write_text("staged\n", encoding="utf-8")
    _git(repo, "add", "src/future.txt")
    future.unlink()
    result = run_preflight(repo, premise, issue)
    assert result["decision"]["reason_codes"] == ["partial_repair"]
    assert result["decision"]["tree_observation"]["expected_missing"][0]["index_present"] is True


def test_staged_expected_missing_descendant_is_partial_repair(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    candidate["tree"]["expected_missing"] = ["src/future"]
    premise.write_text(json.dumps(candidate), encoding="utf-8")
    future = repo / "src" / "future"
    future.mkdir()
    (future / "repair.py").write_text("partial\n", encoding="utf-8")
    _git(repo, "add", "src/future/repair.py")
    (future / "repair.py").unlink()
    future.rmdir()
    result = run_preflight(repo, premise, issue)
    assert result["decision"]["reason_codes"] == ["partial_repair"]
    assert result["decision"]["tree_observation"]["expected_missing"][0]["index_present"] is True


def test_protected_worktree_read_failure_is_partial_repair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    original_read_bytes = Path.read_bytes

    def fail_target(path: Path) -> bytes:
        if path == repo / "src" / "target.txt":
            raise PermissionError("fixture unreadable")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", fail_target)
    result = run_preflight(repo, premise, issue)
    assert result["decision"]["reason_codes"] == ["partial_repair"]
    assert result["decision"]["tree_observation"]["protected"][0]["worktree_sha256"] is None


def test_captured_symlink_is_not_a_protected_regular_file(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    link = repo / "src" / "link.txt"
    link.symlink_to("target.txt")
    _git(repo, "add", "src/link.txt")
    _git(repo, "commit", "-qm", "add symlink")
    candidate["tree"]["captured_head_sha"] = _git(repo, "rev-parse", "HEAD")
    candidate["tree"]["protected"] = [{"path": "src/link.txt", "sha256": _sha(b"target.txt")}]
    candidate["tree"]["expected_missing"] = []
    premise.write_text(json.dumps(candidate), encoding="utf-8")
    with pytest.raises(PremiseError) as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "invalid_premise"


def test_moved_head_is_stale_tree_without_partial_repair(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    (repo / "src" / "target.txt").write_text("new commit\n", encoding="utf-8")
    _git(repo, "add", "src/target.txt")
    _git(repo, "commit", "-qm", "move tree")
    result = run_preflight(repo, premise, issue)
    assert result["decision"]["reason_codes"] == ["stale_tree"]


def test_duplicate_only_follows_an_accepted_decision(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    assert run_preflight(repo, premise, issue)["status"] == "accepted"
    duplicate = run_preflight(repo, premise, issue)
    assert duplicate["decision"]["reason_codes"] == ["duplicate_premise"]


def test_closed_issue_and_reachable_marker_are_already_shipped(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    closed = json.loads(issue.read_text())
    closed["issue"]["state"] = "CLOSED"
    issue.write_text(json.dumps(closed), encoding="utf-8")
    assert run_preflight(repo, premise, issue)["decision"]["reason_codes"] == ["already_shipped"]


def test_whitespace_padded_marker_is_not_an_exact_match(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    closed = json.loads(issue.read_text())
    (repo / "marker.txt").write_text("marker shipped\n", encoding="utf-8")
    _git(repo, "add", "marker.txt")
    _git(repo, "commit", "-qm", "padded marker\n\n Charness-Premise-ID: issue-7-slice-2 ")
    candidate["tree"]["captured_head_sha"] = _git(repo, "rev-parse", "HEAD")
    premise.write_text(json.dumps(candidate), encoding="utf-8")
    assert run_preflight(repo, premise, issue)["status"] == "accepted"

    issue.write_text(json.dumps({**closed, "issue": {**closed["issue"], "state": "OPEN"}}), encoding="utf-8")
    (repo / "marker.txt").write_text("marker\n", encoding="utf-8")
    _git(repo, "add", "marker.txt")
    _git(repo, "commit", "-qm", "ship marker\n\nCharness-Premise-ID: issue-7-slice-2")
    candidate["tree"]["captured_head_sha"] = _git(repo, "rev-parse", "HEAD")
    premise.write_text(json.dumps(candidate), encoding="utf-8")
    assert run_preflight(repo, premise, issue)["decision"]["reason_codes"] == ["already_shipped", "duplicate_premise"]


def test_malformed_decision_history_does_not_append(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    log = repo / ".fixture" / "decisions.jsonl"
    log.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(PremiseError) as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "invalid_decision_history"
    assert log.read_text() == "not-json\n"


def test_incomplete_json_decision_history_does_not_block_or_append(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    record = {
        "kind": "charness.premise-decision",
        "schema_version": 1,
        "status": "accepted",
        "premise_id": candidate["premise_id"],
        "attempt_id": "0" * 32,
    }
    log = repo / ".fixture" / "decisions.jsonl"
    log.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(PremiseError) as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "invalid_decision_history"
    assert len(log.read_text().splitlines()) == 1


def test_decision_log_parent_failure_is_structured(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    parent = repo / ".fixture" / "not-a-directory"
    parent.write_text("file\n", encoding="utf-8")
    candidate["decision_log"] = ".fixture/not-a-directory/decisions.jsonl"
    premise.write_text(json.dumps(candidate), encoding="utf-8")
    with pytest.raises(PremiseError) as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "decision_log_write_failed"


def test_dangling_decision_log_symlink_is_structured(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    target = repo / ".fixture" / "future-decisions.jsonl"
    link = repo / ".fixture" / "decisions-link.jsonl"
    link.symlink_to(target.name)
    candidate["decision_log"] = ".fixture/decisions-link.jsonl"
    premise.write_text(json.dumps(candidate), encoding="utf-8")
    with pytest.raises(PremiseError) as caught:
        run_preflight(repo, premise, issue)
    assert caught.value.code == "invalid_decision_history"
    assert not target.exists()


@pytest.mark.parametrize("cli_path", [SOURCE_CLI, PLUGIN_CLI])
def test_cli_emits_shell_free_json_for_valid_fixture(tmp_path: Path, cli_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    result = subprocess.run(
        ["python3", str(cli_path), "--repo-root", str(repo), "--premise", str(premise), "--issue-readback", str(issue), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "accepted"
    assert payload["decision"]["repository"] == "acme/charness"
    assert result.stderr == ""


def test_cli_returns_exit_two_for_invalid_issue_readback(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    data = json.loads(issue.read_text())
    del data["issue"]["comments"]
    issue.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run(
        ["python3", str(SOURCE_CLI), "--repo-root", str(repo), "--premise", str(premise), "--issue-readback", str(issue), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["error"]["code"] == "invalid_issue_readback"
