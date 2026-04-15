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
    make_fake_claude,
    make_fake_codex,
    make_git_repo_copy,
    run_cli,
)

CURRENT_VERSION = json.loads((CLI.parent / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]


def test_charness_init_installs_codex_via_official_app_server(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = make_git_repo_copy(source_root)
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    fake_codex = make_fake_codex(tmp_path)
    standalone_cli = tmp_path / "bin" / "charness"
    standalone_cli.parent.mkdir(parents=True, exist_ok=True)
    standalone_cli.write_text(CLI.read_text(encoding="utf-8"), encoding="utf-8")
    standalone_cli.chmod(0o755)

    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_claude.parent, fake_codex.parent, standalone_cli.parent)

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
    assert payload["codex_host_install"]["status"] == "installed"
    assert payload["codex_host_install"]["action"] == "install"
    assert payload["codex_host_guidance"]["status"] == "installed"
    assert payload["codex_cache_manifest_version"] == CURRENT_VERSION
    assert (
        payload["next_steps"]["codex"]
        == "Codex host install markers are present. Start a new Codex session to load charness."
    )
    assert "codex_host_installed" in payload["completed_actions"]
    config_path = home_root / ".codex" / "config.toml"
    cache_manifest = (
        home_root
        / ".codex"
        / "plugins"
        / "cache"
        / "local"
        / "charness"
        / CURRENT_VERSION
        / ".codex-plugin"
        / "plugin.json"
    )
    assert config_path.is_file()
    assert '[plugins."charness@local"]' in config_path.read_text(encoding="utf-8")
    assert cache_manifest.is_file()


def test_charness_doctor_reports_codex_version_drift(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path)
    env["PATH"] = build_test_path(fake_codex.parent)
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--json", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["codex_source_version"] == CURRENT_VERSION
    assert payload["codex_cache_manifest_version"] == "0.0.0-old"
    assert payload["codex_source_cache_drift"] is True
    assert payload["codex_enabled_plugin_id"] == "charness@local"
    assert payload["codex_host_guidance"]["status"] == "needs-refresh"
    assert payload["next_action"]["kind"] == "manual"
    assert payload["next_action"]["host"] == "codex"
    assert payload["next_action"]["message"] == payload["codex_host_guidance"]["message"]
