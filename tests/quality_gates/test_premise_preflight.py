from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

import scripts.premise_decision_history as premise_history
import scripts.premise_git_snapshot as premise_git
import scripts.premise_preflight_lib as premise_lib
import scripts.premise_tree_observation as premise_tree
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


def _build_premise_preflight_seed(staging: Path) -> None:
    repo = staging / "repo"
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


def premise_preflight_seed(*, cache_get_or_build=None) -> Path:
    """Return one source-bound immutable Git seed for premise-preflight tests."""
    if cache_get_or_build is None:
        from tests.seed_cache import get_or_build

        cache_get_or_build = get_or_build
    return cache_get_or_build(
        "premise-preflight-repo-seed", _build_premise_preflight_seed
    ) / "repo"


def _seed(tmp_path: Path) -> tuple[Path, Path, Path, dict[str, Any]]:
    seed = premise_preflight_seed()
    repo = tmp_path / "repo"
    shutil.copytree(seed, repo)
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


def _tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_premise_preflight_seed_is_never_mutated_by_a_test_clone(tmp_path: Path) -> None:
    seed = premise_preflight_seed()
    before_seed = _tree_snapshot(seed)
    repo, _, _, _ = _seed(tmp_path)

    (repo / "src" / "target.txt").write_text("clone-only change\n", encoding="utf-8")
    _git(repo, "add", "src/target.txt")
    _git(repo, "commit", "-qm", "mutate only the disposable clone")

    assert _tree_snapshot(seed) == before_seed


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
def test_cli_emits_shell_free_payload_for_valid_fixture(tmp_path: Path, cli_path: Path) -> None:
    """The payload-shape half: one machine-parseable document on stdout, nothing on the
    side channel. Output is YAML since the `--json` removal; YAML is a JSON superset, so
    this stays the same shell-free/parse-it-don't-grep-it claim it always was."""
    repo, premise, issue, _ = _seed(tmp_path)
    result = subprocess.run(
        ["python3", str(cli_path), "--repo-root", str(repo), "--premise", str(premise), "--issue-readback", str(issue)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "accepted"
    assert payload["decision"]["repository"] == "acme/charness"
    assert result.stderr == ""


def test_cli_rejects_a_json_flag(tmp_path: Path) -> None:
    """`--json` was removed repo-wide, not kept as a no-op: a caller still passing it is
    told so (argparse exit 2) rather than silently getting a different contract."""
    repo, premise, issue, _ = _seed(tmp_path)
    result = subprocess.run(
        ["python3", str(SOURCE_CLI), "--repo-root", str(repo), "--premise", str(premise), "--issue-readback", str(issue), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "unrecognized arguments: --json" in result.stderr


def test_cli_returns_exit_two_for_invalid_issue_readback(tmp_path: Path) -> None:
    repo, premise, issue, _ = _seed(tmp_path)
    data = json.loads(issue.read_text())
    del data["issue"]["comments"]
    issue.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run(
        ["python3", str(SOURCE_CLI), "--repo-root", str(repo), "--premise", str(premise), "--issue-readback", str(issue)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert yaml.safe_load(result.stdout)["error"]["code"] == "invalid_issue_readback"


@pytest.mark.parametrize("cli_path", [SOURCE_CLI, PLUGIN_CLI])
def test_cli_reports_accepted_and_refused_fixtures(tmp_path: Path, cli_path: Path) -> None:
    """The verdict/exit-code half, run against BOTH the source CLI and the exported
    mirror: an accepted run names the decision log it wrote, and a refused run names the
    refusal instead of exiting 2 with a payload a reader could mistake for a pass."""
    repo, premise, issue, _ = _seed(tmp_path)
    accepted = subprocess.run(
        ["python3", str(cli_path), "--repo-root", str(repo), "--premise", str(premise), "--issue-readback", str(issue)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert accepted.returncode == 0
    accepted_payload = yaml.safe_load(accepted.stdout)
    assert accepted_payload["status"] == "accepted"
    # The deleted ACCEPTED line carried the decision-log path; it has to stay reachable.
    assert accepted_payload["decision_log"] == ".fixture/decisions.jsonl"

    data = json.loads(issue.read_text())
    del data["issue"]["comments"]
    issue.write_text(json.dumps(data), encoding="utf-8")
    refused = subprocess.run(
        ["python3", str(cli_path), "--repo-root", str(repo), "--premise", str(premise), "--issue-readback", str(issue)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert refused.returncode == 2
    refused_payload = yaml.safe_load(refused.stdout)
    assert refused_payload["status"] == "refused"
    # The deleted REFUSED line carried the detail; it is on the payload now, and the
    # refusal is fully on the structured channel rather than split across stderr.
    assert refused_payload["error"]["code"] == "invalid_issue_readback"
    assert refused.stderr == ""


def _raises(code: str, function: Any, *args: Any, **kwargs: Any) -> None:
    with pytest.raises(PremiseError) as caught:
        function(*args, **kwargs)
    assert caught.value.code == code


def test_premise_scalar_and_repository_error_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _raises("invalid_premise", premise_lib._mapping, [], "field")
    _raises("invalid_premise", premise_lib._string, "", "field")
    _raises("invalid_premise", premise_lib._integer, -1, "field")
    _raises("invalid_premise", premise_lib._hash, "bad", "field", premise_lib._SHA256_RE)
    _raises("invalid_premise", premise_lib._timestamp, "", "field")
    _raises("invalid_premise", premise_lib._timestamp, "2026-99-99T01:02:03Z", "field")
    _raises("unsafe_path", premise_lib._relative_path, "../outside", "field")
    _raises("unsafe_path", premise_lib._repo_path, tmp_path, "../outside", "field")

    original_error = premise_lib._error
    monkeypatch.setattr(premise_lib, "_error", lambda *_args: None)
    with pytest.raises(AssertionError):
        premise_lib._relative_path("../outside", "field")
    monkeypatch.setattr(premise_lib, "_error", original_error)
    class NaiveDateTime:
        @classmethod
        def fromisoformat(cls, _: str) -> Any:
            return type("Naive", (), {"tzinfo": None})()
    original_datetime = premise_history._datetime.datetime
    monkeypatch.setattr(premise_history._datetime, "datetime", NaiveDateTime)
    _raises("invalid_premise", premise_lib._timestamp, "2026-08-06T01:02:03Z", "field")
    monkeypatch.setattr(premise_history._datetime, "datetime", original_datetime)

    missing = tmp_path / "missing.json"
    _raises("missing_input", premise_lib._load_json, tmp_path, missing, "field")
    _raises("unsafe_path", premise_lib._load_json, tmp_path, tmp_path.parent / "outside.json", "field")
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    _raises("invalid_json", premise_lib._load_json, tmp_path, invalid, "field")

    monkeypatch.setattr(
        premise_lib,
        "_git",
        lambda *_args: subprocess.CompletedProcess([], 1, stdout="", stderr="failed"),
    )
    _raises("invalid_git_state", premise_lib._current_head, tmp_path)
    monkeypatch.setattr(
        premise_lib,
        "_git",
        lambda *_args: subprocess.CompletedProcess([], 0, stdout="not-a-sha", stderr=""),
    )
    _raises("invalid_git_state", premise_lib._current_head, tmp_path)


def test_premise_git_batch_parser_preserves_binary_blob_frames() -> None:
    object_id = b"a" * 40
    payload = object_id + b" blob 4\na\nb\n\nmissing-expression missing\n"

    assert premise_git._parse_batch(payload, 2) == [("blob", b"a\nb\n"), None]
    assert premise_git._parse_batch(payload + b"trailing", 2) is None


def test_premise_tree_observation_reports_an_unreadable_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        premise_tree,
        "_git_bytes",
        lambda *_args: subprocess.CompletedProcess([], 1, stdout=b"", stderr=b"failed"),
    )

    with pytest.raises(premise_tree.CurrentTreeInspectionError):
        premise_tree._index_paths(tmp_path)


def test_premise_candidate_and_issue_error_branches(tmp_path: Path) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    mutations = [
        (lambda value: value.update(premise_id="!"), "invalid_premise"),
        (lambda value: value.update(repository="invalid"), "invalid_premise"),
        (lambda value: value.update(goal_path="missing.md"), "invalid_premise"),
        (lambda value: value.update(slice_id="!"), "invalid_premise"),
    ]
    for mutate, code in mutations:
        data = json.loads(json.dumps(candidate))
        mutate(data)
        _raises(code, premise_lib._validate_candidate_identity, repo, data)

    data = json.loads(json.dumps(candidate))
    data["issue"]["number"] = 0
    _raises("invalid_premise", premise_lib._validate_candidate_identity, repo, data)
    data = json.loads(json.dumps(candidate))
    data["issue"]["expected_state"] = "CLOSED"
    _raises("invalid_premise", premise_lib._validate_candidate_identity, repo, data)

    tree = json.loads(json.dumps(candidate["tree"]))
    tree["protected"] = []
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["captured_head_sha"] = "0" * 40
    _raises("invalid_git_state", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["protected"][0]["path"] = "src/missing.txt"
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["protected"].append(tree["protected"][0].copy())
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["protected"][0]["sha256"] = "0" * 64
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["expected_missing"] = "missing"
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["expected_missing"] = [tree["protected"][0]["path"]]
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["expected_missing"] = ["src/future.txt", "src/future.txt"]
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    tree = json.loads(json.dumps(candidate["tree"]))
    tree["expected_missing"] = ["charness-artifacts/goals/example.md"]
    _raises("invalid_premise", premise_lib._validate_candidate_tree, repo, tree)
    invalid_kind = json.loads(json.dumps(candidate))
    invalid_kind["kind"] = "wrong"
    _raises("invalid_premise", premise_lib._validate_candidate, repo, invalid_kind)

    normalized = premise_lib._validate_candidate(repo, candidate)
    valid_issue = json.loads(issue.read_text())
    issue_mutations = [
        (lambda value: value.update(ok=False), {"repository": "acme/charness", "issue_number": 7}, "invalid_issue_readback"),
        (lambda value: value.update(repo="other/repo"), normalized, "invalid_issue_readback"),
        (lambda value: value.update(issue=[]), normalized, "invalid_issue_readback"),
        (lambda value: value.update(number=True), {"repository": "acme/charness", "issue_number": True}, "invalid_issue_readback"),
    ]
    for mutate, issue_candidate, code in issue_mutations:
        data = json.loads(json.dumps(valid_issue))
        mutate(data)
        _raises(code, premise_lib._validate_issue, repo, data, issue_candidate)
    data = json.loads(json.dumps(valid_issue))
    data["issue"]["number"] = True
    _raises("invalid_issue_readback", premise_lib._validate_issue, repo, data, normalized)
    data = json.loads(json.dumps(valid_issue))
    data["issue"]["number"] = 8
    _raises("invalid_issue_readback", premise_lib._validate_issue, repo, data, normalized)
    data = json.loads(json.dumps(valid_issue))
    data["issue"]["body"] = 3
    _raises("invalid_issue_readback", premise_lib._validate_issue, repo, data, normalized)
    data = json.loads(json.dumps(valid_issue))
    data["issue"]["body"] = None
    _raises("invalid_issue_readback", premise_lib._validate_issue, repo, data, normalized)
    data = json.loads(json.dumps(valid_issue))
    data["comment_count"] = 2
    _raises("invalid_issue_readback", premise_lib._validate_issue, repo, data, normalized)
    data = json.loads(json.dumps(valid_issue))
    data["issue"]["state"] = "BROKEN"
    _raises("invalid_issue_readback", premise_lib._validate_issue, repo, data, normalized)


def test_premise_history_and_write_error_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, premise, issue, candidate = _seed(tmp_path)
    normalized = premise_lib._validate_candidate(repo, candidate)
    issue_data = premise_lib._validate_issue(repo, json.loads(issue.read_text()), normalized)
    observations, _ = premise_lib._protected_observations(repo, normalized)
    record = premise_history._record(repo, normalized, issue_data, normalized["captured_head_sha"], observations, [], status="accepted")

    _raises("invalid_decision_history", premise_history._history_hash, "bad", "field")
    _raises("invalid_decision_history", premise_history._history_git_sha, "bad", "field")
    _raises("invalid_decision_history", premise_history._history_path, "../bad", "field")
    for mutation in (
        lambda value: value.update(issue_observation=None),
        lambda value: value.update(issue_observation={"number": 0}),
        lambda value: value.update(issue_observation={"number": 1, "state": "BAD"}),
    ):
        value = json.loads(json.dumps(record))
        mutation(value)
        _raises("invalid_decision_history", premise_history._history_observation, value, "record")
    value = json.loads(json.dumps(record))
    value["issue_observation"]["comment_count"] = True
    _raises("invalid_decision_history", premise_history._history_observation, value, "record")
    value = json.loads(json.dumps(record))
    value["tree_observation"] = None
    _raises("invalid_decision_history", premise_history._history_observation, value, "record")
    value = json.loads(json.dumps(record))
    value["tree_observation"]["captured_head_sha"] = "bad"
    _raises("invalid_decision_history", premise_history._history_observation, value, "record")
    value = json.loads(json.dumps(record))
    value["tree_observation"]["protected"] = None
    _raises("invalid_decision_history", premise_history._history_observation, value, "record")
    value = json.loads(json.dumps(record))
    value["tree_observation"]["protected"] = [None]
    _raises("invalid_decision_history", premise_history._history_observation, value, "record")
    value = json.loads(json.dumps(record))
    value["tree_observation"]["expected_missing"] = [None]
    _raises("invalid_decision_history", premise_history._history_observation, value, "record")
    value = json.loads(json.dumps(record))
    value["tree_observation"]["expected_missing"] = [{"path": "src/future.txt"}]
    _raises("invalid_decision_history", premise_history._history_observation, value, "record")

    record_mutations = [
        (None, "invalid_decision_history"),
        ({**record, "kind": "bad"}, "invalid_decision_history"),
        ({**record, "status": "unknown"}, "invalid_decision_history"),
        ({**record, "premise_id": "!"}, "invalid_decision_history"),
        ({**record, "attempt_id": "bad"}, "invalid_decision_history"),
        ({**record, "repository": "bad"}, "invalid_decision_history"),
        ({**record, "goal_path": "../bad"}, "invalid_decision_history"),
        ({**record, "slice_id": "!"}, "invalid_decision_history"),
        ({**record, "reason_codes": ["bad"]}, "invalid_decision_history"),
        ({**record, "reason_codes": ["stale_tree", "already_shipped"]}, "invalid_decision_history"),
        ({**record, "reasons": None}, "invalid_decision_history"),
        ({**record, "status": "refused", "reason_codes": ["stale_tree"], "reasons": [{}]}, "invalid_decision_history"),
        ({**record, "status": "refused", "reason_codes": [], "reasons": []}, "invalid_decision_history"),
        ({**record, "non_claim": "changed"}, "invalid_decision_history"),
    ]
    for value, code in record_mutations:
        _raises(code, premise_history._validate_decision_record, repo, value, 0)

    log = repo / ".fixture" / "history"
    log.mkdir()
    _raises("invalid_decision_history", premise_history._read_decisions, repo, ".fixture/history")
    log.rmdir()
    log.write_text("\n", encoding="utf-8")
    _raises("invalid_decision_history", premise_history._read_decisions, repo, ".fixture/history")
    monkeypatch.setattr(
        premise_history.Path,
        "read_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("unreadable")),
    )
    _raises("invalid_decision_history", premise_history._read_decisions, repo, ".fixture/history")
    monkeypatch.undo()
    monkeypatch.setattr(
        premise_lib,
        "_git",
        lambda *_args: subprocess.CompletedProcess([], 1, stdout="", stderr="failed"),
    )
    _raises("invalid_git_state", premise_lib._marker_seen, repo, "issue-7-slice-2")

    original_error = premise_history._error
    monkeypatch.setattr(premise_history, "_error", lambda *_args: None)
    with pytest.raises(AssertionError):
        premise_history._history_path("../bad", "field")
    monkeypatch.setattr(premise_history, "_error", original_error)

    missing_candidate = {"protected": [{"path": "src/missing.txt", "sha256": "0" * 64}], "expected_missing": []}
    _, drift = premise_lib._protected_observations(repo, missing_candidate)
    assert drift is True
    link = repo / ".fixture" / "append-link.jsonl"
    link.symlink_to("future.jsonl")
    _raises("decision_log_write_failed", premise_history._append_decision, repo, ".fixture/append-link.jsonl", record)
    link.unlink()
    directory = repo / ".fixture" / "append-dir.jsonl"
    directory.mkdir()
    _raises("decision_log_write_failed", premise_history._append_decision, repo, ".fixture/append-dir.jsonl", record)
