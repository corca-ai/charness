from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .release_publish_fixtures import _install_fake_git, _write_exec


def _fake_git_env(log_path: Path, **overrides: str) -> dict[str, str]:
    return {**os.environ, "FAKE_GIT_LOG": str(log_path), **overrides}


def test_fake_git_logs_decodable_argv_and_preserves_argument_boundaries(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    real_git = tmp_path / "real-git"
    _write_exec(real_git, "#!/usr/bin/env bash\nexit 0\n")
    _install_fake_git(bin_dir, real_git=str(real_git))
    log_path = tmp_path / "git-log.json"
    unusual = 'quote" slash\\ controls\x01\b\f\n\r\t 한글'

    first = subprocess.run(
        [bin_dir / "git", "probe", unusual],
        check=False,
        capture_output=True,
        text=True,
        env=_fake_git_env(log_path),
    )
    boundary = subprocess.run(
        [bin_dir / "git", "ls-remote", "--tags origin", "refs/tags/v0.0.0"],
        check=False,
        capture_output=True,
        text=True,
        env=_fake_git_env(log_path, FAKE_GIT_LS_REMOTE_PREVIOUS_TAG_FAIL="1"),
    )

    assert first.returncode == 0
    assert boundary.returncode == 0
    assert json.loads(log_path.read_text(encoding="utf-8")) == [
        ["probe", unusual],
        ["ls-remote", "--tags origin", "refs/tags/v0.0.0"],
    ]


def test_fake_git_branch_failure_count_is_derived_from_log(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    real_git = tmp_path / "real-git"
    _write_exec(real_git, "#!/usr/bin/env bash\nexit 0\n")
    _install_fake_git(bin_dir, real_git=str(real_git))
    log_path = tmp_path / "git-log.json"
    log_path.write_text('[["push","origin","main"]]\n', encoding="utf-8")

    result = subprocess.run(
        [bin_dir / "git", "push", "origin", "main"],
        check=False,
        capture_output=True,
        text=True,
        env=_fake_git_env(log_path, FAKE_GIT_BRANCH_PUSH_ERROR_AT="2"),
    )

    assert result.returncode == 49
    assert "forced branch push error (before)" in result.stderr
    assert json.loads(log_path.read_text(encoding="utf-8")) == [
        ["push", "origin", "main"],
        ["push", "origin", "main"],
    ]


def test_fake_git_after_mode_normalizes_real_git_failure(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    real_git = tmp_path / "real-git"
    _write_exec(real_git, "#!/usr/bin/env bash\nexit 7\n")
    _install_fake_git(bin_dir, real_git=str(real_git))

    result = subprocess.run(
        [bin_dir / "git", "push", "origin", "main"],
        check=False,
        capture_output=True,
        text=True,
        env=_fake_git_env(
            tmp_path / "git-log.json",
            FAKE_GIT_BRANCH_PUSH_ERROR_AT="1",
            FAKE_GIT_BRANCH_PUSH_ERROR_MODE="after",
        ),
    )

    assert result.returncode == 1
    assert "forced branch push error" not in result.stderr
