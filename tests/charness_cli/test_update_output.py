from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.repo_copy import clone_seeded_charness_repo

from .support import (
    make_fake_go_specdown,
    make_fake_npm_agent_browser,
    make_fake_update_all_toolchain,
    make_release_fixture,
    make_support_sync_fixture,
)
from .test_managed_install import init_managed_home_from_repo, load_charness_module
from .tool_fakes import make_fake_cautilus, make_fake_nose


@pytest.mark.release_only
def test_installed_cli_update_all_without_json_prints_progress_and_summary(tmp_path: Path, seeded_charness_git_repo: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = clone_seeded_charness_repo(source_root, seeded_charness_git_repo)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo)

    fake_agent_browser_npm, fake_agent_browser = make_fake_npm_agent_browser(tmp_path)
    fake_go, specdown_bin = make_fake_go_specdown(tmp_path)
    make_fake_update_all_toolchain(tmp_path)
    fake_cautilus = make_fake_cautilus(tmp_path)
    fake_curl, fake_nose = make_fake_nose(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env["PATH"] = os.pathsep.join(
        [
            str(fake_curl.parent),
            str(fake_nose.parent),
            str(fake_agent_browser_npm.parent),
            str(fake_agent_browser.parent),
            str(fake_go.parent),
            str(specdown_bin.parent),
            str(fake_cautilus.parent),
            env["PATH"],
        ]
    )
    env["GOPATH"] = str(specdown_bin.parent.parent)
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
    assert "nose=updated healthcheck=not-configured" in update_result.stdout


def test_update_human_summary_without_version_none_prints_tool_statuses(capsys) -> None:
    module = load_charness_module("charness_update_output_unit_under_test")

    module.print_update_human_summary(
        {
            "package_id": "charness",
            "checkout": {"pulled": False, "repo_root": "/tmp/charness"},
            "scope": "all",
            "completed_actions": ["external_tools_updated"],
            "tool_update": {
                "results": {
                    "cautilus": {"update": {"status": "manual"}},
                    "agent-browser": {"update": {"status": "updated"}},
                    "nose": {
                        "doctor": {
                            "doctor_status": "updated",
                            "healthcheck": {"status": "not-configured"},
                        }
                    },
                }
            },
        }
    )

    output = capsys.readouterr().out
    assert "VERSION: None" not in output
    assert "-> None" not in output
    assert "SCOPE: all" in output
    assert "TOOLS: agent-browser=updated, cautilus=manual, nose=updated healthcheck=not-configured" in output
