#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

FAIL_PLUGIN_INSTALL = (
    os.environ.get("CHARNESS_FAKE_CODEX_FAIL_PLUGIN_INSTALL") == "1"
    or Path(sys.argv[0]).with_name(".codex-fail-plugin-install").exists()
)
APP_SERVER_MODE = os.environ.get("CHARNESS_FAKE_CODEX_APP_SERVER_MODE", "success")


def load_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def plugin_source_from_marketplace(marketplace_path: Path, plugin_name: str):
    data = load_json(marketplace_path, {})
    marketplace_name = data.get("name")
    for plugin in data.get("plugins", []):
        if isinstance(plugin, dict) and plugin.get("name") == plugin_name:
            source = plugin.get("source", {})
            raw_path = source.get("path")
            if isinstance(raw_path, str):
                source_path = (marketplace_path.parent.parent.parent / raw_path.removeprefix("./")).resolve()
                return marketplace_name, source_path
    raise SystemExit(2)


def plugin_version(source_path: Path):
    manifest_path = source_path / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path, {})
    version = manifest.get("version")
    return version if isinstance(version, str) and version else "local"


def install_plugin(codex_home: Path, marketplace_path: Path, plugin_name: str):
    marketplace_name, source_path = plugin_source_from_marketplace(marketplace_path, plugin_name)
    version = plugin_version(source_path)
    target = codex_home / "plugins" / "cache" / marketplace_name / plugin_name / version
    base_root = target.parent
    if base_root.exists():
        shutil.rmtree(base_root)
    shutil.copytree(source_path, target)
    config_path = codex_home / "config.toml"
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    plugin_key = f"{plugin_name}@{marketplace_name}"
    if f'[plugins."{plugin_key}"]' not in existing:
        existing = existing.rstrip() + ("\n\n" if existing.strip() else "") + f'[plugins."{plugin_key}"]\nenabled = true\n'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(existing, encoding="utf-8")
    return version


args = sys.argv[1:]
if args == ["--help"]:
    print("Codex CLI")
    raise SystemExit(0)
if args[:3] == ["app-server", "--listen", "stdio://"]:
    codex_home = Path(os.environ["CODEX_HOME"])
    for raw in sys.stdin:
        message = json.loads(raw)
        method = message.get("method")
        req_id = message.get("id")
        if method == "initialize":
            if APP_SERVER_MODE == "malformed":
                print("not-json", flush=True)
                continue
            if APP_SERVER_MODE == "eof":
                raise SystemExit(0)
            if APP_SERVER_MODE == "initialize-error":
                print(
                    json.dumps(
                        {
                            "id": req_id,
                            "error": {"code": -32000, "message": "forced initialize failure"},
                        }
                    ),
                    flush=True,
                )
                continue
            if APP_SERVER_MODE == "unrelated-stream":
                for value in range(20):
                    print(json.dumps({"id": 100 + value, "result": {}}), flush=True)
                    time.sleep(0.015)
                continue
            print(
                json.dumps(
                    {
                        "id": req_id,
                        "result": (
                            {
                                "userAgent": "fake-codex/0.144.5",
                                "codexHome": str(codex_home),
                                "platformFamily": "unix",
                                "platformOs": "linux",
                            }
                            if APP_SERVER_MODE == "real-init-notifications"
                            else {
                                "serverInfo": {"name": "fake-codex-app-server", "version": "0.0.0"},
                                "capabilities": {},
                            }
                        ),
                    }
                ),
                flush=True,
            )
            if APP_SERVER_MODE == "real-init-notifications":
                print(
                    json.dumps(
                        {
                            "method": "configWarning",
                            "params": {"summary": "sandbox fallback active"},
                        }
                    ),
                    flush=True,
                )
                print(
                    json.dumps(
                        {
                            "method": "remoteControl/status/changed",
                            "params": {"status": "disabled", "installationId": "fake-installation"},
                        }
                    ),
                    flush=True,
                )
            continue
        if method == "notifications/initialized":
            continue
        if method == "plugin/install":
            if FAIL_PLUGIN_INSTALL:
                print(
                    json.dumps(
                        {
                            "id": req_id,
                            "error": {"code": -32000, "message": "forced plugin/install failure"},
                        }
                    ),
                    flush=True,
                )
                continue
            params = message.get("params", {})
            version = install_plugin(codex_home, Path(params["marketplacePath"]), params["pluginName"])
            print(
                json.dumps(
                    {
                        "id": req_id,
                        "result": {"authPolicy": "ON_INSTALL", "appsNeedingAuth": [], "version": version},
                    }
                ),
                flush=True,
            )
            continue
    raise SystemExit(0)
raise SystemExit(0)
