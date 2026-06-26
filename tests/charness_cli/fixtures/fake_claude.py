#!/usr/bin/env python3
from __future__ import annotations

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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    ensure_marketplace("corca-charness", args[-1])
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
