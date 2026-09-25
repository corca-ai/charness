from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pytest

import scripts.cli.cmd_meta as cmd_meta
import scripts.cli.host_claude as host_claude


def _clean_state_env(monkeypatch) -> None:
    monkeypatch.delenv("CHARNESS_STATE_HOME", raising=False)
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.delenv("CHARNESS_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)


def test_remove_codex_config_entries_mixed(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text(
        '[plugins."charness@market"]\nenabled = true\n\n[plugins."other@market"]\nenabled = false\n',
        encoding="utf-8",
    )
    removed = cmd_meta.remove_codex_config_entries(path)
    assert removed == ["charness@market"]
    text = path.read_text(encoding="utf-8")
    assert "charness@market" not in text
    assert "other@market" in text


def test_remove_codex_config_entries_missing(tmp_path: Path) -> None:
    assert cmd_meta.remove_codex_config_entries(tmp_path / "nope.toml") == []


def test_ensure_parent_json(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "data.json"
    cmd_meta.ensure_parent_json(path, {"a": 1})
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1}


def test_remove_claude_installed_entry_missing(tmp_path: Path) -> None:
    assert cmd_meta.remove_claude_installed_entry(tmp_path / "nope.json", "ref") is False


def test_remove_claude_installed_entry_removes(tmp_path: Path) -> None:
    path = tmp_path / "installed.json"
    path.write_text(
        json.dumps({"plugins": {"charness@mkt": {"x": 1}, "other@mkt": {}}}) + "\n",
        encoding="utf-8",
    )
    assert cmd_meta.remove_claude_installed_entry(path, "charness@mkt") is True
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "charness@mkt" not in data["plugins"]
    assert "other@mkt" in data["plugins"]


def test_remove_claude_installed_entry_wrong_shape(tmp_path: Path) -> None:
    path = tmp_path / "installed.json"
    path.write_text(json.dumps({"plugins": []}) + "\n", encoding="utf-8")
    assert cmd_meta.remove_claude_installed_entry(path, "charness@mkt") is False


def test_remove_claude_marketplace_entry_removes(tmp_path: Path) -> None:
    path = tmp_path / "known.json"
    path.write_text(json.dumps({"mkt": {"url": "x"}, "other": {}}) + "\n", encoding="utf-8")
    assert cmd_meta.remove_claude_marketplace_entry(path, "mkt") is True
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "mkt" not in data


def test_remove_claude_marketplace_entry_missing(tmp_path: Path) -> None:
    assert cmd_meta.remove_claude_marketplace_entry(tmp_path / "nope.json", "m") is False
    path = tmp_path / "known.json"
    path.write_text(json.dumps({"other": {}}) + "\n", encoding="utf-8")
    assert cmd_meta.remove_claude_marketplace_entry(path, "mkt") is False


def test_remove_codex_marketplace_entry_removes(tmp_path: Path) -> None:
    path = tmp_path / "marketplace.json"
    path.write_text(
        json.dumps({"plugins": [{"name": "charness"}, {"name": "other"}]}) + "\n",
        encoding="utf-8",
    )
    assert cmd_meta.remove_codex_marketplace_entry(path) is True
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["plugins"] == [{"name": "other"}]


def test_remove_codex_marketplace_entry_missing(tmp_path: Path) -> None:
    assert cmd_meta.remove_codex_marketplace_entry(tmp_path / "nope.json") is False


def test_remove_codex_marketplace_entry_rejects_non_list(tmp_path: Path) -> None:
    path = tmp_path / "marketplace.json"
    path.write_text(json.dumps({"plugins": {}}) + "\n", encoding="utf-8")
    with pytest.raises(cmd_meta.CharnessError, match="must be a list"):
        cmd_meta.remove_codex_marketplace_entry(path)


def test_remove_claude_plugin_without_binary(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cmd_meta.shutil, "which", lambda _name: None)
    assert cmd_meta.remove_claude_plugin(tmp_path, home_root=tmp_path) is False


def _failing_result() -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["claude"], returncode=1, stdout="boom", stderr="bust")


def test_remove_claude_plugin_failure_raises(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text(
        json.dumps({"claude": {"marketplace": {"name": "mkt"}}}) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(cmd_meta.shutil, "which", lambda _name: "/usr/bin/claude")
    # The remove paths call through the host module namespace (not a
    # from-import copy), so this is the patch point that intercepts them
    # no matter when cmd_meta was first imported.
    monkeypatch.setattr(host_claude, "run_claude", lambda *a, **k: _failing_result())
    with pytest.raises(cmd_meta.CharnessError, match="plugin uninstall"):
        cmd_meta.remove_claude_plugin(repo, home_root=tmp_path)


def test_remove_claude_marketplace_failure_raises(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text(
        json.dumps({"claude": {"marketplace": {"name": "mkt"}}}) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(cmd_meta.shutil, "which", lambda _name: "/usr/bin/claude")
    # The remove paths call through the host module namespace (not a
    # from-import copy), so this is the patch point that intercepts them
    # no matter when cmd_meta was first imported.
    monkeypatch.setattr(host_claude, "run_claude", lambda *a, **k: _failing_result())
    with pytest.raises(cmd_meta.CharnessError, match="marketplace remove"):
        cmd_meta.remove_claude_marketplace(repo, home_root=tmp_path)


def test_print_version_summary_full(capsys) -> None:
    payload: dict[str, object] = {
        "current_version": "v2.0.0",
        "current_git_head": "abc123",
        "version_provenance": {
            "invocation_kind": "cli",
            "install_method": "managed",
            "repo_root": "/repo",
        },
        "latest_release_check": {
            "status": "ok",
            "latest_tag": "v2.1.0",
            "checked_at": "2026-01-01T00:00:00Z",
            "update_available": True,
        },
        "update_notice": "update now",
    }
    cmd_meta.print_version_summary(payload)
    out = capsys.readouterr().out
    assert "VERSION: v2.0.0" in out
    assert "GIT_HEAD: abc123" in out
    assert "INVOCATION: cli" in out
    assert "INSTALL_METHOD: managed" in out
    assert "REPO_ROOT: /repo" in out
    assert "LATEST_RELEASE: ok v2.1.0" in out
    assert "LATEST_RELEASE_CHECKED_AT: 2026-01-01T00:00:00Z" in out
    assert "NEXT: update now" in out


def test_print_version_summary_minimal(capsys) -> None:
    cmd_meta.print_version_summary({})
    out = capsys.readouterr().out
    assert "VERSION: unknown" in out


def test_cmd_uninstall_removes_everything(tmp_path: Path, monkeypatch) -> None:
    _clean_state_env(monkeypatch)
    home_root = tmp_path / "home"
    repo_root = tmp_path / "repo"
    (repo_root / "packaging").mkdir(parents=True)
    (repo_root / "packaging" / "charness.json").write_text("{}\n", encoding="utf-8")

    plugin_root = home_root / ".codex" / "plugins" / "charness"
    plugin_root.mkdir(parents=True)
    (plugin_root / "f.txt").write_text("x", encoding="utf-8")

    marketplace_path = home_root / ".agents" / "plugins" / "marketplace.json"
    marketplace_path.parent.mkdir(parents=True)
    marketplace_path.write_text(
        json.dumps({"plugins": [{"name": "charness"}]}) + "\n", encoding="utf-8"
    )

    cache_dir = home_root / ".codex" / "plugins" / "cache" / "charness"
    cache_dir.mkdir(parents=True)
    (cache_dir / "f.txt").write_text("x", encoding="utf-8")

    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@mkt"]\nenabled = true\n', encoding="utf-8")

    wrapper_path = home_root / ".local" / "bin" / "claude-charness"
    wrapper_path.parent.mkdir(parents=True)
    wrapper_path.write_text("#!/bin/sh\n", encoding="utf-8")

    cli_path = home_root / ".local" / "bin" / "charness"
    cli_path.write_text("#!/bin/sh\n", encoding="utf-8")

    host_state = home_root / ".local" / "state" / "charness" / "host-state.json"
    host_state.parent.mkdir(parents=True)
    host_state.write_text("{}\n", encoding="utf-8")

    native_dir = home_root / ".local" / "state" / "charness" / "native"
    native_dir.mkdir(parents=True)
    (native_dir / "f.txt").write_text("x", encoding="utf-8")

    monkeypatch.setattr(cmd_meta, "remove_claude_plugin", lambda *a, **k: True)
    monkeypatch.setattr(cmd_meta, "remove_claude_marketplace", lambda *a, **k: True)
    monkeypatch.setattr(cmd_meta, "remove_grok_plugin", lambda **k: False)
    emitted: dict[str, object] = {}
    monkeypatch.setattr(cmd_meta, "emit_yaml", lambda payload: emitted.update(payload))

    args = argparse.Namespace(
        home_root=home_root,
        repo_root=repo_root,
        plugin_root=None,
        codex_marketplace_path=None,
        claude_wrapper_path=None,
        cli_path=None,
        delete_cli=True,
        delete_checkout=True,
    )
    assert cmd_meta.cmd_uninstall(args) == 0
    assert emitted["removed_plugin_root"] is True
    assert emitted["removed_codex_cache"] is True
    assert emitted["removed_claude_plugin"] is True
    assert emitted["removed_claude_marketplace"] is True
    assert emitted["removed_claude_wrapper"] is True
    assert emitted["removed_cli"] is True
    assert emitted["removed_checkout"] is True
    assert emitted["removed_host_state"] is True
    assert emitted["removed_native_core"] is True
    assert not plugin_root.exists()
    assert not cli_path.exists()
    assert not repo_root.exists()


def test_cmd_reset_delegates(tmp_path: Path, monkeypatch) -> None:
    called: dict[str, object] = {}

    def fake_uninstall(args: argparse.Namespace) -> int:
        called["args"] = args
        return 0

    monkeypatch.setattr(cmd_meta, "cmd_uninstall", fake_uninstall)
    args = argparse.Namespace(home_root=tmp_path)
    assert cmd_meta.cmd_reset(args) == 0
    assert called["args"] is args
