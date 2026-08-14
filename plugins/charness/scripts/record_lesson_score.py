#!/usr/bin/env python3
"""Append one cited lesson score without bypassing the ledger validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
lesson_ledger_path = _ledger.lesson_ledger_path
replay_validated_ledger_payload = _ledger.replay_validated_ledger_payload
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")
ledger_lock = _writer.ledger_lock
replace_payload = _writer.replace_payload


def _fail(message: str) -> None:
    raise ValueError(f"record lesson score: {message}")


def _nonblank(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        _fail(f"{name} must be a non-empty non-whitespace string")
    return stripped


def append_score(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
    event_id: str,
    session_id: str,
    lesson_id: str,
    source_retro: str,
    score: int,
    anchor: str | None,
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    event_id = _nonblank(event_id, "event_id")
    lesson_id = _nonblank(lesson_id, "lesson_id")
    session_id = _nonblank(session_id, "session_id")
    source_retro = _nonblank(source_retro, "source_retro")
    if anchor is not None:
        anchor = _nonblank(anchor, "anchor")
    if type(score) is not int:
        _fail("score must be an integer")
    path = lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    with ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        replayed = replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=payload,
        )
        if lesson_id not in replayed:
            _fail(f"lesson_id `{lesson_id}` is unseeded")
        candidate = copy.deepcopy(payload)
        event: dict[str, Any] = {
            "event_id": event_id,
            "session_id": session_id,
            "source_retro": source_retro,
            "lesson_id": lesson_id,
            "score": score,
        }
        if anchor is not None:
            event["anchor"] = anchor
        candidate["score_events"].append(event)
        candidate["lessons"] = replayed
        candidate["lessons"][lesson_id]["score_total"] += score
        candidate["lessons"][lesson_id]["score_count"] += 1
        replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=candidate,
        )
        replace_payload(path, candidate)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--lesson-id", required=True)
    parser.add_argument("--source-retro", required=True)
    parser.add_argument("--score", type=int, required=True)
    parser.add_argument("--anchor")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    event = append_score(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
        event_id=args.event_id,
        session_id=args.session_id,
        lesson_id=args.lesson_id,
        source_retro=args.source_retro,
        score=args.score,
        anchor=args.anchor,
    )
    # Receipt only; `append_score` already persisted the event in the JSON ledger.
    emit_yaml(event)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
