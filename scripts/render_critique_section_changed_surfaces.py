#!/usr/bin/env python3
"""Default `changed-files-and-owning-surfaces` producer for prepare packets.

Stdout body lists each path in the current working set and the surfaces
(from `.agents/surfaces.json`) that own or derive from it. The output
shape is the *section body*; the runner wraps this into the packet
envelope. Exit 0 even when the working set is empty.

See `skills/public/critique/references/prepare-packet.md` and the retro
prepare-packet sibling.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_working_tree_snapshot = _scripts_surfaces_lib_module.collect_working_tree_snapshot
collect_changed_and_deleted_paths_for_ref = (
    _scripts_surfaces_lib_module.collect_changed_and_deleted_paths_for_ref
)
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
    deleted_paths = set(payload.get("deleted_paths") or ())
    if changed_paths:
        for path in changed_paths:
            # A removal rendered exactly like an edit is what let a release
            # review report "no deletion entry or absence marker for any removed
            # component" while the range removed six files. The reviewer cannot
            # ask what a deletion cost if the listing never says one happened.
            suffix = "  (DELETED — judge what depended on it)" if path in deleted_paths else ""
            lines.append(f"- {path}{suffix}")
        if deleted_paths:
            substrate = f"ref `{changed_ref}`" if changed_ref else "working tree"
            lines.append("")
            lines.append(
                f"{len(deleted_paths)} of {len(changed_paths)} changed path(s) were DELETED in the "
                f"{substrate}. Their pre-image bytes are bound in the reviewed-input identity, so "
                "what was removed is recoverable."
            )
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
                lines.append(f"  source matches: {', '.join(surface['matched_source_paths'])}")
            if surface["matched_derived_paths"]:
                lines.append(f"  derived matches: {', '.join(surface['matched_derived_paths'])}")
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
        default=os.environ.get("CHARNESS_CRITIQUE_CHANGED_REF")
        or os.environ.get("CHARNESS_RETRO_CHANGED_REF"),
        help="Git commit or range to render instead of the current working tree.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        surfaces = load_surfaces(repo_root)
        if args.changed_ref:
            changed_paths, deleted_paths = collect_changed_and_deleted_paths_for_ref(
                repo_root, args.changed_ref
            )
        else:
            snapshot = collect_working_tree_snapshot(repo_root)
            changed_paths = list(snapshot.changed_paths)
            deleted_paths = set(snapshot.deleted_paths)
        match = match_surfaces(surfaces, changed_paths)
    except SurfaceError as exc:
        print(f"surfaces lookup failed: {exc}")
        return 1
    payload = {
        "changed_ref": args.changed_ref,
        "changed_paths": match["changed_paths"],
        "deleted_paths": sorted(deleted_paths),
        "matched_surfaces": match["matched_surfaces"],
        "sync_commands": match["sync_commands"],
    }
    print(_render(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
