#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_packaging_lib_module = import_repo_module(__file__, "scripts.plugin_export.packaging_lib")
PackagingError = _scripts_packaging_lib_module.PackagingError
materialized_plugin_root = _scripts_packaging_lib_module.materialized_plugin_root
expected_root_artifacts = _scripts_packaging_lib_module.expected_root_artifacts
export_plugin_tree = _scripts_packaging_lib_module.export_plugin_tree
load_manifest = _scripts_packaging_lib_module.load_manifest
write_json = _scripts_packaging_lib_module.write_json


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(repo_root: Path, roots: list[Path]) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for root in roots:
        if root.is_file():
            snapshot[str(root.relative_to(repo_root))] = _digest(root)
        elif root.is_dir():
            for path in sorted(p for p in root.rglob("*") if p.is_file()):
                snapshot[str(path.relative_to(repo_root))] = _digest(path)
    return snapshot


def _change_summary(before: dict[str, str], after: dict[str, str]) -> dict[str, object]:
    before_paths = set(before)
    after_paths = set(after)
    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    changed = sorted(path for path in before_paths & after_paths if before[path] != after[path])
    unchanged = len(before_paths & after_paths) - len(changed)
    return {
        "added_paths": added,
        "changed_paths": changed,
        "removed_paths": removed,
        "unchanged_count": unchanged,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the materialized plugin export and root marketplace files from the shared packaging manifest."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-id", default="charness")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest = load_manifest(repo_root, args.package_id)
    written_paths: list[str] = []
    removed_paths: list[str] = []
    plugin_root = repo_root / materialized_plugin_root(manifest)
    root_artifact_paths = [
        repo_root / rel_path for rel_path, _payload in expected_root_artifacts(manifest)
    ]
    stale_manifest_paths = [
        repo_root / ".claude-plugin" / "plugin.json",
        repo_root / ".codex-plugin" / "plugin.json",
    ]
    before = _snapshot(repo_root, [plugin_root, *root_artifact_paths, *stale_manifest_paths])
    if plugin_root.exists():
        shutil.rmtree(plugin_root)
    export_plugin_tree(repo_root, plugin_root, manifest)
    written_paths.append(str(plugin_root.relative_to(repo_root)))
    for stale_path in stale_manifest_paths:
        if stale_path.exists():
            stale_path.unlink()
            removed_paths.append(str(stale_path.relative_to(repo_root)))
    for rel_path, payload in expected_root_artifacts(manifest):
        write_json(repo_root / rel_path, payload)
        written_paths.append(rel_path)
    after = _snapshot(repo_root, [plugin_root, *root_artifact_paths, *stale_manifest_paths])

    # The generated `.json` install-surface artifacts are written by `write_json`
    # above and keep their storage format; only this run receipt is YAML.
    emit_yaml(
        {
            "package_id": args.package_id,
            "written_paths": written_paths,
            "removed_paths": removed_paths,
            "change_summary": _change_summary(before, after),
        }
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PackagingError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
