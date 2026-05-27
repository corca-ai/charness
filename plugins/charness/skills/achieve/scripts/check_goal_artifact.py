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


def _resolve_goal_path(args) -> Path:
    repo_root = args.repo_root.expanduser().resolve()
    if args.goal_path is not None:
        return args.goal_path.expanduser().resolve()
    if not (args.slug and args.date):
        raise SystemExit("provide --goal-path, or both --slug and --date")
    try:
        return goal_lib.goal_path(repo_root, args.date, args.slug)
    except ValueError as exc:
        raise SystemExit(str(exc))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check that a goal artifact keeps the required sections, status, and activation line.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--goal-path", type=Path, help="Explicit path to the goal artifact (overrides --slug/--date)")
    parser.add_argument("--slug", help="Goal slug, used with --date to locate the artifact")
    parser.add_argument("--date", default=date_cls.today().isoformat(), help="Goal date prefix YYYY-MM-DD used with --slug")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = _resolve_goal_path(args)
    if not path.exists():
        print(json.dumps({"ok": False, "issues": [f"goal artifact not found: {path}"]}, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    result = goal_lib.check_goal(path.read_text(encoding="utf-8"))
    result["path"] = str(path)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
