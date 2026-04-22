#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces


def print_text(payload: dict[str, object]) -> None:
    changed_paths = payload["changed_paths"]
    print("Changed paths:")
    if changed_paths:
        for path in changed_paths:
            print(f"- {path}")
    else:
        print("- (none)")

    print("Matched surfaces:")
    matched_surfaces = payload["matched_surfaces"]
    if matched_surfaces:
        for surface in matched_surfaces:
            print(f"- {surface['surface_id']}: {surface['description']}")
            if surface["matched_source_paths"]:
                print(f"  source matches: {', '.join(surface['matched_source_paths'])}")
            if surface["matched_derived_paths"]:
                print(f"  derived matches: {', '.join(surface['matched_derived_paths'])}")
            if surface["sync_commands"]:
                print(f"  sync: {', '.join(surface['sync_commands'])}")
            if surface["verify_commands"]:
                print(f"  verify: {', '.join(surface['verify_commands'])}")
    else:
        print("- (none)")

    print("Planned sync commands:")
    if payload["sync_commands"]:
        for command in payload["sync_commands"]:
            print(f"- {command}")
    else:
        print("- (none)")

    print("Planned verify commands:")
    if payload["verify_commands"]:
        for command in payload["verify_commands"]:
            print(f"- {command}")
    else:
        print("- (none)")

    if payload["unmatched_paths"]:
        print("Unmatched paths:")
        for path in payload["unmatched_paths"]:
            print(f"- {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--surfaces-path", type=Path, default=SURFACES_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest = load_surfaces(repo_root, surfaces_path=args.surfaces_path)
    assert manifest is not None
    changed_paths = args.paths if args.paths else collect_changed_paths(repo_root)
    payload = match_surfaces(manifest, changed_paths)
    payload["surfaces_manifest_path"] = manifest["path"]

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
