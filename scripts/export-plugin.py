#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_packaging_lib_module = import_repo_module(__file__, "scripts.packaging_lib")
PackagingError = _scripts_packaging_lib_module.PackagingError
build_codex_marketplace = _scripts_packaging_lib_module.build_codex_marketplace
checked_in_plugin_root = _scripts_packaging_lib_module.checked_in_plugin_root
export_plugin_tree = _scripts_packaging_lib_module.export_plugin_tree
load_manifest = _scripts_packaging_lib_module.load_manifest
manifest_with_version_override = _scripts_packaging_lib_module.manifest_with_version_override
write_json = _scripts_packaging_lib_module.write_json


class ExportError(Exception):
    pass


def export_plugin(repo_root: Path, output_root: Path, manifest: dict, host: str, with_marketplace: bool) -> Path:
    plugin_root = output_root / checked_in_plugin_root(manifest)
    if plugin_root.exists():
        shutil.rmtree(plugin_root)
    export_plugin_tree(repo_root, plugin_root, manifest)

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
