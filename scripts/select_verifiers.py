#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
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
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
dedupe_preserve_order = _scripts_surfaces_lib_module.dedupe_preserve_order
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces


def command_reasons(payload: dict[str, object], phase: str) -> list[dict[str, object]]:
    key = f"{phase}_commands"
    commands = payload.get(key, [])
    matched_surfaces = payload.get("matched_surfaces", [])
    if not isinstance(commands, list) or not isinstance(matched_surfaces, list):
        return []
    reasons: list[dict[str, object]] = []
    for command in commands:
        if not isinstance(command, str):
            continue
        surface_ids = dedupe_preserve_order(
            [
                surface["surface_id"]
                for surface in matched_surfaces
                if isinstance(surface, dict)
                and isinstance(surface.get(key), list)
                and command in surface[key]
                and isinstance(surface.get("surface_id"), str)
            ]
        )
        reasons.append(
            {
                "phase": phase,
                "command": command,
                "reason_surface_ids": surface_ids,
            }
        )
    return reasons


def bundle_status(payload: dict[str, object]) -> tuple[str, list[str]]:
    unmatched_paths = payload.get("unmatched_paths", [])
    verify_commands = payload.get("verify_commands", [])
    notes: list[str] = []
    if isinstance(unmatched_paths, list) and unmatched_paths:
        notes.append(
            "Some changed paths are not covered by `.agents/surfaces.json`; add coverage or keep the closeout unmatched explicitly."
        )
    if isinstance(verify_commands, list) and verify_commands:
        return "repo-owned-bundle", notes
    notes.append(
        "No repo-owned verifier bundle matched these changes; this is a real quality gap if the surface is expected to have standing verification."
    )
    return "missing-bundle", notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--surfaces-path", type=Path, default=SURFACES_PATH)
    parser.add_argument(
        "--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff."
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest = load_surfaces(repo_root, surfaces_path=args.surfaces_path)
    assert manifest is not None
    changed_paths = args.paths if args.paths else collect_changed_paths(repo_root)
    payload = match_surfaces(manifest, changed_paths)
    payload["surfaces_manifest_path"] = manifest["path"]
    payload["selection_mode"] = "surface-manifest"
    payload["recommended_commands"] = command_reasons(payload, "sync") + command_reasons(
        payload, "verify"
    )
    payload["bundle_status"], payload["notes"] = bundle_status(payload)

    emit_yaml(payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
