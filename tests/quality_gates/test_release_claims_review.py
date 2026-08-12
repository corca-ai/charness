"""Topology proof for the prepared-record claims-review boundary."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from .release_publish_fixtures import _release_env, _run_publish, _seed_publish_release_repo
from .release_script_loading import load_release_script

CLAIMS_REVIEW = load_release_script("publish_release_claims_review", suffix="topology")


def _record(payload: dict, prepared_commit: str, prepared_record: str) -> str:
    return json.dumps({
        "schema_version": "charness.release.claims-review.v1",
        "prepared_commit": prepared_commit,
        "release_record_path": "charness-artifacts/release/latest.md",
        "release_record_sha256": hashlib.sha256(prepared_record.encode("utf-8")).hexdigest(),
        "target_version": payload["target_version"], "tag_name": payload["tag_name"], "verdict": "pass",
        "preparer_context": "fixture-preparer", "reviewer_context": "fixture-reviewer",
    }) + "\n"


def _run(command: list[str], *, cwd: Path, check: bool = True):
    return subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)


def _source_bound_evidence(tmp_path: Path):
    repo, remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    prepared = _run_publish(repo, env, "--part", "patch", "--execute",
                            "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents")
    assert prepared.returncode == 0, prepared.stderr
    payload = json.loads(prepared.stdout)
    commit = payload["prepared_release_commit"]
    record = _run(["git", "show", f"{commit}:charness-artifacts/release/latest.md"], cwd=repo).stdout
    path = "charness-artifacts/release-review/source-claims.json"
    review = repo / path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(_record(payload, commit, record), encoding="utf-8")
    _run(["git", "add", path], cwd=repo)
    _run(["git", "commit", "-m", "Record source claims review"], cwd=repo)
    return repo, remote, bin_dir, env, payload, path


@pytest.mark.release_only
def test_claims_review_rejects_non_direct_and_merge_evidence(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    prepared_run = _run_publish(repo, _release_env(tmp_path, bin_dir), "--part", "patch", "--execute",
                                "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents")
    assert prepared_run.returncode == 0, prepared_run.stderr
    payload = json.loads(prepared_run.stdout)
    prepared_commit = payload["prepared_release_commit"]
    prepared_record = _run(["git", "show", f"{prepared_commit}:charness-artifacts/release/latest.md"], cwd=repo).stdout
    review_path = "charness-artifacts/release-review/non-direct.json"
    readme = repo / "README.md"
    original = readme.read_text(encoding="utf-8")

    # P -> X -> R restores X, so its net tree delta looks evidence-only.
    readme.write_text(original + "intermediate change\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", "Intermediary source change"], cwd=repo)
    review = repo / review_path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(_record(payload, prepared_commit, prepared_record), encoding="utf-8")
    readme.write_text(original, encoding="utf-8")
    _run(["git", "add", "README.md", review_path], cwd=repo)
    _run(["git", "commit", "-m", "Record non-direct claims review"], cwd=repo)
    evidence = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    prepared = {"commit": prepared_commit, "path": "charness-artifacts/release/latest.md",
                "sha256": hashlib.sha256(prepared_record.encode("utf-8")).hexdigest()}
    with pytest.raises(SystemExit, match="direct child"):
        CLAIMS_REVIEW.validate_claims_review(repo, prepared=prepared, evidence_commit=evidence,
                                             artifact_path=review_path, target_version=payload["target_version"],
                                             tag_name=payload["tag_name"], run=_run)

    # A merge with P as first parent is not a one-parent reviewer handoff.
    _run(["git", "checkout", "-B", "claims-side", prepared_commit], cwd=repo)
    readme.write_text(original + "merge-side change\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", "Merge-side source change"], cwd=repo)
    _run(["git", "checkout", "-B", "main", prepared_commit], cwd=repo)
    _run(["git", "merge", "--no-ff", "--no-commit", "claims-side"], cwd=repo)
    readme.write_text(original, encoding="utf-8")
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(_record(payload, prepared_commit, prepared_record), encoding="utf-8")
    _run(["git", "add", "README.md", review_path], cwd=repo)
    _run(["git", "commit", "-m", "Merge claims review"], cwd=repo)
    merge = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    with pytest.raises(SystemExit, match="direct child"):
        CLAIMS_REVIEW.validate_claims_review(repo, prepared=prepared, evidence_commit=merge,
                                             artifact_path=review_path, target_version=payload["target_version"],
                                             tag_name=payload["tag_name"], run=_run)


@pytest.mark.release_only
def test_resume_refuses_inherited_prepared_marker_before_auth_or_publish(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    prepared = _run_publish(repo, env, "--part", "patch", "--execute",
                            "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents")
    assert prepared.returncode == 0, prepared.stderr
    payload = json.loads(prepared.stdout)
    prepared_commit = payload["prepared_release_commit"]
    prepared_record = _run(["git", "show", f"{prepared_commit}:charness-artifacts/release/latest.md"], cwd=repo).stdout
    review_path = "charness-artifacts/release-review/inherited-marker.json"
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "unreviewed X\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", payload["commit_message"]], cwd=repo)
    review = repo / review_path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(_record(payload, prepared_commit, prepared_record), encoding="utf-8")
    _run(["git", "add", review_path], cwd=repo)
    _run(["git", "commit", "-m", "Record inherited-marker claims review"], cwd=repo)
    gh_log, git_log = tmp_path / "gh-log.json", tmp_path / "git-log.json"
    prior_gh = json.loads(gh_log.read_text(encoding="utf-8"))
    prior_git = json.loads(git_log.read_text(encoding="utf-8"))

    refused = _run_publish(repo, env, "--resume", "--publish-current", "--execute",
                           "--claims-review-artifact", review_path,
                           "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents")

    assert refused.returncode != 0
    assert "nothing to resume" in refused.stderr
    assert ["auth", "status"] not in json.loads(gh_log.read_text(encoding="utf-8"))[len(prior_gh):]
    new_git = json.loads(git_log.read_text(encoding="utf-8"))[len(prior_git):]
    assert ["push", "origin", "main", "v0.0.1"] not in new_git
    assert ["tag", "v0.0.1"] not in new_git


@pytest.mark.release_only
def test_prepared_record_refuses_merge_that_inherits_marker_from_second_parent(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    base = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    prepared = _run_publish(repo, _release_env(tmp_path, bin_dir), "--part", "patch", "--execute",
                            "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents")
    assert prepared.returncode == 0, prepared.stderr
    prepared_commit = json.loads(prepared.stdout)["prepared_release_commit"]
    _run(["git", "checkout", "-B", "merge-first-parent", base], cwd=repo)
    readme = repo / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "first-parent source change\n", encoding="utf-8")
    _run(["git", "add", "README.md"], cwd=repo)
    _run(["git", "commit", "-m", "First parent before prepared marker"], cwd=repo)
    _run(["git", "merge", "--no-ff", "--no-commit", prepared_commit], cwd=repo)
    _run(["git", "commit", "-m", "Merge prepared marker from second parent"], cwd=repo)
    merge = _run(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()

    assert CLAIMS_REVIEW.prepared_record(repo, commit=merge, run=_run) is None


def test_claims_review_refuses_invalid_paths_tree_and_bindings(tmp_path: Path) -> None:
    prepared = {"commit": "prepared", "path": "charness-artifacts/release/latest.md", "sha256": "record-sha"}

    def invoke(path: str | None, responses: dict[tuple[str, ...], tuple[int, str]]):
        def run(command: list[str], *, cwd: Path, check: bool = True):
            code, stdout = responses.get(tuple(command), (0, ""))
            return subprocess.CompletedProcess(command, code, stdout=stdout)
        return CLAIMS_REVIEW.validate_claims_review(
            tmp_path, prepared=prepared, evidence_commit="evidence", artifact_path=path,
            target_version="1.2.3", tag_name="v1.2.3", run=run,
        )

    with pytest.raises(SystemExit, match="normalized repo-relative"):
        invoke("../review.json", {})
    with pytest.raises(SystemExit, match="JSON record under"):
        invoke("charness-artifacts/other/review.txt", {})

    parents = ("git", "show", "-s", "--format=%P", "evidence")
    diff = ("git", "diff-tree", "--no-commit-id", "--name-only", "-r", "prepared", "evidence")
    path = "charness-artifacts/release-review/review.json"
    with pytest.raises(SystemExit, match="must change only"):
        invoke(path, {parents: (0, "prepared\n"), diff: (0, "README.md\n")})
    with pytest.raises(SystemExit, match="not committed"):
        invoke(path, {parents: (0, "prepared\n"), diff: (0, path + "\n"), ("git", "show", f"evidence:{path}"): (1, "")})
    with pytest.raises(SystemExit, match="not valid JSON"):
        invoke(path, {parents: (0, "prepared\n"), diff: (0, path + "\n"), ("git", "show", f"evidence:{path}"): (0, "{")})
    with pytest.raises(SystemExit, match="does not bind"):
        invoke(path, {parents: (0, "prepared\n"), diff: (0, path + "\n"), ("git", "show", f"evidence:{path}"): (0, "{}")})
    bound = {
        "schema_version": "charness.release.claims-review.v1", "prepared_commit": "prepared",
        "release_record_path": "charness-artifacts/release/latest.md", "release_record_sha256": "record-sha",
        "target_version": "1.2.3", "tag_name": "v1.2.3", "verdict": "pass",
        "preparer_context": "same", "reviewer_context": "same",
    }
    with pytest.raises(SystemExit, match="distinct nonempty"):
        invoke(path, {parents: (0, "prepared\n"), diff: (0, path + "\n"), ("git", "show", f"evidence:{path}"): (0, json.dumps(bound))})


@pytest.mark.release_only
def test_publish_cli_refuses_claims_artifact_without_resume(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)

    result = _run_publish(
        repo, _release_env(tmp_path, bin_dir), "--part", "patch",
        "--claims-review-artifact", "charness-artifacts/release-review/review.json",
    )

    assert result.returncode != 0
    assert "only valid with --resume --publish-current" in result.stderr


@pytest.mark.release_only
@pytest.mark.parametrize("remote_leg", ["tag", "branch"])
def test_source_resume_repairs_only_the_missing_claims_publication_leg(tmp_path: Path, remote_leg: str) -> None:
    repo, _remote, _bin_dir, env, payload, path = _source_bound_evidence(tmp_path)
    if remote_leg == "tag":
        _run(["git", "tag", payload["tag_name"], payload["prepared_release_commit"]], cwd=repo)
        _run(["git", "push", "origin", payload["tag_name"]], cwd=repo)
    else:
        _run(["git", "push", "origin", "main"], cwd=repo)
    git_log = tmp_path / "git-log.json"
    before = json.loads(git_log.read_text(encoding="utf-8"))

    resumed = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute", "--claims-review-artifact", path,
        "--critique-blocked", "synthetic-test-harness does not spawn real critique subagents",
    )

    assert resumed.returncode == 0, resumed.stderr
    new = json.loads(git_log.read_text(encoding="utf-8"))[len(before):]
    expected = ["push", "origin", "main"] if remote_leg == "tag" else ["push", "origin", payload["tag_name"]]
    assert expected in new
