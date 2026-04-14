#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


REPO_ROOT = _runtime_root()
_RELEASE_SCRIPT_DIR = REPO_ROOT / "skills" / "public" / "release" / "scripts"
sys.path[:0] = [str(REPO_ROOT), str(_RELEASE_SCRIPT_DIR)]

from resolve_adapter import load_adapter

from scripts.surfaces_lib import collect_changed_paths, load_surfaces, match_surfaces


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--paths", nargs="*")
    return parser.parse_args()


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def build_payload(repo_root: Path, changed_paths: list[str]) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    surfaces_manifest = load_surfaces(repo_root)
    assert surfaces_manifest is not None
    matched = match_surfaces(surfaces_manifest, changed_paths)

    trigger_surfaces = adapter["data"].get("real_host_required_surfaces", [])
    trigger_globs = adapter["data"].get("real_host_required_path_globs", [])
    checklist = adapter["data"].get("real_host_checklist", [])
    surface_hits = [
        surface["surface_id"]
        for surface in matched["matched_surfaces"]
        if surface["surface_id"] in trigger_surfaces
    ]
    path_hits = [path for path in changed_paths if matches_any(path, trigger_globs)]
    required = bool(surface_hits or path_hits)
    return {
        "required": required,
        "changed_paths": changed_paths,
        "surface_hits": surface_hits,
        "path_hits": path_hits,
        "checklist": checklist if required else [],
        "reason": (
            "Changed surfaces hit configured release-time real-host proof seams."
            if required
            else "No configured release-time real-host proof trigger matched the current slice."
        ),
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    changed_paths = args.paths if args.paths else collect_changed_paths(repo_root)
    print(json.dumps(build_payload(repo_root, changed_paths), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
