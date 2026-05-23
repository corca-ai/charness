#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
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
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_scripts_tool_recommendation_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.tool_recommendation_lib")
recommendations_for_role = _scripts_tool_recommendation_lib_module.recommendations_for_role
_scripts_control_plane_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.control_plane_lib")
load_manifests = _scripts_control_plane_lib_module.load_manifests_for_discovery


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose integration manifests should be inspected for tool recommendations")
    parser.add_argument("--recommendation-role", default="validation", help="Recommendation role to surface (e.g. validation, security)")
    parser.add_argument("--next-skill-id", default="quality", help="Skill ID about to run, used to scope manifest recommendations")
    parser.add_argument("--include-ready", action="store_true", help="Include already-satisfied tool recommendations in the output")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    payload = {
        "recommendation_role": args.recommendation_role,
        "next_skill_id": args.next_skill_id,
        "tool_recommendations": recommendations_for_role(
            repo_root,
            load_manifests(repo_root),
            recommendation_role=args.recommendation_role,
            next_skill_id=args.next_skill_id,
            only_blocking=not args.include_ready,
        ),
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
