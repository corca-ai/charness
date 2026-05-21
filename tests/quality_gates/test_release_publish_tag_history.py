from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.quality_gates.test_release_publish import _seed_publish_release_repo
from tests.quality_gates.test_release_publish_real_host_delta import (
    _publish_env,
    _seed_publish_current_previous_tag_delta,
    _write_base_ref_failing_git,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _assert_publish_current_tag_discovery_failure(
    repo: Path,
    tmp_path: Path,
    bin_dir: Path,
    env_name: str,
    *,
    source: str,
    command: str,
    exit_code: int,
    stderr_marker: str,
) -> None:
    _write_base_ref_failing_git(bin_dir)
    before_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env[env_name] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--publish-current",
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "release tag discovery failed while resolving previous release version" in result.stderr
    assert f"source: {source}" in result.stderr
    assert f"command: {command}" in result.stderr
    assert f"exit_code: {exit_code}" in result.stderr
    assert stderr_marker in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.1"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == before_head
    assert subprocess.run(
        ["git", "tag", "--list", "v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log_path = tmp_path / "gh-log.json"
    gh_log = json.loads(gh_log_path.read_text(encoding="utf-8")) if gh_log_path.exists() else []
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_current_fails_closed_when_local_release_tag_discovery_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_publish_current_previous_tag_delta(tmp_path)

    _assert_publish_current_tag_discovery_failure(
        repo,
        tmp_path,
        bin_dir,
        "FAKE_GIT_TAG_LIST_FAIL",
        source="local tags",
        command="git tag --list v[0-9]*.[0-9]*.[0-9]*",
        exit_code=45,
        stderr_marker="forced local tag list failure",
    )


def test_publish_current_fails_closed_when_remote_release_tag_discovery_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_publish_current_previous_tag_delta(tmp_path)

    _assert_publish_current_tag_discovery_failure(
        repo,
        tmp_path,
        bin_dir,
        "FAKE_GIT_LS_REMOTE_TAG_HISTORY_FAIL",
        source="remote tags",
        command="git ls-remote --tags origin refs/tags/v[0-9]*",
        exit_code=46,
        stderr_marker="forced remote tag history failure",
    )


def test_publish_current_allows_no_previous_release_tags_after_successful_discovery(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _publish_env(tmp_path, bin_dir)

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--publish-current",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["execute"] is False
    assert payload["previous_version"] == "0.0.0"
    assert payload["target_version"] == "0.0.0"
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"] in git_log
    assert ["ls-remote", "--tags", "origin", "refs/tags/v[0-9]*"] in git_log
