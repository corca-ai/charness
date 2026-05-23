#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
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
_control_plane_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.control_plane_lib")
load_manifests_for_discovery = _control_plane_lib.load_manifests_for_discovery
dependencies_path = _control_plane_lib.dependencies_path
dependencies_schema_path = _control_plane_lib.dependencies_schema_path


def _plugin_schema_source() -> Path:
    return Path(_control_plane_lib.__file__).resolve().parent.parent / "integrations" / "tools" / "dependencies.schema.json"


def _resolve_tool_ids(repo_root: Path, *, explicit: list[str], from_recommendations: bool) -> list[str]:
    if explicit and from_recommendations:
        raise SystemExit("error: pass --tool-id or --from-recommendations, not both")
    if explicit:
        return sorted(set(explicit))
    if not from_recommendations:
        return []
    manifests = load_manifests_for_discovery(repo_root)
    return sorted({m["tool_id"] for m in manifests if m.get("recommendation_role")})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root path")
    parser.add_argument("--tool-id", action="append", default=[], help="Tool id to seed (repeatable)")
    parser.add_argument(
        "--from-recommendations",
        action="store_true",
        help="Seed every plugin-fallback tool with a recommendation_role.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing integrations/tools/dependencies.json.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    deps_path = dependencies_path(repo_root)
    schema_path = dependencies_schema_path(repo_root)

    tool_ids = _resolve_tool_ids(
        repo_root, explicit=list(args.tool_id), from_recommendations=args.from_recommendations
    )
    payload = {"schema_version": 1, "tool_dependencies": tool_ids}

    actions: list[str] = []
    if deps_path.exists() and not args.force:
        result = {
            "status": "skipped",
            "reason": "dependencies.json already exists; pass --force to overwrite",
            "dependencies_path": str(deps_path),
            "tool_dependencies": tool_ids,
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(result["reason"])
        return 1

    deps_path.parent.mkdir(parents=True, exist_ok=True)
    deps_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    actions.append(f"wrote {deps_path.relative_to(repo_root)}")

    if not schema_path.exists():
        source = _plugin_schema_source()
        if source.is_file():
            schema_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, schema_path)
            actions.append(f"copied schema to {schema_path.relative_to(repo_root)}")

    result = {
        "status": "seeded",
        "dependencies_path": str(deps_path.relative_to(repo_root)),
        "schema_path": str(schema_path.relative_to(repo_root)) if schema_path.exists() else None,
        "tool_dependencies": tool_ids,
        "actions": actions,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for action in actions:
            print(action)
        if tool_ids:
            print(f"staged tool_dependencies: {', '.join(tool_ids)}")
        else:
            print("staged tool_dependencies: (empty)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
