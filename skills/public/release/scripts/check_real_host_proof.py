#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)






_RELEASE_SCRIPT_DIR = REPO_ROOT / "skills" / "public" / "release" / "scripts"

_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

_scripts_surfaces_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.surfaces_lib")
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces
resolve_trigger_surfaces = _scripts_surfaces_lib_module.resolve_trigger_surfaces
SurfaceError = _scripts_surfaces_lib_module.SurfaceError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root used to resolve the release adapter")
    parser.add_argument("--paths", nargs="*", help="Changed paths to evaluate; defaults to git-derived changed paths")
    return parser.parse_args()


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def broken_trigger_config_payload(
    unresolved: list[str], manifest_path: str
) -> dict[str, object]:
    return {
        "required": False,
        "configuration_status": "broken",
        "unresolved_trigger_surfaces": unresolved,
        "surfaces_manifest_path": manifest_path,
        "checklist": [],
        "reason": (
            "real_host_required_surfaces references surface ids that are not declared in the surfaces manifest."
        ),
        "remediation": (
            "Fix the typo in real_host_required_surfaces, declare the missing surface id in .agents/surfaces.json, "
            "or remove the unresolved entry. Unresolved trigger ids must not silently fall through to a normal non-match."
        ),
    }


def surface_error_payload(error: str) -> dict[str, object]:
    return {
        "required": False,
        "error": error,
        "checklist": [],
        "reason": "Release real-host proof configuration is present, but the surfaces manifest could not be loaded.",
        "remediation": (
            "Create a valid repo-local .agents/surfaces.json, or remove real_host_required_surfaces "
            "and real_host_required_path_globs from the release adapter when this repo does not gate on host proof."
        ),
    }


def build_payload(repo_root: Path, changed_paths: list[str]) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    trigger_surfaces = adapter["data"].get("real_host_required_surfaces", [])
    trigger_globs = adapter["data"].get("real_host_required_path_globs", [])
    checklist = adapter["data"].get("real_host_checklist", [])

    surface_hits: list[str] = []
    if trigger_surfaces:
        surfaces_manifest = load_surfaces(repo_root)
        assert surfaces_manifest is not None
        resolved_trigger_surfaces = resolve_trigger_surfaces(surfaces_manifest, trigger_surfaces)
        if resolved_trigger_surfaces["unresolved"]:
            return broken_trigger_config_payload(
                resolved_trigger_surfaces["unresolved"], surfaces_manifest["path"]
            )
        declared_trigger_surfaces = set(resolved_trigger_surfaces["declared"])
        matched = match_surfaces(surfaces_manifest, changed_paths)
        surface_hits = [
            surface["surface_id"]
            for surface in matched["matched_surfaces"]
            if surface["surface_id"] in declared_trigger_surfaces
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
    changed_paths = args.paths if args.paths is not None else collect_changed_paths(repo_root)
    payload = build_payload(repo_root, changed_paths)
    if payload.get("configuration_status") == "broken":
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(json.dumps(surface_error_payload(str(exc)), ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
