from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

from .support import (
    build_test_path,
    clone_seeded_managed_home,
    make_fake_agent_browser,
    make_fake_brew_specdown,
    make_fake_npm_gws,
    make_release_fixture,
    make_repo_copy,
    make_support_sync_fixture,
    run_cli,
    run_cli_in_repo,
)


def make_fake_cautilus(tmp_path: Path) -> Path:
    script = tmp_path / "bin" / "cautilus"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("cautilus 1.2.3")
                raise SystemExit(0)
            if args == ["doctor", "--help"]:
                print("cautilus doctor")
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_tool_install_persists_manual_guidance_and_support_state(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path()
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    result = run_cli_in_repo(repo_root, "tool", "install", "--repo-root", str(repo_root), "--json", "cautilus", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    cautilus = payload["results"]["cautilus"]
    assert cautilus["install"]["status"] == "manual"
    assert cautilus["install"]["docs_url"] == "https://github.com/corca-ai/cautilus"
    assert cautilus["install"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.md"
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


def test_installed_cli_tool_install_materializes_cautilus_support(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    result = run_cli("tool", "install", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    cautilus = payload["results"]["cautilus"]
    managed_repo = home_root / ".agents" / "src" / "charness"

    assert payload["managed_checkout"] is True
    assert payload["repo_root"] == str(managed_repo)
    assert cautilus["install"]["status"] == "manual"
    assert cautilus["install"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.md"
    assert cautilus["install"]["release"]["latest_tag"] == "v1.2.3"
    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["skills/support/generated/cautilus"]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert (managed_repo / "skills" / "support" / "generated" / "cautilus").is_symlink()

    lock_payload = json.loads((managed_repo / "integrations" / "locks" / "cautilus.json").read_text(encoding="utf-8"))
    assert lock_payload["install"]["install_status"] == "manual"
    assert lock_payload["support"]["materialized_paths"] == ["skills/support/generated/cautilus"]
    assert lock_payload["doctor"]["doctor_status"] == "missing"


def test_installed_cli_tool_doctor_reports_ok_for_cautilus_with_binary_and_support(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    fake_cautilus = make_fake_cautilus(tmp_path)
    env["PATH"] = build_test_path(fake_cautilus.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    sync_result = run_cli("tool", "sync-support", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert sync_result.returncode == 0, sync_result.stderr

    doctor_result = run_cli("tool", "doctor", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    cautilus = payload["results"]["cautilus"]["doctor"]

    assert cautilus["doctor_status"] == "ok"
    assert cautilus["support_state"] == "upstream-consumed"
    assert cautilus["support_sync"]["status"] == "ok"
    assert cautilus["support_discovery"]["status"] == "materialized"
    assert cautilus["support_discovery"]["support_skill_path"] == "skills/support/generated/cautilus/SKILL.md"
    assert cautilus["release"]["latest_tag"] == "v1.2.3"


def test_installed_cli_tool_sync_support_reports_materialized_support_and_binary_gap(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    sync_result = run_cli("tool", "sync-support", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert sync_result.returncode == 1, sync_result.stderr
    payload = json.loads(sync_result.stdout)
    cautilus = payload["results"]["cautilus"]

    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["skills/support/generated/cautilus"]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert cautilus["doctor"]["install_route"]["mode"] == "manual"
    assert cautilus["doctor"]["install_route"]["docs_url"] == "https://github.com/corca-ai/cautilus"
    assert cautilus["doctor"]["install_route"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.md"
    assert cautilus["doctor"]["support_discovery"]["status"] == "materialized"
    assert cautilus["doctor"]["support_discovery"]["support_skill_path"] == "skills/support/generated/cautilus/SKILL.md"
    assert cautilus["doctor"]["install_route"]["commands"] == []
    assert "Support skill materialization for `cautilus` was refreshed under skills/support/generated/cautilus" in cautilus["next_step"]
    assert "the standalone binary is still missing" in cautilus["next_step"]
    assert "Install docs: https://github.com/corca-ai/cautilus/blob/main/install.md" in cautilus["next_step"]
    assert "Docs: https://github.com/corca-ai/cautilus" in cautilus["next_step"]
    assert "Support skill is available at `skills/support/generated/cautilus/SKILL.md`." in cautilus["next_step"]
    assert "Use `find-skills` to surface it on demand or inspect that path directly." in cautilus["next_step"]


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
