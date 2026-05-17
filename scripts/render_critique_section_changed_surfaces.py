#!/usr/bin/env python3
"""Default `changed-files-and-owning-surfaces` producer for the
critique prepare-packet contract.

Stdout body lists each path in the current working set and the surfaces
(from `.agents/surfaces.json`) that own or derive from it. The output
shape is the *section body*; the runner wraps this into the packet
envelope. Exit 0 even when the working set is empty.

See `skills/public/critique/references/prepare-packet.md`.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
collect_changed_paths_for_ref = _scripts_surfaces_lib_module.collect_changed_paths_for_ref
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces


def _render(payload: dict[str, object]) -> str:
    lines: list[str] = []
    changed_paths = payload["changed_paths"]
    changed_ref = payload.get("changed_ref")
    if changed_ref:
        lines.append(f"Changed paths for ref `{changed_ref}`:")
    else:
        lines.append("Changed paths for working tree:")
    if changed_paths:
        for path in changed_paths:
            lines.append(f"- {path}")
    elif changed_ref:
        lines.append("- (none — changed ref produced no changed paths)")
    else:
        lines.append("- (none — clean working tree)")
    lines.append("")

    matched = payload["matched_surfaces"]
    lines.append("Owning surfaces:")
    if matched:
        for surface in matched:
            lines.append(f"- {surface['surface_id']}: {surface['description']}")
            if surface["matched_source_paths"]:
                lines.append(
                    f"  source matches: {', '.join(surface['matched_source_paths'])}"
                )
            if surface["matched_derived_paths"]:
                lines.append(
                    f"  derived matches: {', '.join(surface['matched_derived_paths'])}"
                )
            if surface["sync_commands"]:
                lines.append(f"  sync: {', '.join(surface['sync_commands'])}")
            if surface["verify_commands"]:
                lines.append(f"  verify: {', '.join(surface['verify_commands'])}")
    else:
        lines.append("- (no surfaces matched the changed paths)")
    lines.append("")

    sync_commands = payload["sync_commands"]
    if sync_commands:
        lines.append("Planned sync commands before validators:")
        for command in sync_commands:
            lines.append(f"- {command}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--changed-ref",
        default=os.environ.get("CHARNESS_CRITIQUE_CHANGED_REF"),
        help="Git commit or range to render instead of the current working tree.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        surfaces = load_surfaces(repo_root)
        changed_paths = (
            collect_changed_paths_for_ref(repo_root, args.changed_ref)
            if args.changed_ref
            else collect_changed_paths(repo_root)
        )
        match = match_surfaces(surfaces, changed_paths)
    except SurfaceError as exc:
        print(f"surfaces lookup failed: {exc}")
        return 1
    payload = {
        "changed_ref": args.changed_ref,
        "changed_paths": match["changed_paths"],
        "matched_surfaces": match["matched_surfaces"],
        "sync_commands": match["sync_commands"],
    }
    print(_render(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
