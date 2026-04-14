#!/usr/bin/env python3
# ruff: noqa: E402
"""Exec every .py in the checked-in plugin tree to catch broken imports.

Companion gate to `check-export-safe-imports.py`. That lint rejects a known
family of dev-tree-only imports statically. This gate executes every module
in the exported plugin tree end-to-end so that any other import-time failure
the static lint cannot see still surfaces before push.

Runs as one subprocess that exec()s each module via
`importlib.util.spec_from_file_location`, skipping `if __name__ == '__main__':`
blocks. Typical cost: ~0.5s for the full charness plugin tree.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_packaging_install_surface import smoke_exported_plugin_imports

PACKAGING_MANIFEST = REPO_ROOT / "packaging" / "charness.json"


class ValidationError(Exception):
    pass


def resolve_plugin_root(repo_root: Path) -> Path:
    manifest_path = repo_root / "packaging" / "charness.json"
    if not manifest_path.is_file():
        raise ValidationError(f"missing packaging manifest: {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    package_id = data.get("package_id")
    if not package_id:
        raise ValidationError(f"{manifest_path}: missing package_id")
    plugin_root = repo_root / "plugins" / package_id
    if not plugin_root.is_dir():
        raise ValidationError(f"missing plugin tree: {plugin_root}")
    return plugin_root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    plugin_root = resolve_plugin_root(root)
    try:
        smoke_exported_plugin_imports(plugin_root)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        raise ValidationError(str(exc)) from exc

    print(f"Imported every .py under {plugin_root.relative_to(root)} successfully.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
