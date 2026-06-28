#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from datetime import date as date_cls
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a new achieve goal artifact, or update only the status of an existing one."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--slug", required=True, help="Short kebab-case goal slug (e.g. acme-184-push-confidence)")
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
    try:
        result = goal_lib.upsert_goal(
            args.repo_root.expanduser().resolve(),
            date=args.date,
            slug=args.slug,
            title=args.title,
            status=args.status,
            goal_body=args.goal_body,
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if result.get("action") == "refused" else 0


if __name__ == "__main__":
    raise SystemExit(main())
