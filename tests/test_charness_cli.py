from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "charness"


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(CLI), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def make_repo_copy(tmp_path: Path) -> Path:
    repo_copy = tmp_path / "repo"
    shutil.copytree(ROOT, repo_copy)
    return repo_copy


def make_release_fixture(tmp_path: Path) -> Path:
    fixture = tmp_path / "release-fixtures.json"
    fixture.write_text(
        json.dumps(
            {
                "corca-ai/charness": {
                    "tag_name": "v0.1.0",
                    "html_url": "https://github.com/corca-ai/charness/releases/tag/v0.1.0",
                    "published_at": "2026-04-12T00:00:00Z",
                    "assets": [{"name": "charness"}],
                },
                "corca-ai/cautilus": {
                    "tag_name": "v1.2.3",
                    "html_url": "https://github.com/corca-ai/cautilus/releases/tag/v1.2.3",
                    "published_at": "2026-04-10T00:00:00Z",
                    "assets": [{"name": "cautilus-linux-amd64.tar.gz"}],
                },
                "vercel-labs/agent-browser": {
                    "tag_name": "v0.25.3",
                    "html_url": "https://github.com/vercel-labs/agent-browser/releases/tag/v0.25.3",
                    "published_at": "2026-04-07T02:11:00Z",
                    "assets": [{"name": "agent-browser-x86_64-unknown-linux-gnu.tar.gz"}],
                },
                "corca-ai/specdown": {
                    "tag_name": "v0.47.2",
                    "html_url": "https://github.com/corca-ai/specdown/releases/tag/v0.47.2",
                    "published_at": "2026-04-05T01:03:46Z",
                    "assets": [{"name": "specdown_0.47.2_linux_amd64.tar.gz"}],
                },
                "googleworkspace/cli": {
                    "tag_name": "v0.22.5",
                    "html_url": "https://github.com/googleworkspace/cli/releases/tag/v0.22.5",
                    "published_at": "2026-03-31T18:53:24Z",
                    "assets": [{"name": "google-workspace-cli-x86_64-unknown-linux-gnu.tar.gz"}],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return fixture


def run_cli_in_repo(repo_root: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(repo_root / "charness"), *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def make_fake_claude(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "claude"
    script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import os
            import sys
            from pathlib import Path

            home = Path(os.environ["HOME"])
            plugins_root = home / ".claude" / "plugins"
            plugins_root.mkdir(parents=True, exist_ok=True)
            known_marketplaces_path = plugins_root / "known_marketplaces.json"
            installed_plugins_path = plugins_root / "installed_plugins.json"

            def load_json(path: Path, default):
                if not path.exists():
                    return default
                return json.loads(path.read_text(encoding="utf-8"))

            def save_json(path: Path, payload):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

            def ensure_marketplace(name: str, source: str):
                data = load_json(known_marketplaces_path, {})
                data[name] = {
                    "source": {"source": "path", "path": source},
                    "installLocation": str(home / ".claude" / "plugins" / "marketplaces" / name),
                }
                save_json(known_marketplaces_path, data)

            def ensure_installed(plugin_ref: str):
                plugin, marketplace = plugin_ref.split("@", 1)
                data = load_json(installed_plugins_path, {"version": 2, "plugins": {}})
                plugins = data.setdefault("plugins", {})
                install_path = home / ".claude" / "plugins" / "cache" / marketplace / plugin / "local"
                install_path.mkdir(parents=True, exist_ok=True)
                plugins[plugin_ref] = [
                    {
                        "scope": "user",
                        "installPath": str(install_path),
                        "version": "local",
                        "installedAt": "2026-04-11T00:00:00.000Z",
                        "lastUpdated": "2026-04-11T00:00:00.000Z",
                    }
                ]
                save_json(installed_plugins_path, data)

            def uninstall(plugin_ref: str):
                data = load_json(installed_plugins_path, {"version": 2, "plugins": {}})
                plugins = data.setdefault("plugins", {})
                plugins.pop(plugin_ref, None)
                save_json(installed_plugins_path, data)

            args = sys.argv[1:]
            if args == ["--version"]:
                print("fake-claude 0.0.0")
                raise SystemExit(0)
            if args[:3] == ["plugins", "marketplace", "add"]:
                source = args[-1]
                ensure_marketplace("corca-charness", source)
                raise SystemExit(0)
            if args[:3] == ["plugins", "marketplace", "update"]:
                raise SystemExit(0)
            if args[:3] == ["plugins", "marketplace", "remove"]:
                data = load_json(known_marketplaces_path, {})
                data.pop(args[-1], None)
                save_json(known_marketplaces_path, data)
                raise SystemExit(0)
            if args[:2] == ["plugins", "install"]:
                ensure_installed(args[-1])
                raise SystemExit(0)
            if args[:2] == ["plugins", "update"]:
                ensure_installed(args[-1])
                raise SystemExit(0)
            if args[:2] == ["plugins", "enable"]:
                raise SystemExit(0)
            if args[:2] == ["plugins", "uninstall"]:
                uninstall(args[-1])
                raise SystemExit(0)
            if args[:2] == ["plugins", "list"]:
                data = load_json(installed_plugins_path, {"version": 2, "plugins": {}})
                print("Installed plugins:")
                print("")
                for plugin_ref, entries in data.get("plugins", {}).items():
                    version = entries[0].get("version", "local")
                    print(f"  ❯ {plugin_ref}")
                    print(f"    Version: {version}")
                    print("    Scope: user")
                    print("    Status: ✔ enabled")
                    print("")
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def make_fake_agent_browser(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "agent-browser"
    script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("agent-browser 0.25.3")
                raise SystemExit(0)
            if args == ["--help"]:
                print("agent-browser")
                raise SystemExit(0)
            if args == ["upgrade"]:
                print("upgraded")
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def make_fake_brew_specdown(tmp_path: Path) -> tuple[Path, Path]:
    brew_root = tmp_path / "linuxbrew"
    bin_dir = brew_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    brew_script = bin_dir / "brew"
    brew_script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["--prefix"]:
                print({str(brew_root)!r})
                raise SystemExit(0)
            if args == ["upgrade", "corca-ai/tap/specdown"]:
                print("upgraded specdown")
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    brew_script.chmod(0o755)
    specdown_script = bin_dir / "specdown"
    specdown_script.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["version"]:
                print("0.47.2")
                raise SystemExit(0)
            if args == ["run", "-help"]:
                print("Usage: specdown run", file=sys.stderr)
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    specdown_script.chmod(0o755)
    return brew_script, specdown_script


def make_fake_npm_gws(tmp_path: Path) -> tuple[Path, Path]:
    npm_prefix = tmp_path / "npm-global"
    bin_dir = npm_prefix / "bin"
    package_bin = npm_prefix / "lib" / "node_modules" / "@googleworkspace" / "cli"
    bin_dir.mkdir(parents=True, exist_ok=True)
    package_bin.mkdir(parents=True, exist_ok=True)
    npm_script = tmp_path / "bin" / "npm"
    npm_script.parent.mkdir(parents=True, exist_ok=True)
    npm_script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys

            args = sys.argv[1:]
            if args == ["prefix", "-g"]:
                print({str(npm_prefix)!r})
                raise SystemExit(0)
            if args == ["install", "-g", "@googleworkspace/cli@latest"]:
                print("updated @googleworkspace/cli")
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    npm_script.chmod(0o755)
    gws_impl = package_bin / "run-gws.js"
    gws_impl.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import sys

            args = sys.argv[1:]
            if args == ["--version"]:
                print("gws 0.18.1")
                print("This is not an officially supported Google product.")
                raise SystemExit(0)
            if args == ["auth", "--help"]:
                print("login")
                raise SystemExit(0)
            if args == ["auth", "status"]:
                print(json.dumps({"token_valid": True}))
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    gws_impl.chmod(0o755)
    gws_link = bin_dir / "gws"
    gws_link.symlink_to(gws_impl)
    return npm_script, gws_link


def test_charness_init_exports_managed_surface(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    legacy_skills = home_root / ".agents" / "skills"
    legacy_skills.parent.mkdir(parents=True, exist_ok=True)
    legacy_skills.symlink_to(ROOT / "skills" / "public", target_is_directory=True)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["plugin_root"] == str(home_root / ".codex" / "plugins" / "charness")
    assert payload["cli_path"] == str(home_root / ".local" / "bin" / "charness")
    assert payload["claude_wrapper_path"] == str(home_root / ".local" / "bin" / "claude-charness")
    assert payload["checkout"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["checkout"]["managed"] is True
    assert (
        payload["next_steps"]["codex"]
        == "Restart Codex from the home directory that owns "
        f"`{home_root / '.agents' / 'plugins' / 'marketplace.json'}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
    )
    assert payload["next_steps"]["claude"] == "Restart Claude Code to load charness."
    assert payload["removed_legacy_skills_symlink"] is True
    assert "legacy_skills_symlink_removed" in payload["completed_actions"]
    marketplace = json.loads((home_root / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
    plugin_entry = marketplace["plugins"][0]
    assert plugin_entry["name"] == "charness"
    assert plugin_entry["source"]["path"] == "./.codex/plugins/charness"
    known_marketplaces = json.loads((home_root / ".claude" / "plugins" / "known_marketplaces.json").read_text(encoding="utf-8"))
    assert "corca-charness" in known_marketplaces
    installed_plugins = json.loads((home_root / ".claude" / "plugins" / "installed_plugins.json").read_text(encoding="utf-8"))
    assert "charness@corca-charness" in installed_plugins["plugins"]
    assert (home_root / ".local" / "bin" / "charness").is_file()
    assert (home_root / ".local" / "bin" / "claude-charness").is_file()
    assert legacy_skills.exists() is False
    assert legacy_skills.is_symlink() is False


def test_charness_doctor_reports_managed_surface(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr

    doctor_result = run_cli(
        "doctor",
        "--home-root",
        str(home_root),
        "--json",
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["install_state_path"] == str(home_root / ".local" / "share" / "charness" / "install-state.json")
    assert payload["host_state_path"] == str(home_root / ".local" / "share" / "charness" / "host-state.json")
    assert payload["version_state_path"] == str(home_root / ".local" / "share" / "charness" / "version-state.json")
    assert payload["checkout_present"] is True
    assert payload["plugin_root_present"] is True
    assert payload["cli_present"] is True
    assert payload["claude_wrapper_present"] is True
    assert payload["codex_marketplace_entry"]["name"] == "charness"
    assert payload["codex_marketplace_entry"]["source"]["path"] == "./.codex/plugins/charness"
    assert payload["legacy_skills_symlink_present"] is False
    assert payload["codex_source_version"] == "0.0.0-dev"
    assert payload["codex_cache_manifest_version"] is None
    assert payload["codex_source_cache_drift"] is False
    assert payload["codex_host_guidance"]["status"] == "needs-host-install"
    assert payload["codex_host_guidance"]["manual_action_required"] is True
    assert (
        payload["codex_host_guidance"]["message"]
        == "Restart Codex from the home directory that owns "
        f"`{home_root / '.agents' / 'plugins' / 'marketplace.json'}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
    )
    assert payload["claude_marketplace_name"] == "corca-charness"
    assert payload["claude_plugin_ref"] == "charness@corca-charness"
    assert payload["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["managed_checkout"] is True
    assert payload["claude_marketplace_entry"]["source"]["path"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["claude_installed_entry"]["version"] == "local"
    assert payload["claude_host_guidance"]["status"] == "installed"
    assert payload["claude_host_guidance"]["manual_action_required"] is False
    assert payload["claude_host_guidance"]["message"] == "Claude host install markers are present. Restart Claude Code to load or refresh charness."
    assert payload["plugin_preamble"]["update_hints"]["claude"] == "Run `charness update`, then restart Claude Code."
    assert payload["version_provenance"]["invocation_kind"] == "custom-cli"
    assert payload["latest_release_check"] is None
    host_state = json.loads((home_root / ".local" / "share" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["state_version"] == 1
    assert host_state["last_init"]["doctor"]["codex_host_guidance"]["status"] == "needs-host-install"
    assert host_state["last_init"]["doctor"]["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert isinstance(host_state["last_init"]["recorded_at"], str)


def test_charness_doctor_reports_codex_version_drift(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    doctor_result = run_cli(
        "doctor",
        "--home-root",
        str(home_root),
        "--json",
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["codex_source_version"] == "0.0.0-dev"
    assert payload["codex_cache_manifest_version"] == "0.0.0-old"
    assert payload["codex_source_cache_drift"] is True
    assert payload["codex_enabled_plugin_id"] == "charness@local"
    assert payload["codex_host_guidance"]["status"] == "needs-refresh"
    assert (
        payload["codex_host_guidance"]["message"]
        == "Codex still has installed charness cache version `0.0.0-old` while the source plugin root is `0.0.0-dev`. "
        "Restart Codex first. If `charness doctor` still shows drift, reopen Plugin Directory and reinstall or disable/re-enable the local `charness` entry."
    )


def test_charness_update_reports_codex_version_drift(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@local"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text('{"version":"0.0.0-old"}', encoding="utf-8")

    update_result = run_cli(
        "update",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert update_result.returncode == 0, update_result.stderr
    payload = json.loads(update_result.stdout)
    assert payload["codex_source_version"] == "0.0.0-dev"
    assert payload["codex_cache_manifest_version"] == "0.0.0-old"
    assert payload["codex_source_cache_drift"] is True
    assert (
        payload["next_steps"]["codex"]
        == "Codex still has installed charness cache version `0.0.0-old` while the source plugin root is `0.0.0-dev`. "
        "Restart Codex first. If `charness doctor` still shows drift, reopen Plugin Directory and reinstall or disable/re-enable the local `charness` entry."
    )
    host_state = json.loads((home_root / ".local" / "share" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_update"]["doctor"]["codex_source_cache_drift"] is True
    assert host_state["last_update"]["doctor"]["codex_cache_manifest_version"] == "0.0.0-old"
    assert isinstance(host_state["last_update"]["recorded_at"], str)


def test_installed_cli_remembers_managed_checkout(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr
    installed_cli = home_root / ".local" / "bin" / "charness"
    doctor_result = subprocess.run(
        ["python3", str(installed_cli), "doctor", "--home-root", str(home_root), "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["checkout_present"] is True
    assert payload["managed_checkout"] is True
    assert payload["claude_host_guidance"]["status"] == "installed"


def test_charness_version_can_refresh_latest_release_and_record_provenance(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr

    installed_cli = home_root / ".local" / "bin" / "charness"
    version_result = subprocess.run(
        ["python3", str(installed_cli), "version", "--home-root", str(home_root), "--json", "--check"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert version_result.returncode == 0, version_result.stderr
    payload = json.loads(version_result.stdout)
    assert payload["current_version"] == "0.0.0-dev"
    assert payload["version_provenance"]["invocation_kind"] == "installed-cli"
    assert payload["version_provenance"]["install_method"] == "managed-local-cli"
    assert payload["latest_release_check"]["latest_tag"] == "v0.1.0"
    assert payload["latest_release_check"]["update_available"] is True
    assert payload["update_notice"] == (
        "charness update available: `0.0.0-dev` -> `v0.1.0`. "
        "Run `charness update`. https://github.com/corca-ai/charness/releases/tag/v0.1.0"
    )
    version_state = json.loads((home_root / ".local" / "share" / "charness" / "version-state.json").read_text(encoding="utf-8"))
    assert version_state["version_provenance"]["invocation_kind"] == "installed-cli"
    assert version_state["latest_release"]["latest_tag"] == "v0.1.0"
    assert version_state["latest_release"]["current_version"] == "0.0.0-dev"


def test_installed_cli_can_emit_auto_update_notice(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_FORCE_UPDATE_CHECK"] = "1"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr

    installed_cli = home_root / ".local" / "bin" / "charness"
    doctor_result = subprocess.run(
        ["python3", str(installed_cli), "doctor", "--home-root", str(home_root)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    assert "charness update available: `0.0.0-dev` -> `v0.1.0`." in doctor_result.stderr


def test_doctor_can_write_host_state_snapshot(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr

    doctor_result = run_cli(
        "doctor",
        "--home-root",
        str(home_root),
        "--json",
        "--write-state",
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    host_state = json.loads((home_root / ".local" / "share" / "charness" / "host-state.json").read_text(encoding="utf-8"))
    assert host_state["last_doctor"]["doctor"]["repo_root"] == payload["repo_root"]
    assert host_state["last_doctor"]["doctor"]["codex_source_version"] == payload["codex_source_version"]
    assert isinstance(host_state["last_doctor"]["recorded_at"], str)


def test_non_managed_repo_root_requires_skip_cli_install(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        env=env,
    )
    assert init_result.returncode != 0
    assert (
        "official charness installs must use the managed checkout" in init_result.stderr
        or "official charness installs must use the managed checkout" in init_result.stdout
    )


def test_doctor_handles_missing_source_checkout_without_traceback(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    installed_cli = home_root / ".local" / "bin" / "charness"
    installed_cli.parent.mkdir(parents=True, exist_ok=True)
    installed_cli.write_text(CLI.read_text(encoding="utf-8"), encoding="utf-8")
    installed_cli.chmod(0o755)

    doctor_result = subprocess.run(
        ["python3", str(installed_cli), "doctor", "--home-root", str(home_root), "--json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["repo_root"] == str(home_root / ".agents" / "src" / "charness")
    assert payload["checkout_present"] is False
    assert payload["plugin_preamble"] is None
    assert payload["claude_host_guidance"]["status"] == "missing-source"
    assert payload["claude_host_guidance"]["message"] == (
        "No managed charness source checkout was found for this CLI. Run `charness init` from a checkout or bootstrap `~/.agents/src/charness` again."
    )


def test_charness_reset_removes_host_state_but_keeps_cli(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    init_result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('[plugins."charness@charness"]\nenabled = true\n', encoding="utf-8")
    cache_manifest = home_root / ".codex" / "plugins" / "cache" / "charness" / "charness" / "local" / ".codex-plugin" / "plugin.json"
    cache_manifest.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest.write_text("{}", encoding="utf-8")

    reset_result = run_cli(
        "reset",
        "--home-root",
        str(home_root),
        "--json",
        env=env,
    )
    assert reset_result.returncode == 0, reset_result.stderr
    payload = json.loads(reset_result.stdout)
    assert payload["removed_plugin_root"] is True
    assert payload["removed_codex_marketplace_entry"] is True
    assert payload["removed_codex_cache"] is True
    assert payload["removed_legacy_skills_symlink"] is False
    assert payload["removed_codex_config_entries"] == ["charness@charness"]
    assert payload["removed_claude_plugin"] is True
    assert payload["removed_claude_marketplace"] is True
    assert payload["removed_cli"] is False
    assert payload["removed_checkout"] is False
    assert payload["removed_host_state"] is True
    assert (home_root / ".local" / "bin" / "charness").is_file()
    assert not (home_root / ".local" / "share" / "charness" / "host-state.json").exists()


def test_tool_install_persists_manual_guidance_and_support_state(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "install",
        "--repo-root",
        str(repo_root),
        "--json",
        "cautilus",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    cautilus = payload["results"]["cautilus"]
    assert cautilus["install"]["status"] == "manual"
    assert cautilus["install"]["docs_url"] == "https://github.com/corca-ai/cautilus"
    assert cautilus["install"]["release"]["latest_tag"] == "v1.2.3"
    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["skills/support/generated/cautilus/REFERENCE.md"]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert cautilus["doctor"]["release"]["latest_version"] == "1.2.3"
    assert "v1.2.3" in cautilus["next_step"]
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "cautilus.json").read_text(encoding="utf-8"))
    assert lock_payload["release"]["latest_tag"] == "v1.2.3"
    assert lock_payload["install"]["install_status"] == "manual"
    assert lock_payload["support"]["materialized_paths"] == ["skills/support/generated/cautilus/REFERENCE.md"]
    assert lock_payload["doctor"]["doctor_status"] == "missing"
    assert (repo_root / "skills" / "support" / "generated" / "cautilus" / "REFERENCE.md").is_file()


def test_tool_update_executes_scripted_updates_and_refreshes_doctor(tmp_path: Path) -> None:
    repo_root = make_repo_copy(tmp_path)
    home_root = tmp_path / "home"
    fake_agent_browser = make_fake_agent_browser(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_agent_browser.parent}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "update",
        "--repo-root",
        str(repo_root),
        "--json",
        "agent-browser",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    browser = payload["results"]["agent-browser"]
    assert browser["update"]["status"] == "updated"
    assert browser["update"]["release"]["latest_tag"] == "v0.25.3"
    assert browser["support"]["status"] == "synced"
    assert browser["doctor"]["doctor_status"] == "ok"
    assert "v0.25.3" in browser["next_step"]
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["release"]["latest_tag"] == "v0.25.3"
    assert lock_payload["update"]["update_status"] == "updated"
    assert lock_payload["support"]["materialized_paths"] == ["skills/support/generated/agent-browser/REFERENCE.md"]
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

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "doctor",
        "--repo-root",
        str(repo_root),
        "--json",
        "gws-cli",
        env=env,
    )
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
    assert "brew" in specdown["next_step"]
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
    assert "npm" in gws["next_step"]
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "gws-cli.json").read_text(encoding="utf-8"))
    assert lock_payload["provenance"]["install_method"] == "npm"
    assert lock_payload["update"]["package_name"] == "@googleworkspace/cli"
