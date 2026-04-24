from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

from .support import (
    build_test_path,
    clone_seeded_managed_home,
    make_fake_agent_browser,
    make_fake_go_specdown,
    make_fake_npm_gws,
    make_release_fixture,
    make_repo_copy,
    make_support_sync_fixture,
    run_cli,
    run_cli_in_repo,
)
from .tool_fakes import make_fake_cautilus


def make_fake_go_glow(tmp_path: Path) -> tuple[Path, Path]:
    gopath = tmp_path / "go"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "go"
    script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import os
            import pathlib
            import sys

            gopath = pathlib.Path({str(gopath)!r})
            gobin = os.environ.get("GOBIN")
            install_root = pathlib.Path(gobin) if gobin else gopath / "bin"
            install_root.mkdir(parents=True, exist_ok=True)

            args = sys.argv[1:]
            if args == ["version"]:
                print("go version go1.26.2 linux/arm64")
                raise SystemExit(0)
            if args == ["env", "GOPATH"]:
                print(gopath)
                raise SystemExit(0)
            if args == ["install", "github.com/charmbracelet/glow/v2@latest"]:
                glow = gopath / "bin" / "glow"
                glow.write_text(
                    "\\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "import sys",
                            "args = sys.argv[1:]",
                            "if args == ['--version']:",
                            "    print('glow 2.1.1-test')",
                            "    raise SystemExit(0)",
                            "if args == ['--help']:",
                            "    print('glow help')",
                            "    raise SystemExit(0)",
                            "print('glow runtime')",
                        ]
                    ) + "\\n",
                    encoding="utf-8",
                )
                glow.chmod(0o755)
                target = install_root / "glow"
                if target != glow:
                    if target.exists() or target.is_symlink():
                        target.unlink()
                    target.symlink_to(glow)
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script, gopath


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
    assert cautilus["install"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.sh"
    assert cautilus["install"]["release"]["latest_tag"] == "v1.2.3"
    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["skills/support/generated/cautilus"]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert cautilus["doctor"]["doctor_disposition"] == "advisory-install-needed"
    assert cautilus["install"]["repo_followup"]["rendered_command"] == f"cautilus install --repo-root {repo_root}"
    assert cautilus["doctor"]["install_route"]["repo_followup"]["rendered_command"] == (
        f"cautilus install --repo-root {repo_root}"
    )
    assert cautilus["doctor"]["release"]["latest_version"] == "1.2.3"
    assert "Follow-up command: `cautilus install --repo-root" in cautilus["next_step"]
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
    assert cautilus["install"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.sh"
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
    assert cautilus["support_discovery"]["intent_triggers"] == [
        "verify",
        "verification",
        "evaluate",
        "evaluation",
        "review",
        "behavior review",
        "closeout",
        "issue closeout",
        "operator reading test",
        "검증",
        "평가",
        "리뷰",
    ]
    assert cautilus["support_discovery"]["support_skill_path"] == "skills/support/generated/cautilus/SKILL.md"
    assert cautilus["support_discovery"]["discovery_stub_path"] == ".agents/charness-discovery/cautilus.md"
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
    assert cautilus["support"]["discovery_stub_path"] == ".agents/charness-discovery/cautilus.md"
    assert cautilus["support"]["intent_triggers"] == [
        "verify",
        "verification",
        "evaluate",
        "evaluation",
        "review",
        "behavior review",
        "closeout",
        "issue closeout",
        "operator reading test",
        "검증",
        "평가",
        "리뷰",
    ]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert cautilus["doctor"]["doctor_disposition"] == "advisory-install-needed"
    assert cautilus["doctor"]["install_route"]["mode"] == "manual"
    assert cautilus["doctor"]["install_route"]["docs_url"] == "https://github.com/corca-ai/cautilus"
    assert cautilus["doctor"]["install_route"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.sh"
    assert cautilus["doctor"]["install_route"]["repo_followup"]["rendered_command"] == (
        f"cautilus install --repo-root {home_root / '.agents' / 'src' / 'charness'}"
    )
    assert cautilus["doctor"]["support_discovery"]["status"] == "materialized"
    assert cautilus["doctor"]["support_discovery"]["support_skill_path"] == "skills/support/generated/cautilus/SKILL.md"
    assert cautilus["doctor"]["support_discovery"]["discovery_stub_path"] == ".agents/charness-discovery/cautilus.md"
    assert cautilus["doctor"]["install_route"]["commands"] == []
    assert "Support skill materialization for `cautilus` was refreshed under skills/support/generated/cautilus" in cautilus["next_step"]
    assert "the standalone binary is still missing" in cautilus["next_step"]
    assert "Install docs: https://github.com/corca-ai/cautilus/blob/main/install.sh" in cautilus["next_step"]
    assert "Docs: https://github.com/corca-ai/cautilus" in cautilus["next_step"]
    assert "Support skill is available at `skills/support/generated/cautilus/SKILL.md`." in cautilus["next_step"]
    assert "Repo-local discovery stub is available at `.agents/charness-discovery/cautilus.md` for host-repo grep and cold-start pickup." in cautilus["next_step"]
    assert "Use `find-skills` to surface it on demand or inspect that path directly." in cautilus["next_step"]
    assert "You can also grep the discovery stub from the host repo." in cautilus["next_step"]
    assert "Follow-up command: `cautilus install --repo-root" in cautilus["next_step"]


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


def test_tool_doctor_reports_specdown_binary_contract_without_support_sync(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    go_script, specdown_script = make_fake_go_specdown(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(go_script.parent, specdown_script.parent)
    env["GOPATH"] = str(specdown_script.parent.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(repo_root, "tool", "doctor", "--repo-root", str(repo_root), "--json", "specdown", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    specdown = payload["results"]["specdown"]
    doctor = specdown["doctor"]

    assert doctor["doctor_status"] == "ok"
    assert doctor["support_state"] == "integration-only"
    assert doctor["support_sync"]["status"] == "not-tracked"
    assert doctor["detect"]["results"][0]["command"] == "specdown version"
    assert doctor["healthcheck"]["results"][0]["command"] == "specdown run -help"
    assert doctor["provenance"]["install_method"] == "go"
    assert doctor["provenance"]["package_name"] == "github.com/corca-ai/specdown/cmd/specdown"
    assert doctor["release"]["latest_tag"] == "v0.47.2"


def test_tool_install_executes_glow_install_script_and_refreshes_doctor(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    fake_go, gopath = make_fake_go_glow(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(fake_go.parent, home_root / ".local" / "bin")
    env["GOPATH"] = str(gopath)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(repo_root, "tool", "install", "--repo-root", str(repo_root), "--json", "glow", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    glow = payload["results"]["glow"]

    assert glow["install"]["status"] == "installed"
    assert glow["install"]["mode"] == "script"
    assert glow["doctor"]["doctor_status"] == "ok"
    assert glow["doctor"]["provenance"]["install_method"] == "go"
    assert glow["doctor"]["provenance"]["package_name"] == "github.com/charmbracelet/glow/v2"
    assert glow["doctor"]["release"]["latest_tag"] == "v2.1.2"
    assert (home_root / ".local" / "bin" / "glow").is_symlink()
    assert (gopath / "bin" / "glow").is_file()


def test_tool_update_routes_go_provenance_for_specdown(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    go_script, specdown_script = make_fake_go_specdown(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path(go_script.parent, specdown_script.parent)
    env["GOPATH"] = str(specdown_script.parent.parent)
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
    assert specdown["update"]["package_manager"] == "go"
    assert specdown["update"]["package_name"] == "github.com/corca-ai/specdown/cmd/specdown"
    assert specdown["doctor"]["provenance"]["install_method"] == "go"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "specdown.json").read_text(encoding="utf-8"))
    assert lock_payload["provenance"]["install_method"] == "go"
    assert lock_payload["update"]["mode"] == "package_manager"
    assert lock_payload["update"]["package_name"] == "github.com/corca-ai/specdown/cmd/specdown"


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
