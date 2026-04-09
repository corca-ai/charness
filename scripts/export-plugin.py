#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PACKAGING_PATH = REPO_ROOT / "scripts" / "validate-packaging.py"
VALIDATE_PACKAGING_SPEC = importlib.util.spec_from_file_location(
    "validate_packaging",
    VALIDATE_PACKAGING_PATH,
)
assert VALIDATE_PACKAGING_SPEC is not None and VALIDATE_PACKAGING_SPEC.loader is not None
VALIDATE_PACKAGING = importlib.util.module_from_spec(VALIDATE_PACKAGING_SPEC)
VALIDATE_PACKAGING_SPEC.loader.exec_module(VALIDATE_PACKAGING)


class ExportError(Exception):
    pass


def load_manifest(repo_root: Path, package_id: str) -> dict:
    manifest_path = repo_root / "packaging" / f"{package_id}.json"
    if not manifest_path.exists():
        raise ExportError(f"missing packaging manifest `{manifest_path}`")
    try:
        VALIDATE_PACKAGING.validate_packaging_manifest(manifest_path, repo_root)
    except Exception as exc:
        raise ExportError(str(exc)) from exc
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def copy_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def export_shared_sources(repo_root: Path, plugin_root: Path, source: dict) -> None:
    copy_file(repo_root / source["readme"], plugin_root / source["readme"])
    for field in (
        "skills_dir",
        "profiles_dir",
        "presets_dir",
        "integrations_dir",
    ):
        rel_path = source[field]
        copy_tree(repo_root / rel_path, plugin_root / rel_path)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_codex_marketplace(manifest: dict) -> dict:
    package_id = manifest["package_id"]
    repo_marketplace = manifest["codex"]["repo_marketplace"]
    return {
        "name": package_id,
        "interface": {
            "displayName": repo_marketplace["display_name"],
        },
        "plugins": [
            {
                "name": package_id,
                "source": {
                    "source": "local",
                    "path": repo_marketplace["default_source_path"],
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": repo_marketplace["category"],
            }
        ],
    }


def export_plugin(repo_root: Path, output_root: Path, manifest: dict, host: str, with_marketplace: bool) -> Path:
    package_id = manifest["package_id"]
    plugin_root = output_root / "plugins" / package_id
    if plugin_root.exists():
        shutil.rmtree(plugin_root)
    plugin_root.mkdir(parents=True, exist_ok=True)

    export_shared_sources(repo_root, plugin_root, manifest["source"])
    write_json(plugin_root / manifest[host]["manifest_path"], manifest[host]["manifest"])

    if host == "codex" and with_marketplace:
        marketplace_path = output_root / manifest["codex"]["repo_marketplace"]["path"]
        write_json(marketplace_path, build_codex_marketplace(manifest))

    return plugin_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a host plugin layout from the shared packaging manifest.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-id", default="charness")
    parser.add_argument("--host", choices=("claude", "codex"), required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--with-marketplace", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()
    manifest = load_manifest(repo_root, args.package_id)
    plugin_root = export_plugin(repo_root, output_root, manifest, args.host, args.with_marketplace)

    print(
        json.dumps(
            {
                "package_id": args.package_id,
                "host": args.host,
                "plugin_root": str(plugin_root),
                "marketplace_written": args.host == "codex" and args.with_marketplace,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ExportError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
