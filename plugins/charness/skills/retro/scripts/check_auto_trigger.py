#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)






_RETRO_SCRIPT_DIR = REPO_ROOT / "skills" / "public" / "retro" / "scripts"

_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

_scripts_surfaces_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.surfaces_lib")
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--paths", nargs="*")
    return parser.parse_args()


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    changed_paths = args.paths if args.paths else collect_changed_paths(repo_root)
    surfaces_manifest = load_surfaces(repo_root)
    assert surfaces_manifest is not None
    matched = match_surfaces(surfaces_manifest, changed_paths)

    trigger_surfaces = adapter["data"].get("auto_session_trigger_surfaces", [])
    trigger_globs = adapter["data"].get("auto_session_trigger_path_globs", [])
    surface_hits = [
        surface["surface_id"]
        for surface in matched["matched_surfaces"]
        if surface["surface_id"] in trigger_surfaces
    ]
    path_hits = [path for path in changed_paths if matches_any(path, trigger_globs)]
    triggered = bool(surface_hits or path_hits)
    payload = {
        "triggered": triggered,
        "changed_paths": changed_paths,
        "surface_hits": surface_hits,
        "path_hits": path_hits,
        "suggested_mode": "session" if triggered else None,
        "reason": (
            "Changed surfaces hit configured install/update/support/export/discovery retro triggers."
            if triggered
            else "No configured auto-retro trigger matched the current slice."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
