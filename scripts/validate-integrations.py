#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import (
    load_lock_schema,
    load_manifests,
    lock_paths,
    validate_lock_data,
)


class ValidationError(Exception):
    pass


ACCESS_MODE_ORDER = {
    "grant": 0,
    "binary": 1,
    "env": 2,
    "public": 3,
    "human-only": 4,
    "degraded": 5,
}


def validate_access_mode_order(manifest: dict[str, object], path: Path) -> None:
    access_modes = manifest.get("access_modes", [])
    if not isinstance(access_modes, list):
        return
    ranks = [ACCESS_MODE_ORDER[mode] for mode in access_modes]
    if ranks != sorted(ranks):
        raise ValidationError(
            f"{path}: access_modes must stay in preferred runtime order "
            "(grant, binary, env, public, human-only, degraded)"
        )


def validate_capability_requirements(manifest: dict[str, object], path: Path) -> None:
    access_modes = manifest.get("access_modes", [])
    if not isinstance(access_modes, list):
        return
    requirements = manifest.get("capability_requirements")
    if not isinstance(requirements, dict):
        requirements = {}
    if "grant" in access_modes and not requirements.get("grant_ids"):
        raise ValidationError(f"{path}: grant access requires capability_requirements.grant_ids")
    if "env" in access_modes and not requirements.get("env_vars"):
        raise ValidationError(f"{path}: env access requires capability_requirements.env_vars")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    try:
        repo_root = args.repo_root.resolve()
        manifests = load_manifests(repo_root)
        for manifest_path in sorted((repo_root / "integrations" / "tools").glob("*.json")):
            if manifest_path.name == "manifest.schema.json":
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            validate_access_mode_order(manifest, manifest_path)
            validate_capability_requirements(manifest, manifest_path)
        lock_schema = load_lock_schema()
        lock_files = lock_paths(repo_root)
        for path in lock_files:
            validate_lock_data(json.loads(path.read_text(encoding="utf-8")), lock_schema, path)
    except Exception as exc:  # pragma: no cover - surfaced via CLI tests
        raise ValidationError(str(exc)) from exc
    print(f"Validated {len(manifests)} integration manifests and {len(lock_files)} lock files.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
