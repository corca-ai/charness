#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.packaging_lib import (
    PackagingError,
    build_codex_marketplace,
    export_plugin_tree,
    load_manifest,
    write_json,
)


class InstallError(Exception):
    pass


def default_home_root() -> Path:
    return Path.home().resolve()


def default_plugin_root(home_root: Path, package_id: str) -> Path:
    return home_root / ".agents" / "plugins" / package_id


def default_codex_marketplace_path(home_root: Path) -> Path:
    return home_root / ".agents" / "plugins" / "marketplace.json"


def relative_source_path(home_root: Path, plugin_root: Path) -> str:
    try:
        relative = plugin_root.resolve().relative_to(home_root.resolve())
    except ValueError as exc:
        raise InstallError(
            f"plugin root `{plugin_root}` must stay under home root `{home_root}` so Codex can resolve a stable local path"
        ) from exc
    relative_str = relative.as_posix()
    return "." if relative_str == "." else f"./{relative_str}"


def load_marketplace(path: Path) -> dict:
    if not path.exists():
        return {
            "name": "local",
            "interface": {
                "displayName": "Local Plugins",
            },
            "plugins": [],
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InstallError(f"invalid JSON in `{path}`") from exc
    if not isinstance(data, dict):
        raise InstallError(f"`{path}` must contain a JSON object")
    plugins = data.get("plugins")
    if plugins is None:
        data["plugins"] = []
    elif not isinstance(plugins, list):
        raise InstallError(f"`{path}` field `plugins` must be a list")
    if "name" not in data:
        data["name"] = "local"
    interface = data.get("interface")
    if interface is None:
        data["interface"] = {"displayName": "Local Plugins"}
    elif not isinstance(interface, dict):
        raise InstallError(f"`{path}` field `interface` must be an object")
    elif "displayName" not in interface:
        interface["displayName"] = "Local Plugins"
    return data


def merge_codex_marketplace(marketplace: dict, plugin_entry: dict) -> dict:
    plugins = marketplace["plugins"]
    for index, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == plugin_entry["name"]:
            plugins[index] = plugin_entry
            break
    else:
        plugins.append(plugin_entry)
    return marketplace


def detect_hosts() -> dict[str, bool]:
    return {
        "codex": shutil.which("codex") is not None,
        "claude": shutil.which("claude") is not None,
    }


def ensure_source_checkout(repo_root: Path, package_id: str) -> None:
    manifest_path = repo_root / "packaging" / f"{package_id}.json"
    if manifest_path.exists():
        return
    if (repo_root / ".codex-plugin" / "plugin.json").exists():
        raise InstallError(
            "machine-local install must run from the source checkout, not the exported plugin root; "
            f"expected `{manifest_path}`"
        )
    raise InstallError(f"missing packaging manifest `{manifest_path}`")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export the checked-in charness plugin surface into a machine-local ~/.agents install root."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-id", default="charness")
    parser.add_argument("--home-root", type=Path, default=default_home_root())
    parser.add_argument(
        "--plugin-root",
        type=Path,
        help="Override the exported plugin root. Must stay under --home-root so Codex can resolve a relative local path.",
    )
    parser.add_argument(
        "--codex-marketplace-path",
        type=Path,
        help="Override the personal Codex marketplace path. Defaults to <home>/.agents/plugins/marketplace.json.",
    )
    parser.add_argument(
        "--skip-codex-marketplace",
        action="store_true",
        help="Export the plugin root without touching the personal Codex marketplace file.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    home_root = args.home_root.resolve()
    ensure_source_checkout(repo_root, args.package_id)

    try:
        manifest = load_manifest(repo_root, args.package_id)
    except PackagingError as exc:
        raise InstallError(str(exc)) from exc

    plugin_root = args.plugin_root.resolve() if args.plugin_root else default_plugin_root(home_root, args.package_id)
    source_path = relative_source_path(home_root, plugin_root)

    if plugin_root.exists():
        shutil.rmtree(plugin_root)
    export_plugin_tree(repo_root, plugin_root, manifest)

    marketplace_path = None
    if not args.skip_codex_marketplace:
        marketplace_path = (
            args.codex_marketplace_path.resolve()
            if args.codex_marketplace_path
            else default_codex_marketplace_path(home_root)
        )
        marketplace = load_marketplace(marketplace_path)
        plugin_entry = build_codex_marketplace(manifest, source_path=source_path)["plugins"][0]
        merge_codex_marketplace(marketplace, plugin_entry)
        write_json(marketplace_path, marketplace)

    detected_hosts = detect_hosts()
    print(
        json.dumps(
            {
                "package_id": args.package_id,
                "source_checkout": str(repo_root),
                "plugin_root": str(plugin_root),
                "codex_marketplace_path": str(marketplace_path) if marketplace_path else None,
                "codex_source_path": source_path,
                "claude_plugin_dir": str(plugin_root),
                "detected_hosts": detected_hosts,
                "next_steps": {
                    "codex": (
                        "Restart Codex from the home root so it reloads the personal marketplace and auto-installs charness by default."
                        if marketplace_path
                        else "Codex marketplace update skipped."
                    ),
                    "claude": f"Use `claude --plugin-dir {plugin_root}` to exercise the same exported install surface.",
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except InstallError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
