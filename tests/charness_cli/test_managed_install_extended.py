from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .support import (
    CLI,
    build_test_path,
    clone_seeded_managed_home,
    make_fake_agent_browser,
    make_fake_brew_specdown,
    make_fake_claude,
    make_fake_npm_gws,
    make_git_repo_copy,
    make_release_fixture,
    make_support_sync_fixture,
    run_cli,
)
from .test_managed_install import init_managed_home_from_repo
from .tool_fakes import make_fake_cautilus


def test_installed_cli_update_refreshes_the_cli_binary_from_managed_checkout(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo)

    updated_checkout_cli = source_repo / "charness"
    original_text = updated_checkout_cli.read_text(encoding="utf-8")
    sentinel = "# update-refresh-sentinel\n"
    assert sentinel not in original_text
    updated_checkout_cli.write_text(sentinel + original_text, encoding="utf-8")
    subprocess.run(["git", "add", "charness"], cwd=source_repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Update CLI entrypoint"],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    installed_cli = home_root / ".local" / "bin" / "charness"
    update_result = subprocess.run(
        [sys.executable, str(installed_cli), "update", "--home-root", str(home_root), "--skip-codex-cache-refresh"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert update_result.returncode == 0, update_result.stderr
    assert sentinel in installed_cli.read_text(encoding="utf-8")
    assert sentinel in (home_root / ".agents" / "src" / "charness" / "charness").read_text(encoding="utf-8")


def test_installed_cli_update_all_refreshes_external_tools_and_support_state(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo)

    updated_checkout_cli = source_repo / "charness"
    original_text = updated_checkout_cli.read_text(encoding="utf-8")
    sentinel = "# update-all-refresh-sentinel\n"
    assert sentinel not in original_text
    updated_checkout_cli.write_text(sentinel + original_text, encoding="utf-8")
    subprocess.run(["git", "add", "charness"], cwd=source_repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Update CLI before update all"],
        cwd=source_repo,
        check=True,
        capture_output=True,
        text=True,
    )

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
        [sys.executable, str(installed_cli), "update", "all", "--home-root", str(home_root), "--skip-codex-cache-refresh", "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)
    managed_repo = home_root / ".agents" / "src" / "charness"

    assert payload["scope"] == "all"
    assert payload["previous_checkout_version"] == payload["checkout_version"]
    assert "external_tools_updated" in payload["completed_actions"]
    assert sentinel in installed_cli.read_text(encoding="utf-8")
    assert sentinel in (managed_repo / "charness").read_text(encoding="utf-8")

    tool_update = payload["tool_update"]
    assert tool_update["managed_checkout"] is True
    assert tool_update["repo_root"] == str(managed_repo)
    assert tool_update["tool_ids"] == []
    assert tool_update["results"]["agent-browser"]["update"]["status"] == "updated"
    assert tool_update["results"]["agent-browser"]["support"]["status"] == "synced"
    assert tool_update["results"]["cautilus"]["update"]["status"] == "manual"
    assert tool_update["results"]["cautilus"]["support"]["status"] == "synced"
    assert tool_update["results"]["specdown"]["update"]["status"] == "updated"
    assert tool_update["results"]["specdown"]["update"]["package_manager"] == "brew"
    assert tool_update["results"]["gws-cli"]["update"]["status"] == "updated"
    assert tool_update["results"]["gws-cli"]["update"]["package_manager"] == "npm"

    assert (managed_repo / "skills" / "support" / "generated" / "agent-browser").is_symlink()
    assert (managed_repo / "skills" / "support" / "generated" / "cautilus").is_symlink()
    assert json.loads((managed_repo / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))["update"][
        "update_status"
    ] == "updated"
    assert json.loads((managed_repo / "integrations" / "locks" / "cautilus.json").read_text(encoding="utf-8"))["update"][
        "update_status"
    ] == "manual"
    assert json.loads((managed_repo / "integrations" / "locks" / "specdown.json").read_text(encoding="utf-8"))["update"][
        "package_manager"
    ] == "brew"
    assert json.loads((managed_repo / "integrations" / "locks" / "gws-cli.json").read_text(encoding="utf-8"))["update"][
        "package_manager"
    ] == "npm"


def test_non_managed_repo_root_requires_skip_cli_install(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    init_result = run_cli("init", "--home-root", str(home_root), "--repo-root", str(CLI.parents[0]), env=env)
    assert init_result.returncode != 0
    assert "official charness installs must use the managed checkout" in (init_result.stderr + init_result.stdout)


def test_doctor_handles_missing_source_checkout_without_traceback(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    installed_cli = home_root / ".local" / "bin" / "charness"
    installed_cli.parent.mkdir(parents=True, exist_ok=True)
    installed_cli.write_text(CLI.read_text(encoding="utf-8"), encoding="utf-8")
    installed_cli.chmod(0o755)

    doctor_result = subprocess.run(
        [sys.executable, str(installed_cli), "doctor", "--home-root", str(home_root), "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["checkout_present"] is False
    assert payload["plugin_preamble"] is None
    assert payload["claude_host_guidance"]["status"] == "missing-source"
    assert "Run `charness init` to recreate" in payload["claude_host_guidance"]["message"]
    assert payload["next_steps"]["claude"] == payload["claude_host_guidance"]["message"]


def test_charness_reset_removes_host_state_but_keeps_cli(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@charness"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "charness" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text("{}", encoding="utf-8")

    reset_result = run_cli("reset", "--home-root", str(home_root), "--json", env=env)
    assert reset_result.returncode == 0, reset_result.stderr
    payload = json.loads(reset_result.stdout)
    assert payload["removed_plugin_root"] is True
    assert payload["removed_codex_marketplace_entry"] is True
    assert payload["removed_codex_cache"] is True
    assert payload["removed_legacy_skills_symlink"] is False
    assert payload["removed_codex_config_entries"] == ["charness@charness"]
    assert payload["removed_claude_plugin"] is True
    assert payload["removed_claude_marketplace"] is True
    assert payload["removed_cli"] is False
    assert payload["removed_checkout"] is False
    assert payload["removed_host_state"] is True
    assert (home_root / ".local" / "bin" / "charness").is_file()
    assert not (home_root / ".local" / "state" / "charness" / "host-state.json").exists()
