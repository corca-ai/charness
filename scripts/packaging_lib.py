#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
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


class PackagingError(Exception):
    pass


def load_manifest(repo_root: Path, package_id: str) -> dict:
    manifest_path = repo_root / "packaging" / f"{package_id}.json"
    if not manifest_path.exists():
        raise PackagingError(f"missing packaging manifest `{manifest_path}`")
    try:
        VALIDATE_PACKAGING.validate_packaging_manifest(
            manifest_path,
            repo_root,
            validate_root_artifacts=False,
        )
    except Exception as exc:
        raise PackagingError(str(exc)) from exc
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_codex_marketplace(manifest: dict, *, source_path: str) -> dict:
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
                    "path": source_path,
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": repo_marketplace["category"],
            }
        ],
    }


def expected_root_artifacts(manifest: dict) -> list[tuple[str, dict]]:
    marketplace = manifest["codex"]["repo_marketplace"]
    return [
        (manifest["codex"]["manifest_path"], manifest["codex"]["manifest"]),
        (manifest["claude"]["manifest_path"], manifest["claude"]["manifest"]),
        (
            marketplace["path"],
            build_codex_marketplace(manifest, source_path=marketplace["repo_root_source_path"]),
        ),
    ]
