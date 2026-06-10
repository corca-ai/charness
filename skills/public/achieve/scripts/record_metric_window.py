#!/usr/bin/env python3
"""Record a goal-scoped `Host metric window:` evidence line in a goal artifact.

The achieve After-phase runs this so `probe_host_logs.py --goal-path <artifact>`
reports an applied (``parsed``) goal window instead of ``absent``. The
host adapter supplies the timestamps and rollout-file path it can prove; this
helper only writes them into the artifact idempotently.
"""
from __future__ import annotations

import argparse
import json
import runpy
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
        description="Record or update the `Host metric window:` evidence line in a goal artifact."
    )
    parser.add_argument("--goal-path", type=Path, required=True, help="Path to the goal artifact to update")
    parser.add_argument("--started-at", required=True, help="Goal window start as an ISO-8601 timestamp")
    parser.add_argument("--completed-at", required=True, help="Goal window end as an ISO-8601 timestamp")
    session_source = parser.add_mutually_exclusive_group(required=True)
    session_source.add_argument(
        "--codex-session-file",
        help="Path to the Codex rollout JSONL scoped by the window",
    )
    session_source.add_argument(
        "--claude-session-file",
        help="Path to the Claude project session JSONL scoped by the window",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.goal_path.expanduser()
    if not path.is_file():
        print(json.dumps({"action": "refused", "note": f"goal artifact not found: {path}"}, ensure_ascii=False))
        return 2
    original = path.read_text(encoding="utf-8")
    try:
        updated = goal_lib.record_metric_window(
            original,
            started_at=args.started_at,
            completed_at=args.completed_at,
            codex_session_file=args.codex_session_file,
            claude_session_file=args.claude_session_file,
        )
    except ValueError as exc:
        print(json.dumps({"action": "refused", "note": str(exc)}, ensure_ascii=False))
        return 2
    changed = updated != original
    if changed:
        path.write_text(updated, encoding="utf-8")
    print(
        json.dumps(
            {"action": "updated" if changed else "unchanged", "path": str(path)},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
