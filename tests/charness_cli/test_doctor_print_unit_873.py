from __future__ import annotations

import argparse
from pathlib import Path

import scripts.cli.cmd_doctor as cmd_doctor


def test_print_latest_release_with_tag(capsys) -> None:
    cmd_doctor._print_latest_release({"latest_tag": "v2.0.0", "status": "ok"})
    out = capsys.readouterr().out
    assert "LATEST_RELEASE: ok v2.0.0" in out


def test_print_latest_release_without_tag(capsys) -> None:
    cmd_doctor._print_latest_release({"status": "unknown"})
    out = capsys.readouterr().out
    assert "LATEST_RELEASE: unknown" in out


def test_print_latest_release_ignores_non_dict(capsys) -> None:
    cmd_doctor._print_latest_release(None)
    assert capsys.readouterr().out == ""


def test_print_latest_release_prefers_version_key(capsys) -> None:
    cmd_doctor._print_latest_release({"latest_version": "v1.0.0", "status": "stale"})
    out = capsys.readouterr().out
    assert "LATEST_RELEASE: stale v1.0.0" in out


def test_print_codex_marketplace_present(capsys) -> None:
    payload = {
        "codex_marketplace_path": "/home/u/marketplace.json",
        "codex_marketplace_entry": {"source": {"path": "/src/charness"}},
    }
    cmd_doctor._print_codex_marketplace(payload)
    out = capsys.readouterr().out
    assert "CODEX_MARKETPLACE: present" in out
    assert "/src/charness" in out


def test_print_codex_marketplace_missing(capsys) -> None:
    payload = {
        "codex_marketplace_path": "/home/u/marketplace.json",
        "codex_marketplace_entry": None,
    }
    cmd_doctor._print_codex_marketplace(payload)
    out = capsys.readouterr().out
    assert "CODEX_MARKETPLACE: missing-entry" in out


def test_print_codex_cache_present(capsys) -> None:
    payload = {
        "codex_cache_entries": [
            {"marketplace": "mkt", "version": "1.0", "manifest_version": "3"},
            {"bogus": True},
            "not-a-dict",
        ],
        "codex_cache_manifest_version": "3",
        "codex_source_cache_drift": True,
    }
    cmd_doctor._print_codex_cache(payload)
    out = capsys.readouterr().out
    assert "CODEX_CACHE: present mkt:1.0 manifest=3" in out
    assert "CODEX_CACHE_VERSION: 3" in out
    assert "CODEX_SOURCE_CACHE_DRIFT: yes" in out


def test_print_codex_cache_missing(capsys) -> None:
    payload = {
        "codex_cache_entries": [],
        "codex_cache_root": "/home/u/cache",
        "codex_source_cache_drift": False,
    }
    cmd_doctor._print_codex_cache(payload)
    out = capsys.readouterr().out
    assert "CODEX_CACHE: missing /home/u/cache" in out
    assert "CODEX_SOURCE_CACHE_DRIFT: no" in out


def test_print_codex_config_present(capsys) -> None:
    payload = {
        "codex_config_entries": [
            {"plugin_id": "charness@x", "enabled": True},
            {"incomplete": True},
        ]
    }
    cmd_doctor._print_codex_config(payload)
    out = capsys.readouterr().out
    assert "CODEX_CONFIG: present charness@x enabled=True" in out


def test_print_codex_config_missing(capsys) -> None:
    payload = {"codex_config_entries": [], "codex_config_path": "/home/u/config.toml"}
    cmd_doctor._print_codex_config(payload)
    out = capsys.readouterr().out
    assert "CODEX_CONFIG: missing-entry" in out


def _claude_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "cli_present": True,
        "cli_path": "/home/u/.local/bin/charness",
        "cli_in_path": True,
        "claude_wrapper_present": False,
        "claude_wrapper_path": "/home/u/.local/bin/claude-charness",
        "claude_wrapper_in_path": False,
        "claude_marketplace_entry": {"name": "mkt"},
        "claude_known_marketplaces_path": "/home/u/.claude/plugins/known.json",
        "claude_marketplace_name": "mkt",
        "claude_installed_entry": {"installPath": "/home/u/.claude/plugins/x"},
        "claude_installed_plugins_path": "/home/u/.claude/plugins/installed.json",
        "claude_plugin_ref": "charness@mkt",
    }
    payload.update(overrides)
    return payload


def test_print_claude_install_surface_all_present(capsys) -> None:
    cmd_doctor._print_claude_install_surface(_claude_payload())
    out = capsys.readouterr().out
    assert "CLI: present" in out
    assert "CLI_IN_PATH: yes" in out
    assert "CLAUDE_WRAPPER: missing" in out
    assert "CLAUDE_WRAPPER_IN_PATH: no" in out
    assert "CLAUDE_MARKETPLACE: present" in out
    assert "CLAUDE_PLUGIN: present" in out


def test_print_claude_install_surface_all_missing(capsys) -> None:
    cmd_doctor._print_claude_install_surface(
        _claude_payload(
            cli_present=False,
            cli_in_path=False,
            claude_marketplace_entry=None,
            claude_installed_entry=None,
        )
    )
    out = capsys.readouterr().out
    assert "CLI: missing" in out
    assert "CLI_IN_PATH: no" in out
    assert "CLAUDE_MARKETPLACE: missing-entry" in out
    assert "CLAUDE_PLUGIN: missing-entry" in out


def test_cmd_doctor_write_state(tmp_path: Path, monkeypatch) -> None:
    home_root = tmp_path / "home"
    home_root.mkdir()
    calls: dict[str, object] = {}

    def fake_resolve_repo_root(home: Path, explicit: object) -> tuple[Path, bool]:
        return (tmp_path / "repo", False)

    def fake_resolve_target(explicit: object) -> Path:
        return tmp_path / "target"

    def fake_runtime_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
        base = tmp_path
        return (
            base / "plugin",
            base / "marketplace.json",
            base / "wrapper",
            base / "cli",
        )

    def fake_build_payload(**kwargs: object) -> dict[str, object]:
        calls["payload_kwargs"] = kwargs
        return {"ok": True}

    def fake_write_state(home: Path, *, key: str, payload: dict[str, object]) -> None:
        calls["write_state"] = (str(home), key, payload)

    def fake_emit(args: argparse.Namespace, payload: dict[str, object], **kwargs: object) -> None:
        calls["emit"] = payload

    monkeypatch.setattr(cmd_doctor, "resolve_repo_root", fake_resolve_repo_root)
    monkeypatch.setattr(cmd_doctor, "resolve_target_repo_root", fake_resolve_target)
    monkeypatch.setattr(cmd_doctor, "resolve_runtime_paths", fake_runtime_paths)
    monkeypatch.setattr(cmd_doctor, "build_doctor_payload", fake_build_payload)
    monkeypatch.setattr(cmd_doctor, "write_host_state", fake_write_state)
    monkeypatch.setattr(cmd_doctor, "emit_operational_response", fake_emit)

    args = argparse.Namespace(
        home_root=home_root,
        repo_root=None,
        target_repo_root=None,
        write_state=True,
        next_action=False,
    )
    assert cmd_doctor.cmd_doctor(args) == 0
    assert calls["write_state"] == (str(home_root), "last_doctor", {"ok": True})
    assert calls["emit"] == {"ok": True}
