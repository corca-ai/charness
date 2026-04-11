from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path


def write_fake_claude(root: Path) -> Path:
    bin_dir = root / "bin"
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

            def ensure_marketplace(source: str):
                data = load_json(known_marketplaces_path, {})
                data["corca-charness"] = {
                    "source": {"source": "path", "path": source},
                    "installLocation": str(home / ".claude" / "plugins" / "marketplaces" / "corca-charness"),
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
                data.setdefault("plugins", {}).pop(plugin_ref, None)
                save_json(installed_plugins_path, data)

            args = sys.argv[1:]
            if args[:3] == ["plugins", "marketplace", "add"]:
                ensure_marketplace(args[-1])
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
                    print(f"  ❯ {plugin_ref}")
                    print(f"    Version: {entries[0].get('version', 'local')}")
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


def run_managed_cli_install(
    root: Path,
    *,
    run_command,
    expect_success,
    error_type,
) -> None:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="charness-eval-managed-home-") as tmpdir:
        home_root = Path(tmpdir)
        fake_claude = write_fake_claude(home_root)
        env = os.environ.copy()
        env["HOME"] = str(home_root)
        env["PATH"] = f"{fake_claude.parent}:{env.get('PATH', '')}"
        init_result = run_command(
            ["python3", "charness", "init", "--home-root", str(home_root), "--repo-root", str(root)],
            cwd=root,
            env=env,
        )
        expect_success(init_result, "managed cli init")
        init_payload = json.loads(init_result.stdout)
        plugin_root = home_root / ".codex" / "plugins" / "charness"
        marketplace_path = home_root / ".agents" / "plugins" / "marketplace.json"
        cli_path = home_root / ".local" / "bin" / "charness"
        claude_wrapper_path = home_root / ".local" / "bin" / "claude-charness"
        for path, label in (
            (plugin_root, "managed plugin root"),
            (marketplace_path, "managed codex marketplace"),
            (cli_path, "managed cli binary"),
            (claude_wrapper_path, "managed claude wrapper"),
        ):
            if not path.exists():
                raise error_type(f"managed cli init: missing {label}")
        if init_payload.get("plugin_root") != str(plugin_root):
            raise error_type(f"managed cli init: unexpected plugin_root {init_payload.get('plugin_root')!r}")
        expected_next_step = (
            "Restart Codex from the home directory that owns "
            f"`{marketplace_path}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
        )
        if init_payload.get("next_steps", {}).get("codex") != expected_next_step:
            raise error_type(f"managed cli init: unexpected Codex next step {init_payload!r}")
        doctor_result = run_command(
            ["python3", str(cli_path), "doctor", "--home-root", str(home_root), "--repo-root", str(root), "--json"],
            cwd=root,
            env=env,
        )
        expect_success(doctor_result, "managed cli doctor")
        doctor_payload = json.loads(doctor_result.stdout)
        if doctor_payload.get("plugin_root_present") is not True:
            raise error_type(f"managed cli doctor: unexpected plugin_root state {doctor_payload!r}")
        entry = doctor_payload.get("codex_marketplace_entry")
        if not isinstance(entry, dict):
            raise error_type(f"managed cli doctor: missing codex marketplace entry {doctor_payload!r}")
        source = entry.get("source", {})
        if not isinstance(source, dict) or source.get("path") != "./.codex/plugins/charness":
            raise error_type(f"managed cli doctor: unexpected codex source path {entry!r}")
        if doctor_payload.get("claude_wrapper_present") is not True:
            raise error_type(f"managed cli doctor: missing Claude wrapper {doctor_payload!r}")
        host_guidance = doctor_payload.get("codex_host_guidance")
        if not isinstance(host_guidance, dict) or host_guidance.get("status") != "needs-host-install":
            raise error_type(f"managed cli doctor: unexpected Codex host guidance {doctor_payload!r}")
        expected_guidance = (
            "Restart Codex from the home directory that owns "
            f"`{marketplace_path}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
        )
        if host_guidance.get("message") != expected_guidance:
            raise error_type(f"managed cli doctor: unexpected Codex guidance message {doctor_payload!r}")
        claude_guidance = doctor_payload.get("claude_host_guidance")
        if not isinstance(claude_guidance, dict) or claude_guidance.get("status") != "installed":
            raise error_type(f"managed cli doctor: unexpected Claude guidance {doctor_payload!r}")
