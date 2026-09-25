from __future__ import annotations

import json
from pathlib import Path

import scripts.cli.host_codex as host_codex
from scripts.cli.bootstrap import PACKAGE_ID


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_marketplace_entry_branches(tmp_path: Path) -> None:
    assert host_codex.codex_marketplace_entry(tmp_path / "missing.json") is None

    not_list = _write_json(tmp_path / "not-list.json", {"plugins": {"name": PACKAGE_ID}})
    assert host_codex.codex_marketplace_entry(not_list) is None

    no_match = _write_json(tmp_path / "no-match.json", {"plugins": [{"name": "other"}]})
    assert host_codex.codex_marketplace_entry(no_match) is None

    found = _write_json(
        tmp_path / "found.json",
        {"plugins": [{"name": "other"}, {"name": PACKAGE_ID, "version": "1.0"}]},
    )
    entry = host_codex.codex_marketplace_entry(found)
    assert entry is not None and entry.get("name") == PACKAGE_ID


def test_source_version_branches(tmp_path: Path) -> None:
    assert host_codex.codex_source_version(tmp_path / "absent") is None

    bad_dir = tmp_path / "bad"
    (bad_dir / ".codex-plugin").mkdir(parents=True)
    (bad_dir / ".codex-plugin" / "plugin.json").write_text("{oops", encoding="utf-8")
    assert host_codex.codex_source_version(bad_dir) is None

    non_str_dir = tmp_path / "non-str"
    (non_str_dir / ".codex-plugin").mkdir(parents=True)
    _write_json(non_str_dir / ".codex-plugin" / "plugin.json", {"version": 7})
    assert host_codex.codex_source_version(non_str_dir) is None

    good_dir = tmp_path / "good"
    (good_dir / ".codex-plugin").mkdir(parents=True)
    _write_json(good_dir / ".codex-plugin" / "plugin.json", {"version": "1.2.3"})
    assert host_codex.codex_source_version(good_dir) == "1.2.3"


def test_cache_entry_for_plugin_id_branches() -> None:
    entries = [{"plugin": PACKAGE_ID, "marketplace": "mp"}]
    assert host_codex.codex_cache_entry_for_plugin_id(entries, "bare-id") is None
    assert host_codex.codex_cache_entry_for_plugin_id(entries, "other@mp") is None
    assert host_codex.codex_cache_entry_for_plugin_id(entries, f"{PACKAGE_ID}@mp") == entries[0]


def test_primary_cache_entry_fallback_branches() -> None:
    ours = {"plugin": PACKAGE_ID, "marketplace": "mp", "manifest_version": "9"}
    entry, plugin_id = host_codex.codex_primary_cache_entry(
        [ours], enabled_plugin_ids=[], source_version=None
    )
    assert (entry, plugin_id) == (ours, None)

    foreign = {"plugin": "other", "marketplace": "mp", "manifest_version": "9"}
    assert host_codex.codex_primary_cache_entry(
        [foreign], enabled_plugin_ids=[], source_version=None
    ) == (None, None)

    match, matched_id = host_codex.codex_primary_cache_entry(
        [ours], enabled_plugin_ids=[f"{PACKAGE_ID}@mp"], source_version="9"
    )
    assert (match, matched_id) == (ours, f"{PACKAGE_ID}@mp")


def test_last_installed_commit_branches(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(host_codex, "read_host_state", lambda _home: {})
    assert host_codex._last_installed_commit(tmp_path) is None

    monkeypatch.setattr(
        host_codex,
        "read_host_state",
        lambda _home: {"last_init": {"recorded_at": "2026-01-01", "delivery_verified": False}},
    )
    assert host_codex._last_installed_commit(tmp_path) is None

    monkeypatch.setattr(
        host_codex,
        "read_host_state",
        lambda _home: {
            "last_init": {
                "recorded_at": "2026-01-01",
                "delivery_verified": True,
                "operation_status": "failed",
            }
        },
    )
    assert host_codex._last_installed_commit(tmp_path) is None

    monkeypatch.setattr(
        host_codex,
        "read_host_state",
        lambda _home: {
            "last_init": {
                "recorded_at": "2026-01-01",
                "delivery_verified": True,
                "doctor": {"checkout_git_head": "abc123"},
            }
        },
    )
    assert host_codex._last_installed_commit(tmp_path) == "abc123"

    monkeypatch.setattr(
        host_codex,
        "read_host_state",
        lambda _home: {
            "last_init": {
                "recorded_at": "2026-01-01",
                "delivery_verified": True,
                "doctor": {},
            }
        },
    )
    assert host_codex._last_installed_commit(tmp_path) is None


def test_maybe_install_skip_and_missing_inputs(tmp_path: Path) -> None:
    skipped = host_codex.maybe_install_codex_host(
        home_root=tmp_path, codex_marketplace_path=tmp_path, doctor_payload={}, skip=True
    )
    assert skipped["status"] == "skipped" and skipped["reason"] == "flag-disabled"

    no_hosts = host_codex.maybe_install_codex_host(
        home_root=tmp_path, codex_marketplace_path=tmp_path, doctor_payload={}, skip=False
    )
    assert no_hosts["reason"] == "codex-cli-missing"

    no_config = host_codex.maybe_install_codex_host(
        home_root=tmp_path,
        codex_marketplace_path=tmp_path,
        doctor_payload={"hosts": {"codex": True}},
        skip=False,
    )
    assert no_config["reason"] == "missing-config"


def test_maybe_install_refresh_paths(tmp_path: Path, monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def _fake_refresh(**kwargs: object) -> dict[str, object]:
        calls.append(dict(kwargs))
        return {"status": "attempted"}

    monkeypatch.setattr(host_codex, "refresh_codex_cache_via_app_server", _fake_refresh)

    def _payload(enabled: list[str]) -> dict[str, object]:
        return {
            "hosts": {"codex": True},
            "codex_enabled_plugin_ids": enabled,
            "codex_source_version": "1.0",
            "codex_cache_manifest_version": "0.9",
            "codex_host_guidance": {"status": "installed"},
            "checkout_git_head": "abc",
        }

    refresh = host_codex.maybe_install_codex_host(
        home_root=tmp_path,
        codex_marketplace_path=tmp_path / "marketplace",
        doctor_payload=_payload([f"{PACKAGE_ID}@mp"]),
        skip=False,
    )
    assert refresh["action"] == "refresh"
    assert refresh["plugin_id"] == f"{PACKAGE_ID}@mp"

    install = host_codex.maybe_install_codex_host(
        home_root=tmp_path,
        codex_marketplace_path=tmp_path / "marketplace",
        doctor_payload=_payload([]),
        skip=False,
    )
    assert install["action"] == "install"
    assert "plugin_id" not in install
    assert len(calls) == 2


def test_config_entries_branches(tmp_path: Path) -> None:
    assert host_codex.codex_config_entries(tmp_path / "missing.toml") == []

    config = tmp_path / "config.toml"
    config.write_text(
        '[plugins."other@mp"]\nenabled = true\n\n'
        f'[plugins."{PACKAGE_ID}@mp"]\nenabled = true\n\n'
        f'[plugins."{PACKAGE_ID}@old"]\n',
        encoding="utf-8",
    )
    entries = host_codex.codex_config_entries(config)
    assert {"plugin_id": f"{PACKAGE_ID}@mp", "enabled": True} in entries
    assert {"plugin_id": f"{PACKAGE_ID}@old", "enabled": None} in entries
    assert all(not item["plugin_id"].startswith("other@") for item in entries)


def test_guidance_unavailable_and_empty_cache(tmp_path: Path) -> None:
    unavailable = host_codex.build_codex_host_guidance(
        codex_available=False,
        codex_marketplace_path=tmp_path,
        source_version="1.0",
        cache_entries=[],
        config_entries=[],
    )
    assert unavailable["status"] == "host-unavailable"

    missing = host_codex.build_codex_host_guidance(
        codex_available=True,
        codex_marketplace_path=tmp_path,
        source_version="1.0",
        cache_entries=[],
        config_entries=[],
    )
    assert missing["status"] == "needs-host-install"


def test_guidance_invalid_manifest_needs_refresh() -> None:
    entry = {
        "plugin": PACKAGE_ID,
        "marketplace": "mp",
        "manifest_version": "",
        "manifest_status": "invalid",
    }
    guidance = host_codex.build_codex_host_guidance(
        codex_available=True,
        codex_marketplace_path=Path("marketplace"),
        source_version="1.0",
        cache_entries=[entry],
        config_entries=[],
    )
    assert guidance["status"] == "needs-refresh"
    assert guidance["reason"] == "invalid-cache-manifest"


def test_guidance_version_drift_needs_refresh() -> None:
    entry = {
        "plugin": PACKAGE_ID,
        "marketplace": "mp",
        "manifest_version": "0.9",
        "manifest_status": "valid",
    }
    guidance = host_codex.build_codex_host_guidance(
        codex_available=True,
        codex_marketplace_path=Path("marketplace"),
        source_version="1.0",
        cache_entries=[entry],
        config_entries=[{"plugin_id": f"{PACKAGE_ID}@mp", "enabled": True}],
    )
    assert guidance["status"] == "needs-refresh"


def test_guidance_stale_enabled_loop_and_cached() -> None:
    current = {
        "plugin": PACKAGE_ID,
        "marketplace": "mp",
        "manifest_version": "1.0",
        "manifest_status": "valid",
    }
    stale = {
        "plugin": PACKAGE_ID,
        "marketplace": "old",
        "manifest_version": "0.5",
        "manifest_status": "valid",
    }
    guidance = host_codex.build_codex_host_guidance(
        codex_available=True,
        codex_marketplace_path=Path("marketplace"),
        source_version="1.0",
        cache_entries=[current, stale],
        config_entries=[
            {"plugin_id": f"{PACKAGE_ID}@mp", "enabled": True},
            {"plugin_id": f"{PACKAGE_ID}@old", "enabled": True},
            {"plugin_id": f"{PACKAGE_ID}@ghost", "enabled": True},
        ],
    )
    assert guidance["status"] == "installed"
    assert f"`{PACKAGE_ID}@old`" in str(guidance["message"])
    assert f"`{PACKAGE_ID}@ghost`" not in str(guidance["message"])

    cached = host_codex.build_codex_host_guidance(
        codex_available=True,
        codex_marketplace_path=Path("marketplace"),
        source_version="1.0",
        cache_entries=[current],
        config_entries=[],
    )
    assert cached["status"] == "cached"
