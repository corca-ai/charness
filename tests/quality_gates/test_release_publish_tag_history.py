from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.release_publish_fixtures import (
    _install_fake_git,
    _seed_publish_release_repo,
)
from tests.quality_gates.seeding_support import git, load_module

REPO_ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.boundary_contract(
    reason="observe release publish's real git tag-history child commands and fail-closed release-delta behavior"
)


def _load_release_module(name: str):
    path = REPO_ROOT / f"skills/public/release/scripts/{name}.py"
    return load_module(name, path)


_helpers = _load_release_module("publish_release_helpers")


def _publish_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
    return env


def _write_base_ref_failing_git(bin_dir: Path) -> None:
    _install_fake_git(bin_dir)


def _seed_missing_local_previous_tag_delta(tmp_path: Path) -> tuple[Path, Path]:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    git(repo, "tag", "v0.0.0")
    git(repo, "push", "origin", "v0.0.0")
    git(repo, "tag", "-d", "v0.0.0")
    (repo / "README.md").write_text(
        "# Demo\n\nChanged after the previous release.\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "Change release surface")
    git(repo, "push", "origin", "main")
    return repo, bin_dir


def _seed_publish_current_previous_tag_delta(tmp_path: Path) -> tuple[Path, Path]:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    git(repo, "tag", "v0.0.0")
    git(repo, "push", "origin", "v0.0.0")
    (repo / "README.md").write_text("# Demo\n\nChanged before publish-current.\n", encoding="utf-8")
    subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/bump_version.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "Prepare current release")
    git(repo, "push", "origin", "main")
    return repo, bin_dir


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

    def fake_run(
        command: list[str], *, cwd: Path, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
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


def test_publish_current_fails_closed_when_local_release_tag_discovery_fails(
    tmp_path: Path,
) -> None:
    _assert_tag_discovery_failure(
        tmp_path,
        ["git", "tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"],
        source="local tags",
        command="git tag --list v[0-9]*.[0-9]*.[0-9]*",
        exit_code=45,
        stderr_marker="forced local tag list failure",
    )


def test_publish_current_fails_closed_when_remote_release_tag_discovery_fails(
    tmp_path: Path,
) -> None:
    _assert_tag_discovery_failure(
        tmp_path,
        ["git", "ls-remote", "--tags", "origin", "refs/tags/v[0-9]*"],
        source="remote tags",
        command="git ls-remote --tags origin refs/tags/v[0-9]*",
        exit_code=46,
        stderr_marker="forced remote tag history failure",
    )


def test_publish_current_subprocess_fails_when_remote_release_tag_discovery_fails(
    tmp_path: Path,
) -> None:
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


def test_publish_current_allows_no_previous_release_tags_after_successful_discovery(
    tmp_path: Path,
) -> None:
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
    payload = yaml.safe_load(result.stdout)
    assert payload["execute"] is False
    assert payload["previous_version"] == "0.0.0"
    assert payload["target_version"] == "0.0.0"
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"] in git_log
    assert ["ls-remote", "--tags", "origin", "refs/tags/v[0-9]*"] in git_log


@pytest.mark.release_only
def test_publish_release_fetches_missing_previous_tag_for_release_delta(tmp_path: Path) -> None:
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
    env = _publish_env(tmp_path, bin_dir)
    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for release delta test",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target_version"] == "0.0.1"
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"] in git_log


@pytest.mark.release_only
def test_publish_release_fails_closed_when_previous_tag_fetch_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    before_head = git(repo, "rev-parse", "HEAD")
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_FETCH_TAG_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for release delta test",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "release base ref fetch failed while computing unreleased paths" in result.stderr
    assert "tag_ref: refs/tags/v0.0.0" in result.stderr
    assert "command: git fetch --quiet origin refs/tags/v0.0.0:refs/tags/v0.0.0" in result.stderr
    assert "exit_code: 43" in result.stderr
    assert "forced tag fetch failure" in result.stderr
    assert (
        json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"]
        == "0.0.0"
    )
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert git(repo, "rev-parse", "HEAD") == before_head
    assert git(repo, "tag", "--list", "v0.0.1") == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log_path = tmp_path / "gh-log.json"
    gh_log = json.loads(gh_log_path.read_text(encoding="utf-8")) if gh_log_path.exists() else []
    fetch_command = ["fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"]
    fetch_index = git_log.index(fetch_command)
    assert ["ls-remote", "--tags", "origin", "refs/tags/v0.0.0"] in git_log
    assert fetch_command in git_log
    assert ["diff", "--name-only", "origin/main..HEAD"] not in git_log[fetch_index + 1 :]
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_fails_closed_when_previous_tag_fetch_fails(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def fake_run(
        command: list[str], *, cwd: Path, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 1, "", "")
        if command[:3] == ["git", "ls-remote", "--tags"]:
            return subprocess.CompletedProcess(command, 0, "abc refs/tags/v0.0.0\n", "")
        if command[:3] == ["git", "fetch", "--quiet"]:
            return subprocess.CompletedProcess(command, 43, "", "forced tag fetch failure\n")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(_helpers, "run", fake_run)
    try:
        with pytest.raises(SystemExit) as excinfo:
            _helpers.unreleased_paths(
                tmp_path, remote="origin", branch="main", previous_version="0.0.0"
            )
    finally:
        monkeypatch.undo()

    message = str(excinfo.value)
    assert "release base ref fetch failed while computing unreleased paths" in message
    assert "forced tag fetch failure" in message
    fetch_command = ["git", "fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"]
    assert fetch_command in commands
    assert not any(
        command[:3] == ["git", "diff", "--name-only"]
        for command in commands[commands.index(fetch_command) + 1 :]
    )


@pytest.mark.release_only
def test_publish_release_fails_closed_when_previous_tag_lookup_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    before_head = git(repo, "rev-parse", "HEAD")
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_LS_REMOTE_PREVIOUS_TAG_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for release delta test",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "release base ref lookup failed while computing unreleased paths" in result.stderr
    assert "tag_ref: refs/tags/v0.0.0" in result.stderr
    assert "command: git ls-remote --tags origin refs/tags/v0.0.0" in result.stderr
    assert "exit_code: 44" in result.stderr
    assert "forced previous tag lookup failure" in result.stderr
    assert (
        json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"]
        == "0.0.0"
    )
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert git(repo, "rev-parse", "HEAD") == before_head
    assert git(repo, "tag", "--list", "v0.0.1") == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log_path = tmp_path / "gh-log.json"
    gh_log = json.loads(gh_log_path.read_text(encoding="utf-8")) if gh_log_path.exists() else []
    lookup_command = ["ls-remote", "--tags", "origin", "refs/tags/v0.0.0"]
    lookup_index = git_log.index(lookup_command)
    assert lookup_command in git_log
    assert ["fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"] not in git_log
    assert ["diff", "--name-only", "origin/main..HEAD"] not in git_log[lookup_index + 1 :]
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_fails_closed_when_previous_tag_lookup_fails(
    tmp_path: Path,
) -> None:
    commands: list[list[str]] = []

    def fake_run(
        command: list[str], *, cwd: Path, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 1, "", "")
        if command[:3] == ["git", "ls-remote", "--tags"]:
            return subprocess.CompletedProcess(
                command, 44, "", "forced previous tag lookup failure\n"
            )
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(_helpers, "run", fake_run)
    try:
        with pytest.raises(SystemExit) as excinfo:
            _helpers.unreleased_paths(
                tmp_path, remote="origin", branch="main", previous_version="0.0.0"
            )
    finally:
        monkeypatch.undo()

    message = str(excinfo.value)
    assert "release base ref lookup failed while computing unreleased paths" in message
    assert "forced previous tag lookup failure" in message
    assert ["git", "ls-remote", "--tags", "origin", "refs/tags/v0.0.0"] in commands
    assert not any(command[:3] == ["git", "fetch", "--quiet"] for command in commands)
    assert not any(command[:3] == ["git", "diff", "--name-only"] for command in commands)


@pytest.mark.release_only
def test_publish_release_fails_closed_when_release_diff_fails(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    (repo / "README.md").write_text("# Demo\n\nRelease delta setup.\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "Prepare release delta")
    before_head = git(repo, "rev-parse", "HEAD")
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_DIFF_NAME_ONLY_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for release delta test",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "release diff failed while computing unreleased paths" in result.stderr
    assert "git diff --name-only -z" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced diff failure" in result.stderr
    assert (
        json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"]
        == "0.0.0"
    )
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert git(repo, "rev-parse", "HEAD") == before_head
    assert git(repo, "tag", "--list", "v0.0.1") == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert any(entry[:2] == ["diff", "--name-only"] for entry in git_log)
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_fails_closed_when_release_diff_fails(tmp_path: Path) -> None:
    def fail_delta(repo_root: Path, base_ref: str, head_ref: str = "HEAD") -> dict[str, object]:
        raise ValueError(
            f"git diff --name-only -z {base_ref}..{head_ref} failed: forced diff failure"
        )

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(_helpers, "collect_release_delta", fail_delta)
    try:
        with pytest.raises(SystemExit) as excinfo:
            _helpers.unreleased_paths(tmp_path, remote="origin", branch="main")
    finally:
        monkeypatch.undo()

    message = str(excinfo.value)
    assert "release diff failed while computing unreleased paths" in message
    assert "git diff --name-only -z origin/main..HEAD" in message
    assert "forced diff failure" in message


def test_publish_release_dry_run_allows_no_trigger_repo_without_surfaces(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    assert not (repo / ".agents" / "surfaces.json").exists()

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for release delta test",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=_publish_env(tmp_path, bin_dir),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["execute"] is False
    assert payload["target_version"] == "0.0.1"
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()


@pytest.mark.release_only
def test_publish_current_uses_previous_release_tag_for_release_delta(tmp_path: Path) -> None:
    repo, bin_dir = _seed_publish_current_previous_tag_delta(tmp_path)

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--critique-blocked",
            "synthetic-host-signal for release delta test",
            "--repo-root",
            str(repo),
            "--publish-current",
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=_publish_env(tmp_path, bin_dir),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["previous_version"] == "0.0.0"
    assert payload["target_version"] == "0.0.1"
