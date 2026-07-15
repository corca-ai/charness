from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.repo_copy import REPO_COPY_IGNORE

from .support import CLI, build_test_path, clone_seeded_managed_home, make_fake_codex, run_cli
from .test_managed_install import load_charness_module

CURRENT_VERSION = json.loads((CLI.parent / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]


@pytest.mark.release_only
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

    update_result = run_cli("update", "--home-root", str(home_root), "--skip-codex-cache-refresh", env=env)
    assert update_result.returncode == 0, update_result.stderr
    payload = yaml.safe_load(update_result.stdout)
    assert payload["codex_source_version"] == CURRENT_VERSION
    assert payload["codex_cache_manifest_version"] == "0.0.0-old"
    assert payload["codex_source_cache_drift"] is True
    host_state = json.loads((home_root / ".local" / "state" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_update"]["doctor"]["codex_source_cache_drift"] is True
    assert host_state["last_update"]["doctor"]["codex_cache_manifest_version"] == "0.0.0-old"
    assert isinstance(host_state["last_update"]["recorded_at"], str)


@pytest.mark.release_only
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

    update_result = run_cli("update", "--detail", "--home-root", str(home_root), env=env)
    assert update_result.returncode == 0, update_result.stderr
    payload = yaml.safe_load(update_result.stdout)

    refreshed_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / CURRENT_VERSION / ".codex-plugin" / "plugin.json"
    assert payload["codex_cache_refresh"]["status"] == "refreshed"
    assert payload["codex_cache_refresh"]["method"] == "codex-app-server-plugin-install"
    assert payload["codex_cache_refresh"]["action"] == "refresh"
    assert payload["codex_cache_manifest_version"] == CURRENT_VERSION
    assert payload["codex_source_cache_drift"] is False
    assert "codex_cache_refreshed" in payload["completed_actions"]
    assert refreshed_manifest.is_file()
    assert json.loads(refreshed_manifest.read_text(encoding="utf-8"))["version"] == CURRENT_VERSION

    staleness = payload.get("session_staleness")
    assert isinstance(staleness, dict), "expected session_staleness payload after cache rotation"
    rotated_pairs = {
        (record["marketplace"], record["plugin"], record["old_version"], record.get("new_version", ""))
        for record in staleness.get("rotated", [])
    }
    assert ("local", "charness", "0.0.0-old", CURRENT_VERSION) in rotated_pairs
    affected = staleness.get("affected") or []
    assert any("0.0.0-old" in line for line in affected)
    assert "capability_catalog.py" in (staleness.get("resolver_path") or "")
    assert "Restart" in (staleness.get("message") or "")


def test_cache_diff_and_staleness_capture_rotation(tmp_path: Path) -> None:
    module = load_charness_module("charness_codex_cache_refresh_diff_under_test")
    old_root = tmp_path / "cache" / "local" / "charness" / "0.0.0-old"
    new_root = tmp_path / "cache" / "local" / "charness" / CURRENT_VERSION
    old_root.mkdir(parents=True)
    new_root.mkdir(parents=True)
    old_root.rmdir()
    third_party_root = tmp_path / "cache" / "openai-curated" / "github" / "cc8b2295"
    third_party_root.mkdir(parents=True)

    before = [
        {
            "marketplace": "local",
            "plugin": "charness",
            "version": "0.0.0-old",
            "version_dir": str(old_root),
            "manifest_path": str(old_root / ".codex-plugin" / "plugin.json"),
            "manifest_version": "0.0.0-old",
        },
        {
            "marketplace": "openai-curated",
            "plugin": "github",
            "version": "cc8b2295",
            "version_dir": str(third_party_root),
            "manifest_path": str(third_party_root / ".codex-plugin" / "plugin.json"),
            "manifest_version": "github-cc8b2295",
        },
    ]
    after = [
        {
            "marketplace": "local",
            "plugin": "charness",
            "version": CURRENT_VERSION,
            "version_dir": str(new_root),
            "manifest_path": str(new_root / ".codex-plugin" / "plugin.json"),
            "manifest_version": CURRENT_VERSION,
        },
        before[1],
    ]

    diff = module.diff_cache_entries(before, after)
    assert diff["rotated"] == [
        {
            "marketplace": "local",
            "plugin": "charness",
            "old_version": "0.0.0-old",
            "old_version_dir": str(old_root),
            "new_version": CURRENT_VERSION,
            "new_version_dir": str(new_root),
        }
    ]
    payload = module.session_staleness_payload(diff, home_root=tmp_path / "home", repo_root=tmp_path / "repo")
    assert payload is not None
    assert payload["affected"] == [f"local/charness 0.0.0-old -> {CURRENT_VERSION}"]
    assert "Restart" in payload["message"]

    stable_root = tmp_path / "cache" / "local" / "charness" / CURRENT_VERSION
    stable = {
        "marketplace": "local",
        "plugin": "charness",
        "version": CURRENT_VERSION,
        "version_dir": str(stable_root),
        "manifest_path": str(stable_root / ".codex-plugin" / "plugin.json"),
        "manifest_version": CURRENT_VERSION,
    }
    stable_diff = module.diff_cache_entries([stable], [stable])
    assert stable_diff == {"rotated": [], "removed": [], "added": []}
    assert module.session_staleness_payload(stable_diff, home_root=tmp_path / "home", repo_root=tmp_path / "repo") is None


def test_session_staleness_without_cache_diff_returns_none(tmp_path: Path) -> None:
    module = load_charness_module("charness_codex_cache_refresh_unit_under_test")

    payload = module.session_staleness_payload(
        {"rotated": [], "removed": [], "added": []},
        home_root=tmp_path / "home",
        repo_root=tmp_path / "repo",
    )

    assert payload is None


def test_session_staleness_uses_repo_resolver_then_managed_checkout_fallback(tmp_path: Path) -> None:
    module = load_charness_module("charness_codex_cache_refresh_resolver_under_test")
    diff = {"rotated": [{"marketplace": "local", "plugin": "charness", "old_version": "1", "new_version": "2"}], "removed": []}
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "capability_catalog.py").write_text("# repo resolver\n", encoding="utf-8")
    payload = module.session_staleness_payload(diff, home_root=tmp_path / "home", repo_root=repo)
    assert payload["resolver_path"] == str(repo / "scripts" / "capability_catalog.py")

    fallback = tmp_path / "fallback-home" / ".agents" / "src" / "charness" / "scripts"
    fallback.mkdir(parents=True)
    (fallback / "capability_catalog.py").write_text("# managed resolver\n", encoding="utf-8")
    payload = module.session_staleness_payload(diff, home_root=tmp_path / "fallback-home", repo_root=tmp_path / "missing-repo")
    assert payload["resolver_path"] == str(fallback / "capability_catalog.py")


def test_charness_catalog_loader_imports_backend_in_process(tmp_path: Path, capsys) -> None:
    module = load_charness_module("charness_catalog_loader_under_test")
    backend = module._load_catalog_lib()
    assert backend.list_catalog(Path.cwd())["artifacts"]["mode"] == "read-only"
    root = str(Path.cwd().resolve())
    original_path = list(module.sys.path)
    try:
        module.EMBEDDED_REPO_ROOT = None
        module.sys.path[:] = [entry for entry in module.sys.path if entry != root]
        assert module._load_catalog_lib() is backend
    finally:
        module.sys.path[:] = original_path

    args = argparse.Namespace(repo_root=tmp_path)
    assert module.cmd_catalog_list(args) == 0
    capsys.readouterr()
    assert module.cmd_catalog_refresh(args) == 0
    capsys.readouterr()

    missing = tmp_path / "missing-refresh-root"
    invalid_args = argparse.Namespace(repo_root=missing)
    assert module.cmd_catalog_refresh(invalid_args) == 2
    error = capsys.readouterr()
    assert "does not exist" in error.out
    assert "Traceback" not in error.out
    assert not missing.exists()

    assert module.cmd_catalog_refresh(invalid_args) == 2
    payload = yaml.safe_load(capsys.readouterr().out)
    assert "does not exist" in payload["error"]

    file_root = tmp_path / "refresh-file-root"
    file_root.write_text("not a directory\n", encoding="utf-8")
    invalid_args = argparse.Namespace(repo_root=file_root)
    assert module.cmd_catalog_refresh(invalid_args) == 2
    error = capsys.readouterr()
    assert "not a directory" in error.out
    assert "Traceback" not in error.out

    resolve_args = argparse.Namespace(
        repo_root=tmp_path,
        skill_id="missing",
        reported_path=tmp_path / "missing/SKILL.md",
        home=tmp_path / "home",
        codex_home=tmp_path / "codex",
        marketplace="local",
        plugin="charness",
    )
    assert module.cmd_catalog_resolve_skill_path(resolve_args) == 1
    capsys.readouterr()


def test_installed_cli_catalog_list_loads_backend_from_managed_checkout(tmp_path: Path) -> None:
    """A copied CLI must use its managed checkout, not its bin directory."""
    home_root = tmp_path / "home"
    managed_checkout = home_root / ".agents" / "src" / "charness"
    shutil.copytree(
        CLI.parent,
        managed_checkout,
        ignore=REPO_COPY_IGNORE,
    )
    installed_cli = home_root / ".local" / "bin" / "charness"
    installed_cli.parent.mkdir(parents=True)
    shutil.copy2(CLI, installed_cli)

    consumer_repo = tmp_path / "consumer"
    consumer_repo.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    result = subprocess.run(
        [
            sys.executable,
            str(installed_cli),
            "catalog",
            "list",
            "--repo-root",
            str(consumer_repo),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifacts"]["mode"] == "read-only"
    assert not (consumer_repo / "charness-artifacts").exists()


def test_charness_catalog_refresh_invalid_roots_subprocess_contract(tmp_path: Path) -> None:
    missing = tmp_path / "missing-refresh-root"
    missing_result = run_cli(
        "catalog",
        "refresh",
        "--repo-root",
        str(missing),
    )
    assert missing_result.returncode == 2
    assert missing_result.stderr == ""
    missing_payload = yaml.safe_load(missing_result.stdout)
    assert missing_payload["repo_root"] == str(missing.resolve())
    assert "does not exist" in missing_payload["error"]
    assert "Traceback" not in missing_result.stdout
    assert not missing.exists()

    file_root = tmp_path / "refresh-file-root"
    file_root.write_text("not a directory\n", encoding="utf-8")
    file_result = run_cli(
        "catalog",
        "refresh",
        "--repo-root",
        str(file_root),
    )
    assert file_result.returncode == 2
    file_payload = yaml.safe_load(file_result.stdout)
    assert "not a directory" in file_payload["error"]
    assert "Traceback" not in file_result.stdout
