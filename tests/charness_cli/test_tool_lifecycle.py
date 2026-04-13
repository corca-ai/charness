from __future__ import annotations

import json
import os
from pathlib import Path

from .support import (
    make_fake_agent_browser,
    make_fake_brew_specdown,
    make_fake_npm_gws,
    make_release_fixture,
    make_repo_copy,
    make_support_sync_fixture,
    run_cli_in_repo,
)


def test_tool_install_persists_manual_guidance_and_support_state(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    result = run_cli_in_repo(repo_root, "tool", "install", "--repo-root", str(repo_root), "--json", "cautilus", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    cautilus = payload["results"]["cautilus"]
    assert cautilus["install"]["status"] == "manual"
    assert cautilus["install"]["docs_url"] == "https://github.com/corca-ai/cautilus"
    assert cautilus["install"]["release"]["latest_tag"] == "v1.2.3"
    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["skills/support/generated/cautilus"]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert cautilus["doctor"]["release"]["latest_version"] == "1.2.3"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "cautilus.json").read_text(encoding="utf-8"))
    assert lock_payload["release"]["latest_tag"] == "v1.2.3"
    assert lock_payload["install"]["install_status"] == "manual"
    assert lock_payload["support"]["materialized_paths"] == ["skills/support/generated/cautilus"]
    assert lock_payload["doctor"]["doctor_status"] == "missing"
    assert (repo_root / "skills" / "support" / "generated" / "cautilus").is_symlink()


def test_tool_update_executes_scripted_updates_and_refreshes_doctor(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    fake_agent_browser = make_fake_agent_browser(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_agent_browser.parent}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    result = run_cli_in_repo(repo_root, "tool", "update", "--repo-root", str(repo_root), "--json", "agent-browser", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    browser = payload["results"]["agent-browser"]
    assert browser["update"]["status"] == "updated"
    assert browser["update"]["release"]["latest_tag"] == "v0.25.3"
    assert browser["support"]["status"] == "synced"
    assert browser["doctor"]["doctor_status"] == "ok"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["release"]["latest_tag"] == "v0.25.3"
    assert lock_payload["update"]["update_status"] == "updated"
    assert lock_payload["support"]["materialized_paths"] == ["skills/support/generated/agent-browser"]
    assert lock_payload["doctor"]["doctor_status"] == "ok"


def test_tool_doctor_records_npm_provenance(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    npm_script, _ = make_fake_npm_gws(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{npm_script.parent}:{(npm_script.parent.parent / 'npm-global' / 'bin')}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(repo_root, "tool", "doctor", "--repo-root", str(repo_root), "--json", "gws-cli", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    gws = payload["results"]["gws-cli"]["doctor"]
    assert gws["doctor_status"] == "ok"
    assert gws["provenance"]["install_method"] == "npm"
    assert gws["provenance"]["package_name"] == "@googleworkspace/cli"
    assert gws["release"]["latest_tag"] == "v0.22.5"


def test_tool_update_routes_brew_provenance_for_specdown(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    brew_script, _ = make_fake_brew_specdown(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{brew_script.parent}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "update",
        "--repo-root",
        str(repo_root),
        "--json",
        "--skip-sync-support",
        "specdown",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    specdown = payload["results"]["specdown"]
    assert specdown["update"]["status"] == "updated"
    assert specdown["update"]["mode"] == "package_manager"
    assert specdown["update"]["package_manager"] == "brew"
    assert specdown["update"]["package_name"] == "corca-ai/tap/specdown"
    assert specdown["doctor"]["provenance"]["install_method"] == "brew"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "specdown.json").read_text(encoding="utf-8"))
    assert lock_payload["provenance"]["install_method"] == "brew"
    assert lock_payload["update"]["mode"] == "package_manager"
    assert lock_payload["update"]["package_name"] == "corca-ai/tap/specdown"


def test_tool_update_routes_npm_provenance_for_gws(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    npm_script, _ = make_fake_npm_gws(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{npm_script.parent}:{(npm_script.parent.parent / 'npm-global' / 'bin')}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "update",
        "--repo-root",
        str(repo_root),
        "--json",
        "--skip-sync-support",
        "gws-cli",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    gws = payload["results"]["gws-cli"]
    assert gws["update"]["status"] == "updated"
    assert gws["update"]["mode"] == "package_manager"
    assert gws["update"]["package_manager"] == "npm"
    assert gws["update"]["package_name"] == "@googleworkspace/cli"
    assert gws["doctor"]["provenance"]["install_method"] == "npm"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "gws-cli.json").read_text(encoding="utf-8"))
    assert lock_payload["provenance"]["install_method"] == "npm"
    assert lock_payload["update"]["package_name"] == "@googleworkspace/cli"
