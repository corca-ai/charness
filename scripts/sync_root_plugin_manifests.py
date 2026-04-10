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
    checked_in_plugin_root,
    expected_root_artifacts,
    export_plugin_tree,
    load_manifest,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the checked-in plugin install surface and root marketplace files from the shared packaging manifest."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-id", default="charness")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest = load_manifest(repo_root, args.package_id)
    written_paths: list[str] = []
    removed_paths: list[str] = []
    plugin_root = repo_root / checked_in_plugin_root(manifest)
    if plugin_root.exists():
        shutil.rmtree(plugin_root)
    export_plugin_tree(repo_root, plugin_root, manifest)
    written_paths.append(str(plugin_root.relative_to(repo_root)))
    for stale_path in (repo_root / ".claude-plugin" / "plugin.json", repo_root / ".codex-plugin" / "plugin.json"):
        if stale_path.exists():
            stale_path.unlink()
            removed_paths.append(str(stale_path.relative_to(repo_root)))
    for rel_path, payload in expected_root_artifacts(manifest):
        write_json(repo_root / rel_path, payload)
        written_paths.append(rel_path)

    print(
        json.dumps(
            {"package_id": args.package_id, "written_paths": written_paths, "removed_paths": removed_paths},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PackagingError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
