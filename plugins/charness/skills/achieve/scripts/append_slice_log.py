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

_FIELD_FLAGS = (
    ("objective", "Objective"),
    ("why", "Why this approach"),
    ("commits", "Commits"),
    ("changed", "What changed"),
    ("alternatives", "Alternatives rejected"),
    ("verification", "Targeted verification"),
    ("test-pressure", "Test duplication pressure"),
    ("critique", "Critique"),
    ("off-goal", "Off-goal findings"),
    ("lessons", "Lessons carried forward"),
    ("metrics", "Metrics"),
)


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
    parser = argparse.ArgumentParser(description="Append one slice report to a goal artifact's Slice Log.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--goal-path", type=Path, help="Explicit path to the goal artifact (overrides --slug/--date)")
    parser.add_argument("--slug", help="Goal slug, used with --date to locate the artifact")
    parser.add_argument("--date", default=date_cls.today().isoformat(), help="Goal date prefix YYYY-MM-DD used with --slug")
    parser.add_argument("--name", required=True, help="Short slice name for the slice heading")
    for flag, label in _FIELD_FLAGS:
        parser.add_argument(f"--{flag}", default="", help=f"Slice report value for '{label}'")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = _resolve_goal_path(args)
    if not path.exists():
        raise SystemExit(f"goal artifact not found: {path}")
    text = path.read_text(encoding="utf-8")
    number = goal_lib.next_slice_number(text)
    fields = {label: getattr(args, flag.replace("-", "_")) for flag, label in _FIELD_FLAGS}
    block = goal_lib.render_slice_block(number, args.name, fields)
    updated = goal_lib.append_slice(text, block)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
    print(json.dumps({"action": "appended", "slice": number, "path": str(path)}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
