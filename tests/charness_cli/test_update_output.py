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
    assert "  - agent-browser: updated 0.25.3 (script)" in update_result.stdout
    assert "  - cautilus: manual" in update_result.stdout
    assert "  - nose: updated 0.17.0 (script) healthcheck=not-configured" in update_result.stdout


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
                        "update": {
                            "status": "updated",
                            "mode": "script",
                            "version_transition": {"from": "0.17.0", "to": "0.18.0"},
                        }
                    },
                    "specdown": {"doctor": {"doctor_status": "ok", "healthcheck": {"status": "not-configured"}}},
                    "tokei": {
                        "update": {
                            "status": "updated",
                            "mode": "script",
                            "version_transition": {"from": "1.1.0", "to": "1.1.0"},
                        }
                    },
                    "github-gh": {
                        "update": {
                            "status": "updated",
                            "mode": "package_manager",
                            "package_manager": "npm",
                            "package_name": "gh-cli",
                            "version_transition": {"from": "2.0.0", "to": "2.1.0"},
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
    assert "TOOLS:" in output
    assert "  - agent-browser: updated (version unknown)" in output
    assert "  - cautilus: manual" in output
    assert "  - nose: updated 0.17.0 -> 0.18.0 (script)" in output
    assert "  - specdown: ok healthcheck=not-configured" in output
    assert "  - tokei: updated 1.1.0 (script)" in output
    assert "  - github-gh: updated 2.0.0 -> 2.1.0 (npm: gh-cli)" in output


def test_tool_update_lines_empty_results_render_nothing(capsys) -> None:
    module = load_charness_module("charness_tool_update_lines_empty_under_test")

    assert module._tool_update_lines({"results": {}}) == []
    assert module._tool_update_lines({}) == []

    module.print_update_human_summary(
        {
            "package_id": "charness",
            "checkout": {"pulled": False, "repo_root": "/tmp/charness"},
            "scope": "all",
            "tool_update": {"results": {}},
        }
    )

    output = capsys.readouterr().out
    assert "TOOLS:" not in output


def test_package_manager_tool_next_step_includes_version_transition() -> None:
    module = load_charness_module("charness_package_manager_next_step_under_test")

    next_step = module._package_manager_tool_next_step(
        "nose",
        {
            "mode": "package_manager",
            "package_manager": "cargo",
            "package_name": "nose-cli",
            "status": "updated",
            "version_transition": {"from": "0.17.0", "to": "0.18.0"},
        },
    )

    assert next_step == "`nose` was updated via `cargo` package `nose-cli` (0.17.0 -> 0.18.0)."

    plain_next_step = module._package_manager_tool_next_step(
        "nose",
        {
            "mode": "package_manager",
            "package_manager": "cargo",
            "package_name": "nose-cli",
            "status": "updated",
        },
    )

    assert plain_next_step == "`nose` was updated via `cargo` package `nose-cli`."


def test_print_next_actions_labels_repo_onboarding_primary_and_merges(capsys) -> None:
    module = load_charness_module("charness_next_actions_unit_under_test")

    module._print_next_actions(
        {
            "next_action": {
                "kind": "repo-init",
                "host": None,
                "source": "repo_onboarding",
                "message": "Run charness setup in this repo.",
            },
            "repo_onboarding": {"message": "Run charness setup in this repo."},
            "claude_host_guidance": {"message": "Restart Claude Code."},
            "codex_host_guidance": {"message": "Restart Codex."},
        }
    )

    output = capsys.readouterr().out
    assert output.count("NEXT_ACTION:") == 1
    assert output.count("  - repo: Run charness setup in this repo.") == 1
    assert "  - claude: Restart Claude Code." in output
    assert "  - codex: Restart Codex." in output
    assert "CODEX_NEXT_STEP" not in output
    assert "CLAUDE_NEXT_STEP" not in output
    assert "REPO_NEXT_STEP" not in output
