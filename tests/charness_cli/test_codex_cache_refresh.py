from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

from tests.repo_copy import REPO_COPY_IGNORE

from .support import (
    CLI,
    build_test_path,
    clone_seeded_managed_home,
    make_fake_codex,
    pin_state_home,
    run_cli,
    run_cli_path,
)
from .test_managed_install import load_charness_module

CURRENT_VERSION = json.loads((CLI.parent / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]
pytestmark = pytest.mark.boundary_contract(
    reason="JSON-RPC refresh tests require a real child transport and deadline"
)


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


@pytest.mark.release_only
def test_failed_codex_refresh_is_retryable_and_does_not_emit_success_completion(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path, fail_plugin_install=True)
    env["PATH"] = build_test_path(fake_codex.parent)

    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "0.0.0-old" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    failed = run_cli("update", "--detail", "--home-root", str(home_root), env=env)
    assert failed.returncode == 1, failed.stderr
    failed_payload = yaml.safe_load(failed.stdout)
    assert failed_payload["codex_cache_refresh"]["status"] == "failed"
    assert failed_payload["codex_host_guidance"]["status"] == "failed"
    assert failed_payload["next_action"]["kind"] == "manual"
    assert "retry with `charness update --detail`" in failed_payload["next_action"]["message"]
    assert "FAILED: update incomplete" in failed.stderr
    assert "DONE: update complete" not in failed.stderr

    host_state = json.loads((home_root / ".local" / "state" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_update"]["delivery_status"] == "failed"
    assert host_state["last_update"]["delivery_verified"] is False

    fake_codex.with_name(".codex-fail-plugin-install").unlink()
    retried = run_cli("update", "--detail", "--home-root", str(home_root), env=env)
    assert retried.returncode == 0, retried.stderr
    retried_payload = yaml.safe_load(retried.stdout)
    assert retried_payload["codex_cache_refresh"]["status"] == "refreshed"
    assert retried_payload["codex_cache_refresh"]["status"] != "skipped"
    assert "DONE: update complete" in retried.stderr

    # A verified same-version no-op is still a successful host-delivery
    # observation. It must not be persisted as an unverified skip that forces
    # every later invocation through the app-server again.
    fake_codex.with_name(".codex-fail-plugin-install").write_text("1\n", encoding="utf-8")
    same_version = run_cli("update", "--detail", "--home-root", str(home_root), env=env)
    assert same_version.returncode == 0, same_version.stderr
    same_version_payload = yaml.safe_load(same_version.stdout)
    assert same_version_payload["codex_cache_refresh"]["status"] == "skipped"
    assert same_version_payload["codex_cache_refresh"]["reason"] == "already-current"
    assert same_version_payload["codex_cache_refresh"]["delivery_verified"] is True
    assert same_version_payload["codex_cache_refresh"]["verification"] == "same-version-content-readback"
    same_version_state = json.loads(
        (home_root / ".local" / "state" / "charness" / "host-state.json").read_text(encoding="utf-8")
    )
    assert same_version_state["last_update"]["delivery_status"] == "skipped"
    assert same_version_state["last_update"]["delivery_verified"] is True

    # A same-version directory with changed payload must not inherit the old
    # verified provenance; a failed refresh remains retryable.
    cache_root = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / CURRENT_VERSION
    cache_file = next(path for path in cache_root.rglob("*") if path.is_file() and path.name != "plugin.json")
    cache_file.write_bytes(cache_file.read_bytes() + b"\ncontent-drift\n")
    stale_same_version = run_cli("update", "--detail", "--home-root", str(home_root), env=env)
    assert stale_same_version.returncode == 1, stale_same_version.stderr
    stale_payload = yaml.safe_load(stale_same_version.stdout)
    assert stale_payload["codex_cache_refresh"]["status"] == "failed"


@pytest.mark.release_only
def test_same_version_invalid_cache_manifest_is_not_verified(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path)
    env["PATH"] = build_test_path(fake_codex.parent)
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")

    first = run_cli("update", "--detail", "--home-root", str(home_root), env=env)
    assert first.returncode == 0, first.stderr
    manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / CURRENT_VERSION / ".codex-plugin" / "plugin.json"
    manifest.write_text('{"version":"not-the-source"}\n', encoding="utf-8")
    fake_codex.with_name(".codex-fail-plugin-install").write_text("1\n", encoding="utf-8")

    result = run_cli("update", "--detail", "--home-root", str(home_root), env=env)
    assert result.returncode == 1, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["codex_cache_refresh"]["status"] == "failed"
    assert payload["codex_cache_refresh"].get("reason") != "already-current"


@pytest.mark.release_only
def test_failed_codex_init_emits_failure_progress_and_records_failed_operation(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path, fail_plugin_install=True)
    env["PATH"] = build_test_path(fake_codex.parent)
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    old_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "0.0.0-old" / ".codex-plugin" / "plugin.json"
    old_manifest.parent.mkdir(parents=True, exist_ok=True)
    old_manifest.write_text('{"version":"0.0.0-old"}\n', encoding="utf-8")

    result = run_cli("init", "--detail", "--home-root", str(home_root), env=env)
    assert result.returncode == 1, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["codex_host_install"]["status"] == "failed"
    assert "FAILED: init incomplete" in result.stderr
    assert "DONE: init complete" not in result.stderr
    state = json.loads((home_root / ".local" / "state" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert state["last_init"]["operation_status"] == "failed"
    assert state["last_init"]["delivery_verified"] is False


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


def _jsonrpc_child(source: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, "-u", "-c", source],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_jsonrpc_response_wait_uses_one_absolute_deadline() -> None:
    module = load_charness_module("charness_codex_deadline_under_test")
    proc = _jsonrpc_child(
        "import json,time\n"
        "for value in range(20):\n"
        " print(json.dumps({'id': 100 + value, 'result': {}}), flush=True)\n"
        " time.sleep(0.015)\n"
    )
    started = time.monotonic()
    try:
        with pytest.raises(module.CharnessError, match="timed out"):
            module.wait_for_jsonrpc_response(
                proc,
                expected_id=2,
                deadline=started + 0.06,
            )
        elapsed = time.monotonic() - started
    finally:
        proc.terminate()
        proc.wait(timeout=2)

    assert elapsed < 0.15


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("print('not-json', flush=True)", "invalid JSON-RPC payload"),
        ("pass", "exited before returning a response"),
    ],
)
def test_jsonrpc_response_wait_reports_malformed_payload_and_eof(source: str, message: str) -> None:
    module = load_charness_module(f"charness_codex_failure_{message.split()[0]}_under_test")
    proc = _jsonrpc_child(source)
    try:
        with pytest.raises(module.CharnessError, match=message):
            module.wait_for_jsonrpc_response(
                proc,
                expected_id=2,
                deadline=time.monotonic() + 0.5,
            )
    finally:
        proc.wait(timeout=2)


def test_jsonrpc_response_wait_returns_matching_error_after_unrelated_message() -> None:
    module = load_charness_module("charness_codex_matching_error_under_test")
    proc = _jsonrpc_child(
        "import json\n"
        "print(json.dumps({'method': 'progress'}), flush=True)\n"
        "print(json.dumps({'id': 2, 'error': {'code': -32000, 'message': 'nope'}}), flush=True)\n"
    )
    try:
        response = module.wait_for_jsonrpc_response(
            proc,
            expected_id=2,
            deadline=time.monotonic() + 0.5,
        )
    finally:
        proc.wait(timeout=2)

    assert response["error"] == {"code": -32000, "message": "nope"}


def test_codex_cache_refresh_preserves_matching_error_envelope(tmp_path: Path, monkeypatch) -> None:
    module = load_charness_module("charness_codex_error_envelope_under_test")
    fake_codex = make_fake_codex(tmp_path, fail_plugin_install=True)
    monkeypatch.setenv("PATH", build_test_path(fake_codex.parent))
    home_root = tmp_path / "home"
    home_root.mkdir()

    result = module.refresh_codex_cache_via_app_server(
        home_root=home_root,
        codex_marketplace_path=CLI.parent / ".agents" / "plugins" / "marketplace.json",
        plugin_name="charness",
        timeout_seconds=0.5,
    )

    assert result == {
        "status": "failed",
        "reason": "plugin-install-error",
        "method": "codex-app-server-plugin-install",
        "error": "forced plugin/install failure",
    }


def test_codex_cache_refresh_accepts_real_initialize_shape_and_lifecycle_notifications(
    tmp_path: Path, monkeypatch
) -> None:
    module = load_charness_module("charness_codex_real_lifecycle_under_test")
    fake_codex = make_fake_codex(tmp_path)
    monkeypatch.setenv("PATH", build_test_path(fake_codex.parent))
    monkeypatch.setenv("CHARNESS_FAKE_CODEX_APP_SERVER_MODE", "real-init-notifications")
    home_root = tmp_path / "home"
    home_root.mkdir()

    result = module.refresh_codex_cache_via_app_server(
        home_root=home_root,
        codex_marketplace_path=CLI.parent / ".agents" / "plugins" / "marketplace.json",
        plugin_name="charness",
        timeout_seconds=0.5,
    )

    assert result["status"] == "attempted"
    assert result["method"] == "codex-app-server-plugin-install"


@pytest.mark.parametrize(
    ("mode", "error_text"),
    [
        ("unrelated-stream", "timed out while waiting for Codex app-server response"),
        ("malformed", "invalid JSON-RPC payload"),
        ("eof", "exited before returning a response"),
        ("initialize-error", "Codex app-server initialize failed: forced initialize failure"),
    ],
)
def test_codex_cache_refresh_maps_transport_failures_to_existing_envelope(
    tmp_path: Path,
    monkeypatch,
    mode: str,
    error_text: str,
) -> None:
    module = load_charness_module(f"charness_codex_{mode}_envelope_under_test")
    fake_codex = make_fake_codex(tmp_path)
    monkeypatch.setenv("PATH", build_test_path(fake_codex.parent))
    monkeypatch.setenv("CHARNESS_FAKE_CODEX_APP_SERVER_MODE", mode)
    home_root = tmp_path / "home"
    home_root.mkdir()

    result = module.refresh_codex_cache_via_app_server(
        home_root=home_root,
        codex_marketplace_path=CLI.parent / ".agents" / "plugins" / "marketplace.json",
        plugin_name="charness",
        timeout_seconds=0.06 if mode == "unrelated-stream" else 0.5,
    )

    assert result["status"] == "failed"
    assert result["reason"] == "app-server-error"
    assert result["method"] == "codex-app-server-plugin-install"
    assert error_text in result["error"]


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

    adoption = tmp_path / ".agents"
    adoption.mkdir()
    shutil.copy2(
        CLI.parent / ".agents" / "consumer-validator-adoption.yaml",
        adoption / "consumer-validator-adoption.yaml",
    )
    args = argparse.Namespace(repo_root=tmp_path, summary=False)
    assert module.cmd_catalog_list(args) == 0
    full = yaml.safe_load(capsys.readouterr().out)
    assert "public_skills" in full["inventory"]
    assert full["consumer_validator_catalog"]["catalog_id"] == "consumer-validator-catalog"
    assert "counts" not in full["inventory"]
    args.summary = True
    assert module.cmd_catalog_list(args) == 0
    summary = yaml.safe_load(capsys.readouterr().out)
    assert "counts" in summary["inventory"]
    assert "public_skills" not in summary["inventory"]
    assert module.cmd_catalog_refresh(args) == 0
    capsys.readouterr()

    missing = tmp_path / "missing-refresh-root"
    invalid_args = argparse.Namespace(repo_root=missing)
    invalid_list_args = argparse.Namespace(repo_root=missing, summary=False)
    assert module.cmd_catalog_list(invalid_list_args) == 2
    list_error = capsys.readouterr()
    assert "does not exist" in list_error.out
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
        symlinks=True,
    )
    installed_cli = home_root / ".local" / "bin" / "charness"
    installed_cli.parent.mkdir(parents=True)
    shutil.copy2(CLI, installed_cli)

    consumer_repo = tmp_path / "consumer"
    consumer_repo.mkdir()
    consumer_agents = consumer_repo / ".agents"
    consumer_agents.mkdir()
    shutil.copy2(
        CLI.parent / ".agents" / "consumer-validator-adoption.yaml",
        consumer_agents / "consumer-validator-adoption.yaml",
    )
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    result = run_cli_path(
        installed_cli,
        "catalog",
        "list",
        "--repo-root",
        str(consumer_repo),
        cwd=tmp_path,
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

    list_result = run_cli(
        "catalog",
        "list",
        "--repo-root",
        str(missing),
    )
    assert list_result.returncode == 2
    list_payload = yaml.safe_load(list_result.stdout)
    assert list_payload["repo_root"] == str(missing.resolve())
    assert "does not exist" in list_payload["error"]
    assert "Traceback" not in list_result.stdout

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
