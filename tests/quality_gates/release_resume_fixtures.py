"""Cached Git states for release resume boundary tests.

The state builders live outside the resilience test module so the test module remains a
readable inventory of boundary assertions.  Each cache entry is immutable; consumers
copy it before attaching their own remote, fake-tool state, or message mutation.
"""
from __future__ import annotations

import shutil
import subprocess
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


def _build_failed_closeout_seed(
    staging: Path,
    *,
    failure_at: int,
    failure_mode: str,
    issue_view_fail_after: int | None = None,
) -> None:
    """Build one immutable post-publication failure state for resume tests."""
    repo, _remote, bin_dir = seed_publish_release(staging)
    env = _resume_closeout_env(staging, bin_dir)
    env["FAKE_GIT_BRANCH_PUSH_ERROR_AT"] = str(failure_at)
    env["FAKE_GIT_BRANCH_PUSH_ERROR_MODE"] = failure_mode
    if issue_view_fail_after is not None:
        env["FAKE_GH_ISSUE_VIEW_FAIL_AFTER"] = str(issue_view_fail_after)
    failed = _run_patch_closeout(repo, env)
    if failed.returncode == 0:
        raise AssertionError(f"failed closeout seed unexpectedly succeeded: {failed.stdout}")

    state = staging / "fixture-state"
    state.mkdir()
    for name in ("release-state.json", "release-assets.json"):
        source = staging / name
        if source.is_file():
            shutil.copy2(source, state / name)


def _failed_closeout_seed(
    *,
    failure_at: int,
    failure_mode: str,
    issue_view_fail_after: int | None = None,
) -> Path:
    suffix = f"{failure_at}-{failure_mode}"
    if issue_view_fail_after is not None:
        suffix += f"-issue-view-{issue_view_fail_after}"
    return get_or_build(
        f"release-failed-closeout-{suffix}",
        lambda staging: _build_failed_closeout_seed(
            staging,
            failure_at=failure_at,
            failure_mode=failure_mode,
            issue_view_fail_after=issue_view_fail_after,
        ),
    )


def seed_failed_closeout(
    tmp_path: Path,
    *,
    failure_at: int = 1,
    failure_mode: str = "before",
    issue_view_fail_after: int | None = None,
) -> tuple[Path, dict[str, str], Path]:
    seed = _failed_closeout_seed(
        failure_at=failure_at,
        failure_mode=failure_mode,
        issue_view_fail_after=issue_view_fail_after,
    )
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
