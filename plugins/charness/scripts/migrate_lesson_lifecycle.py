#!/usr/bin/env python3
"""Preview or apply the deterministic lesson-ledger v3 to v4 migration."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")


def migration_candidate(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("kind") != _ledger.KIND:
        raise ValueError("lesson lifecycle migration: expected a lesson ledger object")
    if payload.get("schema_version") == _ledger.SCHEMA_VERSION:
        return copy.deepcopy(payload)
    if payload.get("schema_version") != 3:
        raise ValueError("lesson lifecycle migration: only schema version 3 can migrate")
    candidate = copy.deepcopy(payload)
    candidate["schema_version"] = _ledger.SCHEMA_VERSION
    candidate["active_lesson_budget"] = _ledger.ACTIVE_LESSON_BUDGET
    candidate["lifecycle_events"] = []
    for lesson in candidate.get("lessons", {}).values():
        if not isinstance(lesson, dict):
            raise ValueError("lesson lifecycle migration: invalid materialized lesson")
        lesson["state"] = "active"
        lesson["last_lifecycle_event_id"] = None
    return candidate


def migrate(*, repo_root: Path, execute: bool) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    output_dir = repo_root / "charness-artifacts/retro"
    path = _ledger.lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    with _writer.ledger_lock(path):
        before = path.read_bytes()
        payload = json.loads(before)
        candidate = migration_candidate(payload)
        _ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=candidate,
        )
        changed = candidate != payload
        if execute and changed:
            _writer.replace_payload(path, candidate)
    return {
        "kind": "charness.lesson-lifecycle-migration",
        "from_schema_version": payload.get("schema_version"),
        "to_schema_version": candidate["schema_version"],
        "changed": changed,
        "executed": execute,
        "lesson_count": len(candidate["lessons"]),
        "active_lesson_budget": candidate["active_lesson_budget"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(migrate(repo_root=args.repo_root.resolve(), execute=args.execute), indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
