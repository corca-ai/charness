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
    load_manifest,
    manifest_with_version_override,
    write_json,
)


class ExportError(Exception):
    pass


def copy_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src,
        dest,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache"),
    )


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
        write_json(
            marketplace_path,
            build_codex_marketplace(
                manifest,
                source_path=manifest["codex"]["repo_marketplace"]["default_source_path"],
            ),
        )

    return plugin_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a host plugin layout from the shared packaging manifest.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-id", default="charness")
    parser.add_argument("--host", choices=("claude", "codex"), required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--with-marketplace", action="store_true")
    parser.add_argument(
        "--version-override",
        help="Override the exported package version without mutating the shared packaging manifest.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()
    try:
        manifest = load_manifest(repo_root, args.package_id)
    except PackagingError as exc:
        raise ExportError(str(exc)) from exc
    manifest = manifest_with_version_override(manifest, args.version_override)
    plugin_root = export_plugin(repo_root, output_root, manifest, args.host, args.with_marketplace)

    print(
        json.dumps(
            {
                "package_id": args.package_id,
                "host": args.host,
                "version": manifest["version"],
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
