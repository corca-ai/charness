#!/usr/bin/env python3
"""Append one explicit archive or resurrection event to the lesson ledger."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    repo_root_from_script,
    require_repo_local_helper,
)
from scripts.yaml_output import emit_yaml  # noqa: E402

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lessons.lesson_ledger_lib")
_writer = import_repo_module(__file__, "scripts.lessons.lesson_ledger_writer_lib")


def _nonblank(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"record lesson lifecycle: {name} must be non-empty")
    return stripped


def append_lifecycle_event(
    *,
    repo_root: Path,
    event_id: str,
    lesson_id: str,
    action: str,
    decision_ref: str,
    rationale: str,
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    output_dir = repo_root / "charness-artifacts/retro"
    path = _ledger.lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    event_id = _nonblank(event_id, "event_id")
    lesson_id = _nonblank(lesson_id, "lesson_id")
    decision_ref = _nonblank(decision_ref, "decision_ref")
    rationale = _nonblank(rationale, "rationale")
    if action not in {"archive", "resurrect"}:
        raise ValueError("record lesson lifecycle: action must be archive or resurrect")
    with _writer.ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload, _migrated = _ledger.migrate_ledger_payload(payload)
        if _migrated:
            # One-way upgrade: keep the pre-upgrade bytes so the documented
            # rollback to the previous release stays true.
            _writer.preserve_pre_migration_copy(path)
        _ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=payload,
        )
        if lesson_id not in payload["lessons"]:
            raise ValueError(
                f"record lesson lifecycle: lesson_id `{lesson_id}` is not seeded"
            )
        candidate = copy.deepcopy(payload)
        event = {
            "sequence": len(candidate["lifecycle_events"]) + 1,
            "event_id": event_id,
            "lesson_id": lesson_id,
            "action": action,
            "decision_ref": decision_ref,
            "rationale": rationale,
        }
        candidate["lifecycle_events"].append(event)
        replayed = _ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload={**candidate, "lessons": _materialize(candidate)},
        )
        candidate["lessons"] = replayed
        _writer.replace_payload(path, candidate)
    return event


def _materialize(candidate: dict[str, Any]) -> dict[str, Any]:
    lessons = copy.deepcopy(candidate["lessons"])
    event = candidate["lifecycle_events"][-1]
    lesson = lessons[event["lesson_id"]]
    lesson["state"] = "archived" if event["action"] == "archive" else "active"
    lesson["last_lifecycle_event_id"] = event["event_id"]
    return lessons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--lesson-id", required=True)
    parser.add_argument("--action", choices=("archive", "resurrect"), required=True)
    parser.add_argument("--decision-ref", required=True)
    parser.add_argument("--rationale", required=True)
    args = parser.parse_args(argv)
    event = append_lifecycle_event(
        repo_root=args.repo_root.resolve(),
        event_id=args.event_id,
        lesson_id=args.lesson_id,
        action=args.action,
        decision_ref=args.decision_ref,
        rationale=args.rationale,
    )
    # Receipt only; the event itself is already persisted in the JSON ledger.
    emit_yaml(event)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
