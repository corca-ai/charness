#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import date as date_cls
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
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a new achieve goal artifact, or update only the status of an existing one."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--slug", required=True, help="Short kebab-case goal slug (e.g. ceal-184-push-confidence)")
    parser.add_argument("--title", required=True, help="Human-readable goal title shown in the artifact heading")
    parser.add_argument("--date", default=date_cls.today().isoformat(), help="Goal date prefix YYYY-MM-DD (default: today)")
    parser.add_argument(
        "--status",
        default="draft",
        choices=goal_lib.VALID_STATUSES,
        help="Lifecycle status; new artifacts default to draft and only activate when the user runs /goal @file",
    )
    parser.add_argument("--goal-body", default="", help="Optional initial goal statement inserted under the Goal section on creation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = goal_lib.upsert_goal(
        args.repo_root.expanduser().resolve(),
        date=args.date,
        slug=args.slug,
        title=args.title,
        status=args.status,
        goal_body=args.goal_body,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
