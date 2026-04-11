from __future__ import annotations

import json
import os
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


def test_charness_init_exports_managed_surface(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    fake_claude = make_fake_claude(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
    result = run_cli(
        "init",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["plugin_root"] == str(home_root / ".codex" / "plugins" / "charness")
    assert payload["cli_path"] == str(home_root / ".local" / "bin" / "charness")
    assert payload["claude_wrapper_path"] == str(home_root / ".local" / "bin" / "claude-charness")
    assert payload["checkout"]["repo_root"] == str(ROOT)
    assert (
        payload["next_steps"]["codex"]
        == "Restart Codex from the home root so it reloads the personal marketplace. If `charness` is still unavailable, install or enable it from Plugin Directory."
    )
    assert payload["next_steps"]["claude"] == "Restart Claude Code to load charness."
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
        "--repo-root",
        str(ROOT),
        env=env,
    )
    assert init_result.returncode == 0, init_result.stderr

    doctor_result = run_cli(
        "doctor",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        "--json",
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["checkout_present"] is True
    assert payload["plugin_root_present"] is True
    assert payload["cli_present"] is True
    assert payload["claude_wrapper_present"] is True
    assert payload["codex_marketplace_entry"]["name"] == "charness"
    assert payload["codex_marketplace_entry"]["source"]["path"] == "./.codex/plugins/charness"
    assert payload["codex_host_guidance"]["status"] == "needs-host-install"
    assert payload["codex_host_guidance"]["manual_action_required"] is True
    assert (
        payload["codex_host_guidance"]["message"]
        == "Restart Codex from the home directory that owns "
        f"`{home_root / '.agents' / 'plugins' / 'marketplace.json'}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
    )
    assert payload["claude_marketplace_name"] == "corca-charness"
    assert payload["claude_plugin_ref"] == "charness@corca-charness"
    assert payload["claude_marketplace_entry"]["source"]["path"] == str(ROOT)
    assert payload["claude_installed_entry"]["version"] == "local"
    assert payload["claude_host_guidance"]["status"] == "installed"
    assert payload["claude_host_guidance"]["manual_action_required"] is False
    assert payload["claude_host_guidance"]["message"] == "Claude host install markers are present. Restart Claude Code to load or refresh charness."
    assert payload["plugin_preamble"]["update_hints"]["claude"] == "Run `charness update`, then restart Claude Code."


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
        "--repo-root",
        str(ROOT),
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
        "--repo-root",
        str(ROOT),
        "--json",
        env=env,
    )
    assert reset_result.returncode == 0, reset_result.stderr
    payload = json.loads(reset_result.stdout)
    assert payload["removed_plugin_root"] is True
    assert payload["removed_codex_marketplace_entry"] is True
    assert payload["removed_codex_cache"] is True
    assert payload["removed_codex_config_entries"] == ["charness@charness"]
    assert payload["removed_claude_plugin"] is True
    assert payload["removed_claude_marketplace"] is True
    assert payload["removed_cli"] is False
    assert payload["removed_checkout"] is False
    assert (home_root / ".local" / "bin" / "charness").is_file()
