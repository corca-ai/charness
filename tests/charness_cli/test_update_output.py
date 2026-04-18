from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .support import (
    make_fake_agent_browser,
    make_fake_brew_specdown,
    make_fake_npm_gws,
    make_git_repo_copy,
    make_release_fixture,
    make_support_sync_fixture,
)
from .test_managed_install import init_managed_home_from_repo
from .tool_fakes import make_fake_cautilus


def test_installed_cli_update_all_without_json_prints_progress_and_summary(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo)

    fake_agent_browser = make_fake_agent_browser(tmp_path)
    fake_brew, _ = make_fake_brew_specdown(tmp_path)
    fake_npm, fake_gws = make_fake_npm_gws(tmp_path)
    fake_cautilus = make_fake_cautilus(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env["PATH"] = os.pathsep.join(
        [
            str(fake_agent_browser.parent),
            str(fake_brew.parent),
            str(fake_npm.parent),
            str(fake_gws.parent),
            str(fake_cautilus.parent),
            env["PATH"],
        ]
    )
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    installed_cli = home_root / ".local" / "bin" / "charness"
    update_result = subprocess.run(
        [sys.executable, str(installed_cli), "update", "all", "--home-root", str(home_root), "--skip-codex-cache-refresh"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert update_result.returncode == 0, update_result.stderr
    assert "STEP: updating tracked external tools" in update_result.stdout
    assert "STEP: syncing support surfaces" in update_result.stdout
    assert "STEP: refreshing tool doctor state" in update_result.stdout
    assert "DONE: update complete" in update_result.stdout
    assert "PACKAGE: charness" in update_result.stdout
    assert "VERSION: None" not in update_result.stdout
    assert "-> None" not in update_result.stdout
    assert "SCOPE: all" in update_result.stdout
    assert "TOOLS:" in update_result.stdout
    assert "agent-browser=updated" in update_result.stdout
    assert "cautilus=manual" in update_result.stdout
