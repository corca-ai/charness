from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .support import CLI, clone_seeded_managed_home, make_fake_claude, run_cli


def test_charness_init_exports_managed_surface(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    legacy_skills = home_root / ".agents" / "skills"
    legacy_skills.parent.mkdir(parents=True, exist_ok=True)
    legacy_skills.symlink_to(CLI.parents[1] / "skills" / "public", target_is_directory=True)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    result = run_cli("init", "--home-root", str(home_root), env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["plugin_root"] == str(home_root / ".codex" / "plugins" / "charness")
    assert payload["cli_path"] == str(home_root / ".local" / "bin" / "charness")
    assert payload["claude_wrapper_path"] == str(home_root / ".local" / "bin" / "claude-charness")
    assert payload["checkout"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["checkout"]["managed"] is True
    assert (
        payload["next_steps"]["codex"]
        == "Restart Codex from the home directory that owns "
        f"`{home_root / '.agents' / 'plugins' / 'marketplace.json'}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
    )
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


def test_charness_doctor_reports_managed_surface(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--json", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["install_state_path"] == str(home_root / ".local" / "share" / "charness" / "install-state.json")
    assert payload["host_state_path"] == str(home_root / ".local" / "share" / "charness" / "host-state.json")
    assert payload["checkout_present"] is True
    assert payload["plugin_root_present"] is True
    assert payload["cli_present"] is True
    assert payload["claude_wrapper_present"] is True
    assert payload["codex_marketplace_entry"]["name"] == "charness"
    assert payload["codex_marketplace_entry"]["source"]["path"] == "./.codex/plugins/charness"
    assert payload["legacy_skills_symlink_present"] is False
    assert payload["codex_source_version"] == "0.0.0-dev"
    assert payload["codex_cache_manifest_version"] is None
    assert payload["codex_source_cache_drift"] is False
    assert payload["codex_host_guidance"]["status"] == "needs-host-install"
    assert payload["codex_host_guidance"]["manual_action_required"] is True
    assert payload["claude_marketplace_name"] == "corca-charness"
    assert payload["claude_plugin_ref"] == "charness@corca-charness"
    assert payload["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["managed_checkout"] is True
    assert payload["claude_marketplace_entry"]["source"]["path"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["claude_installed_entry"]["version"] == "local"
    assert payload["claude_host_guidance"]["status"] == "installed"
    assert payload["claude_host_guidance"]["manual_action_required"] is False
    assert payload["plugin_preamble"]["update_hints"]["claude"] == "Run `charness update`, then restart Claude Code."
    host_state = json.loads((home_root / ".local" / "share" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["state_version"] == 1
    assert host_state["last_init"]["doctor"]["codex_host_guidance"]["status"] == "needs-host-install"
    assert host_state["last_init"]["doctor"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert isinstance(host_state["last_init"]["recorded_at"], str)


def test_charness_doctor_reports_codex_version_drift(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--json", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["codex_source_version"] == "0.0.0-dev"
    assert payload["codex_cache_manifest_version"] == "0.0.0-old"
    assert payload["codex_source_cache_drift"] is True
    assert payload["codex_enabled_plugin_id"] == "charness@local"
    assert payload["codex_host_guidance"]["status"] == "needs-refresh"


def test_charness_update_reports_codex_version_drift(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    update_result = run_cli("update", "--home-root", str(home_root), env=env)
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)
    assert payload["codex_source_version"] == "0.0.0-dev"
    assert payload["codex_cache_manifest_version"] == "0.0.0-old"
    assert payload["codex_source_cache_drift"] is True
    host_state = json.loads((home_root / ".local" / "share" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_update"]["doctor"]["codex_source_cache_drift"] is True
    assert host_state["last_update"]["doctor"]["codex_cache_manifest_version"] == "0.0.0-old"
    assert isinstance(host_state["last_update"]["recorded_at"], str)


def test_installed_cli_remembers_managed_checkout(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    installed_cli = home_root / ".local" / "bin" / "charness"
    doctor_result = subprocess.run(
        ["python3", str(installed_cli), "doctor", "--home-root", str(home_root), "--json"],
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
    host_state = json.loads((home_root / ".local" / "share" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_doctor"]["doctor"]["repo_root"] == payload["repo_root"]
    assert host_state["last_doctor"]["doctor"]["codex_source_version"] == payload["codex_source_version"]
    assert isinstance(host_state["last_doctor"]["recorded_at"], str)


def test_non_managed_repo_root_requires_skip_cli_install(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli("init", "--home-root", str(home_root), "--repo-root", str(CLI.parents[0]), env=env)
    assert init_result.returncode != 0
    assert "official charness installs must use the managed checkout" in (init_result.stderr + init_result.stdout)


def test_doctor_handles_missing_source_checkout_without_traceback(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    installed_cli = home_root / ".local" / "bin" / "charness"
    installed_cli.parent.mkdir(parents=True, exist_ok=True)
    installed_cli.write_text(CLI.read_text(encoding="utf-8"), encoding="utf-8")
    installed_cli.chmod(0o755)

    doctor_result = subprocess.run(
        ["python3", str(installed_cli), "doctor", "--home-root", str(home_root), "--json"],
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
    assert not (home_root / ".local" / "share" / "charness" / "host-state.json").exists()
