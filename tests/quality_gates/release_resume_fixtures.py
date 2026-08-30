"""Cached Git states for release resume boundary tests.

The state builders live outside the resilience test module so the test module remains a
readable inventory of boundary assertions.  Each cache entry is immutable; consumers
copy it before attaching their own remote, fake-tool state, or message mutation.
"""
from __future__ import annotations

import shutil
import subprocess
from enum import Enum
from pathlib import Path

from tests.seed_cache import get_or_build

from .release_publish_fixtures import (
    _release_env,
    _run_publish_patch,
    _seed_publish_release_repo,
    _simulate_partial_publish,
    bug_closeout_body,
)


def _resume_closeout_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = _release_env(tmp_path, bin_dir)
    issue_state = tmp_path / "issue-state.json"
    issue_state.write_text('{"44": "OPEN"}\n', encoding="utf-8")
    env["FAKE_GH_ISSUE_STATE"] = str(issue_state)
    return env


def _run_patch_closeout(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return _run_publish_patch(
        repo,
        env,
        "--close-issue", "44",
        "--close-issue-behavior", "Behavior #44: confirmed through recovery fixture",
        "--close-issue-probe-record", "Probe record #44: local-only-by-contract",
    )


class FailedCloseoutState(str, Enum):
    CARRIER_PUSH_FAILED = "carrier-push-failed"
    ISSUE_READBACK_FAILED = "issue-readback-failed"


def _rebind_seed_remote(repo: Path, seed: Path, remote: Path) -> None:
    """Relocate a copied seed's existing origin instead of adding/fetching it."""
    config = repo / ".git" / "config"
    source_url = str(seed / "remote.git")
    text = config.read_text(encoding="utf-8")
    if source_url not in text:
        raise AssertionError(f"seed remote is not bound to its expected source: {config}")
    config.write_text(text.replace(source_url, str(remote)), encoding="utf-8")


def _build_bound_publish_seed(staging: Path) -> None:
    # The ordinary fixture pays the remote add/push cost once while constructing this
    # immutable source.  Consumers copy its refs/config and only rewrite the local path.
    _seed_publish_release_repo(staging)


def seed_publish_release(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Copy a fully seeded repo/remote/tool bundle without per-test Git setup."""
    seed = get_or_build("release-publish-bound-repo", _build_bound_publish_seed)
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    bin_dir = tmp_path / "bin"
    shutil.copytree(seed / "repo", repo)
    shutil.copytree(seed / "remote.git", remote)
    shutil.copytree(seed / "bin", bin_dir)
    _rebind_seed_remote(repo, seed, remote)
    return repo, remote, bin_dir


def _build_failed_closeout_seed(staging: Path) -> None:
    """Build the sole full-protocol failed-closeout seed."""
    repo, _remote, bin_dir = seed_publish_release(staging)
    env = _resume_closeout_env(staging, bin_dir)
    env["FAKE_GIT_BRANCH_PUSH_ERROR_AT"] = "1"
    env["FAKE_GIT_BRANCH_PUSH_ERROR_MODE"] = "before"
    failed = _run_patch_closeout(repo, env)
    if failed.returncode == 0:
        raise AssertionError(f"failed closeout seed unexpectedly succeeded: {failed.stdout}")

    state = staging / "fixture-state"
    state.mkdir()
    for name in ("release-state.json", "release-assets.json"):
        source = staging / name
        if source.is_file():
            shutil.copy2(source, state / name)


def _failed_closeout_seed() -> Path:
    return get_or_build(
        "release-failed-closeout-1-before",
        _build_failed_closeout_seed,
    )


def _run_git(repo: Path, *args: str, bare: bool = False) -> str:
    prefix = ["git", "--git-dir", str(repo)] if bare else ["git", "-C", str(repo)]
    return subprocess.run(
        [*prefix, *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _apply_issue_readback_overlay(repo: Path, remote: Path, root: Path) -> None:
    rows = [
        line.split("\t", 1)
        for line in _run_git(
            repo, "log", "--first-parent", "--max-count=5", "--format=%H%x09%s"
        ).splitlines()
    ]
    subjects = [
        "Release demo 0.0.1",
        "Record claims review",
        "Release demo 0.0.1",
        "seed",
    ]
    if (
        len(rows) != 4
        or any(len(row) != 2 for row in rows)
        or [row[1] for row in rows] != subjects
    ):
        raise AssertionError(f"failed-closeout seed topology changed: {rows!r}")
    _carrier, review, _prepared, seed = (row[0] for row in rows)
    _run_git(repo, "reset", "--hard", review)
    _run_git(repo, "tag", "-d", "v0.0.1")
    _run_git(repo, "update-ref", "refs/remotes/origin/main", seed)
    _run_git(remote, "update-ref", "refs/heads/main", seed, bare=True)
    _run_git(remote, "update-ref", "-d", "refs/tags/v0.0.1", bare=True)
    release_state = root / "release-state.json"
    if not release_state.is_file():
        raise AssertionError("canonical failed-closeout seed lacks release state")
    release_state.unlink()


def seed_failed_closeout(
    tmp_path: Path,
    *,
    state: FailedCloseoutState = FailedCloseoutState.CARRIER_PUSH_FAILED,
) -> tuple[Path, dict[str, str], Path]:
    seed = _failed_closeout_seed()
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    bin_dir = tmp_path / "bin"
    shutil.copytree(seed / "repo", repo)
    shutil.copytree(seed / "remote.git", remote)
    shutil.copytree(seed / "bin", bin_dir)
    _rebind_seed_remote(repo, seed, remote)
    for name in ("release-state.json", "release-assets.json"):
        source = seed / "fixture-state" / name
        if source.is_file():
            shutil.copy2(source, tmp_path / name)
    if state is FailedCloseoutState.ISSUE_READBACK_FAILED:
        _apply_issue_readback_overlay(repo, remote, tmp_path)
    elif state is not FailedCloseoutState.CARRIER_PUSH_FAILED:
        raise AssertionError(f"unsupported failed closeout state: {state!r}")
    env = _resume_closeout_env(tmp_path, bin_dir)
    carrier = tmp_path / "synthetic-release-closeout.md"
    carrier.write_text(
        bug_closeout_body(close_line="Close #44.", behavior_line=None) + "\n",
        encoding="utf-8",
    )
    return repo, env, carrier


def _build_partial_publish_seed(staging: Path) -> None:
    repo, _remote, _bin_dir = seed_publish_release(staging)
    _simulate_partial_publish(repo)


def seed_partial_publish(
    tmp_path: Path, *, head_closeout_body: str | None = None
) -> tuple[Path, dict[str, str], Path]:
    """Copy the common prepared release state used by closeout-only tests."""
    seed = get_or_build(
        "release-partial-publish-closeout",
        lambda staging: _build_partial_publish_seed(staging),
    )
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    bin_dir = tmp_path / "bin"
    shutil.copytree(seed / "repo", repo)
    shutil.copytree(seed / "remote.git", remote)
    shutil.copytree(seed / "bin", bin_dir)
    _rebind_seed_remote(repo, seed, remote)
    if head_closeout_body is not None:
        subprocess.run(
            ["git", "commit", "--amend", "--allow-empty", "-m", "Release demo 0.0.0",
             "-m", head_closeout_body], cwd=repo,
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "tag", "-f", "v0.0.0"], cwd=repo, check=True,
            capture_output=True, text=True,
        )
    env = _resume_closeout_env(tmp_path, bin_dir)
    carrier = tmp_path / "resume-closeout.md"
    carrier.write_text(
        bug_closeout_body(
            close_line="Close #44.",
            behavior_line="Behavior #44: confirmed through the release resume fixture",
        ) + "\n",
        encoding="utf-8",
    )
    return repo, env, carrier
