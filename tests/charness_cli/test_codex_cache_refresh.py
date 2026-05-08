from __future__ import annotations

import json
from pathlib import Path

import pytest

from .support import CLI, build_test_path, clone_seeded_managed_home, make_fake_codex, run_cli

CURRENT_VERSION = json.loads((CLI.parent / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]
pytestmark = pytest.mark.ci_only


def test_charness_update_reports_codex_version_drift(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    update_result = run_cli("update", "--home-root", str(home_root), "--skip-codex-cache-refresh", "--json", env=env)
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)
    assert payload["codex_source_version"] == CURRENT_VERSION
    assert payload["codex_cache_manifest_version"] == "0.0.0-old"
    assert payload["codex_source_cache_drift"] is True
    host_state = json.loads((home_root / ".local" / "state" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_update"]["doctor"]["codex_source_cache_drift"] is True
    assert host_state["last_update"]["doctor"]["codex_cache_manifest_version"] == "0.0.0-old"
    assert isinstance(host_state["last_update"]["recorded_at"], str)


def test_charness_update_refreshes_codex_cache_via_official_app_server(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path)
    env["PATH"] = build_test_path(fake_codex.parent)

    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "0.0.0-old" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    update_result = run_cli("update", "--home-root", str(home_root), "--json", env=env)
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)

    refreshed_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / CURRENT_VERSION / ".codex-plugin" / "plugin.json"
    assert payload["codex_cache_refresh"]["status"] == "refreshed"
    assert payload["codex_cache_refresh"]["method"] == "codex-app-server-plugin-install"
    assert payload["codex_cache_refresh"]["action"] == "refresh"
    assert payload["codex_cache_manifest_version"] == CURRENT_VERSION
    assert payload["codex_source_cache_drift"] is False
    assert "codex_cache_refreshed" in payload["completed_actions"]
    assert refreshed_manifest.is_file()
    assert json.loads(refreshed_manifest.read_text(encoding="utf-8"))["version"] == CURRENT_VERSION


def test_charness_update_emits_session_staleness_when_cache_rotates(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path)
    env["PATH"] = build_test_path(fake_codex.parent)

    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    old_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "0.0.0-old" / ".codex-plugin" / "plugin.json"
    old_manifest.parent.mkdir(parents=True, exist_ok=True)
    old_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")
    third_party_manifest = (
        home_root / ".codex" / "plugins" / "cache" / "openai-curated" / "github" / "cc8b2295" / ".codex-plugin" / "plugin.json"
    )
    third_party_manifest.parent.mkdir(parents=True, exist_ok=True)
    third_party_manifest.write_text('{"version":"github-cc8b2295"}', encoding="utf-8")

    update_result = run_cli("update", "--home-root", str(home_root), "--json", env=env)
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)

    staleness = payload.get("session_staleness")
    assert isinstance(staleness, dict), "expected session_staleness payload after cache rotation"
    rotated_pairs = {
        (record["marketplace"], record["plugin"], record["old_version"], record.get("new_version", ""))
        for record in staleness.get("rotated", [])
    }
    assert ("local", "charness", "0.0.0-old", CURRENT_VERSION) in rotated_pairs
    affected = staleness.get("affected") or []
    assert any("0.0.0-old" in line for line in affected)
    assert "resolve_skill_path.py" in (staleness.get("resolver_path") or "")
    assert "Restart" in (staleness.get("message") or "")


def test_charness_update_omits_session_staleness_when_cache_stable(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path)
    env["PATH"] = build_test_path(fake_codex.parent)

    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    same_version_manifest = (
        home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / CURRENT_VERSION / ".codex-plugin" / "plugin.json"
    )
    same_version_manifest.parent.mkdir(parents=True, exist_ok=True)
    same_version_manifest.write_text(json.dumps({"version": CURRENT_VERSION}), encoding="utf-8")

    update_result = run_cli("update", "--home-root", str(home_root), "--json", env=env)
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)
    assert payload.get("session_staleness") is None
