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
    make_fake_cautilus,
    make_fake_claude,
    make_fake_npm_gws,
    make_git_repo_copy,
    make_release_fixture,
    make_support_sync_fixture,
    run_cli,
)

CURRENT_VERSION = json.loads((CLI.parent / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]


def init_managed_home_from_repo(
    tmp_path: Path,
    source_repo: Path,
    *,
    cli_source: Path | None = None,
) -> tuple[Path, dict[str, str]]:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    standalone_cli = tmp_path / "bin" / "charness"
    standalone_cli.parent.mkdir(parents=True, exist_ok=True)
    standalone_cli.write_text((cli_source or source_repo / "charness").read_text(encoding="utf-8"), encoding="utf-8")
    standalone_cli.chmod(0o755)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent, standalone_cli.parent)
    init_result = subprocess.run(
        [sys.executable, str(standalone_cli), "init", "--home-root", str(home_root), "--repo-url", str(source_repo)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr
    return home_root, env


def test_charness_init_exports_managed_surface(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    legacy_skills = home_root / ".agents" / "skills"
    legacy_skills.parent.mkdir(parents=True, exist_ok=True)
    legacy_skills.symlink_to(CLI.parents[1] / "skills" / "public", target_is_directory=True)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    result = run_cli("init", "--home-root", str(home_root), env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["plugin_root"] == str(home_root / ".codex" / "plugins" / "charness")
    assert payload["cli_path"] == str(home_root / ".local" / "bin" / "charness")
    assert payload["claude_wrapper_path"] == str(home_root / ".local" / "bin" / "claude-charness")
    assert payload["checkout"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["checkout"]["managed"] is True
    assert payload["next_steps"]["codex"] == payload["codex_host_guidance"]["message"]
    assert payload["codex_host_install"]["status"] == "skipped"
    assert payload["codex_host_install"]["reason"] == "codex-cli-missing"
    assert payload["next_steps"]["claude"] == "Restart Claude Code to load charness."
    assert payload["removed_legacy_skills_symlink"] is True
    assert "legacy_skills_symlink_removed" in payload["completed_actions"]
    marketplace = json.loads((home_root / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
    assert marketplace["plugins"][0]["name"] == "charness"
    assert marketplace["plugins"][0]["source"]["path"] == "./.codex/plugins/charness"
    known_marketplaces = json.loads((home_root / ".claude" / "plugins" / "known_marketplaces.json").read_text(encoding="utf-8"))
    installed_plugins = json.loads((home_root / ".claude" / "plugins" / "installed_plugins.json").read_text(encoding="utf-8"))
    assert "corca-charness" in known_marketplaces
    assert "charness@corca-charness" in installed_plugins["plugins"]
    assert (home_root / ".local" / "bin" / "charness").is_file()
    assert (home_root / ".local" / "bin" / "claude-charness").is_file()
    assert legacy_skills.exists() is False
    assert legacy_skills.is_symlink() is False


def test_standalone_cli_bootstraps_managed_checkout_without_explicit_clone(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    standalone_cli = tmp_path / "bin" / "charness"
    standalone_cli.parent.mkdir(parents=True, exist_ok=True)
    standalone_cli.write_text(CLI.read_text(encoding="utf-8"), encoding="utf-8")
    standalone_cli.chmod(0o755)

    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent, standalone_cli.parent)
    result = subprocess.run(
        [sys.executable, str(standalone_cli), "init", "--home-root", str(home_root), "--repo-url", str(source_repo)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["checkout"]["managed"] is True
    assert payload["checkout"]["cloned"] is True
    assert payload["checkout"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert (home_root / ".agents" / "src" / "charness" / "packaging" / "charness.json").is_file()
    assert (home_root / ".local" / "bin" / "charness").is_file()
    install_state = json.loads((home_root / ".local" / "state" / "charness" / "install-state.json").read_text(encoding="utf-8"))
    assert install_state["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert install_state["managed_checkout"] is True


def test_embedded_cli_bootstraps_managed_checkout_from_configured_repo_url(tmp_path: Path) -> None:
    embedded_root = tmp_path / "embedded"
    embedded_root.mkdir()
    embedded_repo = make_git_repo_copy(embedded_root)
    upstream_root = tmp_path / "upstream"
    upstream_root.mkdir()
    upstream_repo = make_git_repo_copy(upstream_root)

    packaging_path = upstream_repo / "packaging" / "charness.json"
    packaging = json.loads(packaging_path.read_text(encoding="utf-8"))
    packaging["version"] = "0.0.1-upstream-test"
    packaging["codex"]["manifest"]["version"] = "0.0.1-upstream-test"
    packaging["claude"]["manifest"]["version"] = "0.0.1-upstream-test"
    packaging_path.write_text(json.dumps(packaging, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sync_result = subprocess.run(
        [sys.executable, "scripts/sync_root_plugin_manifests.py", "--repo-root", "."],
        cwd=upstream_repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert sync_result.returncode == 0, sync_result.stderr
    subprocess.run(
        ["git", "add", "packaging/charness.json", "plugins/charness", ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"],
        cwd=upstream_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "mark upstream repo"],
        cwd=upstream_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    embedded_cli = embedded_repo / "charness"
    embedded_text = embedded_cli.read_text(encoding="utf-8")
    embedded_cli.write_text(
        embedded_text.replace(
            'REPO_URL = "https://github.com/corca-ai/charness"',
            f'REPO_URL = "{upstream_repo}"',
        ),
        encoding="utf-8",
    )

    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent)
    result = subprocess.run(
        [sys.executable, str(embedded_cli), "init", "--home-root", str(home_root)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["checkout"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["checkout"]["cloned"] is True
    assert payload["checkout"]["managed"] is True
    assert payload["codex_source_version"] == "0.0.1-upstream-test"
    install_state = json.loads((home_root / ".local" / "state" / "charness" / "install-state.json").read_text(encoding="utf-8"))
    assert install_state["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert install_state["managed_checkout"] is True


def test_charness_doctor_reports_managed_surface(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--json", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["install_state_path"] == str(home_root / ".local" / "state" / "charness" / "install-state.json")
    assert payload["host_state_path"] == str(home_root / ".local" / "state" / "charness" / "host-state.json")
    assert payload["version_state_path"] == str(home_root / ".local" / "state" / "charness" / "version-state.json")
    assert payload["checkout_present"] is True
    assert payload["plugin_root_present"] is True
    assert payload["cli_present"] is True
    assert payload["claude_wrapper_present"] is True
    assert payload["codex_marketplace_entry"]["name"] == "charness"
    assert payload["codex_marketplace_entry"]["source"]["path"] == "./.codex/plugins/charness"
    assert payload["legacy_skills_symlink_present"] is False
    assert payload["codex_source_version"] == CURRENT_VERSION
    assert payload["codex_cache_manifest_version"] is None
    assert payload["codex_source_cache_drift"] is False
    assert payload["codex_host_guidance"]["status"] == "host-unavailable"
    assert payload["codex_host_guidance"]["manual_action_required"] is False
    assert (
        payload["next_steps"]["codex"]
        == "Codex CLI not detected; charness prepared the local plugin source and personal marketplace only."
    )
    assert payload["claude_marketplace_name"] == "corca-charness"
    assert payload["claude_plugin_ref"] == "charness@corca-charness"
    assert payload["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["managed_checkout"] is True
    assert payload["claude_marketplace_entry"]["source"]["path"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["claude_installed_entry"]["version"] == "local"
    assert payload["claude_host_guidance"]["status"] == "installed"
    assert payload["claude_host_guidance"]["manual_action_required"] is False
    assert payload["next_steps"]["claude"] == payload["claude_host_guidance"]["message"]
    assert payload["plugin_preamble"]["update_hints"]["claude"] == "Run `charness update`, then restart Claude Code."
    assert payload["version_provenance"]["invocation_kind"] == "custom-cli"
    assert payload["latest_release_check"] is None
    host_state = json.loads((home_root / ".local" / "state" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["state_version"] == 1
    assert host_state["last_init"]["doctor"]["codex_host_guidance"]["status"] == "host-unavailable"
    assert host_state["last_init"]["doctor"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert isinstance(host_state["last_init"]["recorded_at"], str)
def test_installed_cli_update_refreshes_installed_binary_from_managed_checkout(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo, cli_source=CLI)

    source_cli = source_repo / "charness"
    original_text = source_cli.read_text(encoding="utf-8")
    marker = "\nUPDATED_BINARY_MARKER = 'from-source-update-test'\n"
    source_cli.write_text(original_text + marker, encoding="utf-8")
    subprocess.run(["git", "add", "charness"], cwd=source_repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "update source binary marker"],
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

    installed_text = installed_cli.read_text(encoding="utf-8")
    managed_checkout_text = (home_root / ".agents" / "src" / "charness" / "charness").read_text(encoding="utf-8")
    assert marker.strip() in installed_text
    assert installed_text == managed_checkout_text


def test_installed_cli_update_allows_untracked_files_in_managed_checkout(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo)

    managed_checkout = home_root / ".agents" / "src" / "charness"
    untracked = managed_checkout / "untracked-update-sentinel.txt"
    untracked.write_text("runtime cache placeholder\n", encoding="utf-8")

    installed_cli = home_root / ".local" / "bin" / "charness"
    update_result = subprocess.run(
        [sys.executable, str(installed_cli), "update", "--home-root", str(home_root), "--skip-codex-cache-refresh", "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)
    assert payload["checkout"]["pulled"] is True
    assert untracked.read_text(encoding="utf-8") == "runtime cache placeholder\n"


def test_installed_cli_update_blocks_tracked_changes_in_managed_checkout(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo)

    managed_checkout = home_root / ".agents" / "src" / "charness"
    readme_path = managed_checkout / "README.md"
    readme_path.write_text(readme_path.read_text(encoding="utf-8") + "\ntracked edit\n", encoding="utf-8")

    installed_cli = home_root / ".local" / "bin" / "charness"
    update_result = subprocess.run(
        [sys.executable, str(installed_cli), "update", "--home-root", str(home_root), "--skip-codex-cache-refresh"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert update_result.returncode != 0
    assert "has tracked local changes" in (update_result.stderr + update_result.stdout)


def test_installed_cli_remembers_managed_checkout(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    installed_cli = home_root / ".local" / "bin" / "charness"
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
    assert payload["checkout_present"] is True
    assert payload["managed_checkout"] is True
    assert payload["claude_host_guidance"]["status"] == "installed"


def test_doctor_can_write_host_state_snapshot(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--json", "--write-state", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    host_state = json.loads((home_root / ".local" / "state" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_doctor"]["doctor"]["repo_root"] == payload["repo_root"]
    assert host_state["last_doctor"]["doctor"]["codex_source_version"] == payload["codex_source_version"]
    assert isinstance(host_state["last_doctor"]["recorded_at"], str)


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
        [sys.executable, str(installed_cli), "update", "all", "--home-root", str(home_root), "--skip-codex-cache-refresh"],
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
