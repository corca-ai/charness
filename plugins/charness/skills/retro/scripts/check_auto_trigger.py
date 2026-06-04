#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import runpy
import subprocess
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






_RETRO_SCRIPT_DIR = REPO_ROOT / "skills" / "public" / "retro" / "scripts"

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
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to scan for auto-retro trigger surfaces and path globs")
    parser.add_argument("--paths", nargs="*", help="Changed paths to evaluate against trigger surfaces (defaults to git diff)")
    parser.add_argument("--base-ref", help="Base git ref for explicit commit-range path discovery")
    parser.add_argument("--head-ref", default="HEAD", help="Head git ref for --base-ref path discovery (default: HEAD)")
    return parser.parse_args()


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def no_config_payload(paths: list[str], field_state: dict[str, object]) -> dict[str, object]:
    surface_state = field_state.get("auto_session_trigger_surfaces")
    glob_state = field_state.get("auto_session_trigger_path_globs")
    intentional_empty = surface_state == "explicit-empty" and glob_state == "explicit-empty"
    payload = {
        "triggered": False,
        "changed_paths": paths,
        "surface_hits": [],
        "path_hits": [],
        "suggested_mode": None,
        "configuration_status": "intentional-empty" if intentional_empty else "missing",
        "field_state": {
            "auto_session_trigger_surfaces": surface_state,
            "auto_session_trigger_path_globs": glob_state,
        },
    }
    if intentional_empty:
        payload["reason"] = "Auto-retro trigger surfaces and path globs are explicitly empty."
    else:
        payload["reason"] = "No auto-retro trigger surfaces or path globs are configured."
        payload["remediation"] = (
            "Add auto_session_trigger_surfaces or auto_session_trigger_path_globs, "
            "or set both fields to [] to record an intentional opt-out."
        )
    return payload


def surface_error_payload(error: str) -> dict[str, object]:
    return {
        "triggered": False,
        "error": error,
        "reason": "Auto-retro trigger configuration is present, but the surfaces manifest could not be loaded.",
        "remediation": (
            "Create a valid repo-local .agents/surfaces.json, or remove "
            "auto_session_trigger_surfaces and auto_session_trigger_path_globs "
            "from the retro adapter when this repo does not use auto-retro triggers."
        ),
    }


def collect_range_paths(repo_root: Path, *, base_ref: str, head_ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}..{head_ref}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SurfaceError(
            "git diff failed while collecting auto-retro trigger paths\n"
            f"base_ref: {base_ref}\n"
            f"head_ref: {head_ref}\n"
            f"exit_code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    return [line for line in result.stdout.splitlines() if line.strip()]


def broken_trigger_config_payload(
    unresolved: list[str], manifest_path: str
) -> dict[str, object]:
    return {
        "triggered": False,
        "configuration_status": "broken",
        "unresolved_trigger_surfaces": unresolved,
        "surfaces_manifest_path": manifest_path,
        "reason": (
            "auto_session_trigger_surfaces references surface ids that are not declared in the surfaces manifest."
        ),
        "remediation": (
            "Fix the typo in auto_session_trigger_surfaces, declare the missing surface id in .agents/surfaces.json, "
            "or remove the unresolved entry. Unresolved trigger ids must not silently fall through to a normal non-match."
        ),
    }


def _input_paths(
    repo_root: Path,
    *,
    paths: list[str] | None = None,
    base_ref: str | None = None,
    head_ref: str = "HEAD",
) -> tuple[list[str], dict[str, object]]:
    if paths is not None and base_ref:
        raise SurfaceError("--paths and --base-ref are mutually exclusive")
    if base_ref:
        return collect_range_paths(repo_root, base_ref=base_ref, head_ref=head_ref), {
            "mode": "commit_range",
            "base_ref": base_ref,
            "head_ref": head_ref,
        }
    if paths is not None:
        return paths, {"mode": "explicit_paths"}
    return collect_changed_paths(repo_root), {"mode": "working_tree_diff"}


def build_payload(
    repo_root: Path,
    *,
    paths: list[str] | None = None,
    base_ref: str | None = None,
    head_ref: str = "HEAD",
) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    trigger_surfaces = adapter["data"].get("auto_session_trigger_surfaces", [])
    trigger_globs = adapter["data"].get("auto_session_trigger_path_globs", [])
    if not trigger_surfaces and not trigger_globs and paths is None and not base_ref:
        payload = no_config_payload([], adapter.get("field_state", {}))
        payload["input"] = {"mode": "working_tree_diff"}
        return payload
    changed_paths, input_payload = _input_paths(
        repo_root, paths=paths, base_ref=base_ref, head_ref=head_ref
    )
    if not trigger_surfaces and not trigger_globs:
        payload = no_config_payload(changed_paths, adapter.get("field_state", {}))
        payload["input"] = input_payload
        return payload

    surfaces_manifest = load_surfaces(repo_root)
    assert surfaces_manifest is not None
    resolved_trigger_surfaces = resolve_trigger_surfaces(surfaces_manifest, trigger_surfaces)
    if resolved_trigger_surfaces["unresolved"]:
        payload = broken_trigger_config_payload(
            resolved_trigger_surfaces["unresolved"], surfaces_manifest["path"]
        )
        payload["input"] = input_payload
        payload["changed_paths"] = changed_paths
        return payload
    declared_trigger_surfaces = set(resolved_trigger_surfaces["declared"])

    matched = match_surfaces(surfaces_manifest, changed_paths)

    surface_hits = [
        surface["surface_id"]
        for surface in matched["matched_surfaces"]
        if surface["surface_id"] in declared_trigger_surfaces
    ]
    path_hits = [path for path in changed_paths if matches_any(path, trigger_globs)]
    triggered = bool(surface_hits or path_hits)
    payload = {
        "triggered": triggered,
        "changed_paths": changed_paths,
        "surface_hits": surface_hits,
        "path_hits": path_hits,
        "suggested_mode": "session" if triggered else None,
        "input": input_payload,
        "reason": (
            "Changed surfaces hit configured install/update/support/export/discovery retro triggers."
            if triggered
            else "No configured auto-retro trigger matched the current slice."
        ),
    }
    return payload


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    payload = build_payload(
        repo_root,
        paths=args.paths,
        base_ref=args.base_ref,
        head_ref=args.head_ref,
    )
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
