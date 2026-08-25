"""End-to-end partial-publication recovery fixtures for the release resume lane."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from .release_publish_fixtures import (
    _release_env,
    _run_publish,
    _seed_publish_release_repo,
    _simulate_partial_publish,
)

CRITIQUE_BLOCKED = "synthetic-test-harness does not spawn real critique subagents"


def test_resume_continues_partial_publish_idempotently(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _simulate_partial_publish(repo)
    env = _release_env(tmp_path, bin_dir)

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )

    assert result.returncode == 0, result.stderr
    assert "nothing to commit" not in result.stderr
    assert "already exists" not in result.stderr

    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    pushes = [entry for entry in git_log if entry[:1] == ["push"]]
    assert any("v0.0.0" in entry for entry in pushes), pushes
    assert ["tag", "v0.0.0"] not in git_log
    assert not any(entry[:1] == ["commit"] and "Release demo 0.0.0" in entry for entry in git_log)

    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert any(entry[:2] == ["release", "create"] for entry in gh_log), gh_log

    payload = yaml.safe_load(result.stdout)
    runtime_labels = {entry["label"] for entry in payload["release_runtime"]}
    assert "quality_command" in runtime_labels
    assert "push_create_verify_release" in runtime_labels
    assert "post_publish_install_refresh" in runtime_labels


def test_resume_recreates_missing_local_tag_after_revalidation(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _simulate_partial_publish(repo, create_tag=False)
    release_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    env = _release_env(tmp_path, bin_dir)

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )

    assert result.returncode == 0, result.stderr
    tag_head = subprocess.run(
        ["git", "rev-list", "-n", "1", "v0.0.0"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout.strip()
    assert tag_head == release_head
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["tag", "v0.0.0", release_head] in git_log


def test_resume_dry_run_describes_revalidation_without_mutating(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _simulate_partial_publish(repo)
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()

    result = _run_publish(
        repo,
        _release_env(tmp_path, bin_dir),
        "--resume", "--publish-current", "--critique-blocked", CRITIQUE_BLOCKED,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["resume"].startswith("dry-run: would re-validate gates")
    assert subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip() == head_before
