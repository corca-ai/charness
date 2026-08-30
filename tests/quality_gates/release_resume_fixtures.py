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
