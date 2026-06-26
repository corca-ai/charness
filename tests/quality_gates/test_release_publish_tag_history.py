from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from tests.quality_gates.release_publish_fixtures import _seed_publish_release_repo
from tests.quality_gates.test_release_publish_real_host_delta import (
    _publish_env,
    _seed_publish_current_previous_tag_delta,
    _write_base_ref_failing_git,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_release_module(name: str):
    path = REPO_ROOT / f"skills/public/release/scripts/{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_helpers = _load_release_module("publish_release_helpers")


def _assert_tag_discovery_failure(
    tmp_path: Path,
    failing_command: list[str],
    *,
    source: str,
    command: str,
    exit_code: int,
    stderr_marker: str,
) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if command == failing_command:
            return subprocess.CompletedProcess(command, exit_code, "", f"{stderr_marker}\n")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(_helpers, "run", fake_run)
    try:
        with pytest.raises(SystemExit) as excinfo:
            _helpers._release_tag_versions(tmp_path, remote="origin")
    finally:
        monkeypatch.undo()

    message = str(excinfo.value)
    assert "release tag discovery failed while resolving previous release version" in message
    assert f"source: {source}" in message
    assert f"command: {command}" in message
    assert f"exit_code: {exit_code}" in message
    assert stderr_marker in message
    assert failing_command in commands


def test_publish_current_fails_closed_when_local_release_tag_discovery_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_publish_current_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    before_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_TAG_LIST_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for legacy release publish tag-history test",
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
    assert "source: local tags" in result.stderr
    assert "command: git tag --list v[0-9]*.[0-9]*.[0-9]*" in result.stderr
    assert "exit_code: 45" in result.stderr
    assert "forced local tag list failure" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.1"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
        == before_head
    )
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


def test_publish_current_fails_closed_when_remote_release_tag_discovery_fails(tmp_path: Path) -> None:
    _assert_tag_discovery_failure(
        tmp_path,
        ["git", "ls-remote", "--tags", "origin", "refs/tags/v[0-9]*"],
        source="remote tags",
        command="git ls-remote --tags origin refs/tags/v[0-9]*",
        exit_code=46,
        stderr_marker="forced remote tag history failure",
    )


def test_publish_current_subprocess_fails_when_remote_release_tag_discovery_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_publish_current_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_LS_REMOTE_TAG_HISTORY_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for legacy release publish tag-history test",
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
    assert "release tag discovery failed while resolving previous release version" in result.stderr
    assert "source: remote tags" in result.stderr
    assert "command: git ls-remote --tags origin refs/tags/v[0-9]*" in result.stderr
    assert "exit_code: 46" in result.stderr
    assert "forced remote tag history failure" in result.stderr
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["ls-remote", "--tags", "origin", "refs/tags/v[0-9]*"] in git_log


def test_publish_current_allows_no_previous_release_tags_after_successful_discovery(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _publish_env(tmp_path, bin_dir)

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for legacy release publish tag-history test",
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
