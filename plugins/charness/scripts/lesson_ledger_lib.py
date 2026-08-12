"""Validate the local, append-only lesson-ledger seed.

The ledger is deliberately not a selector or a contract register.  It records
retro-cited lesson transitions and checks that its materialized view is exactly
the deterministic fold of those transitions.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.recent_lessons_lib import build_lesson_selection_index

LEDGER_FILENAME = "lesson-ledger.json"
KIND = "charness.lesson-ledger"
SCHEMA_VERSION = 1
TOP_LEVEL_KEYS = {"kind", "schema_version", "transitions", "lessons"}
TRANSITION_KEYS = {"sequence", "transition_id", "lesson_id", "source_retro"}
LESSON_KEYS = {"source_retro", "transition_id"}


def lesson_ledger_path(output_dir: Path) -> Path:
    return output_dir / LEDGER_FILENAME


def _candidate_sources(repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, set[str]]:
    index = build_lesson_selection_index(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    sources: dict[str, set[str]] = {}
    for candidate in index["candidates"]:
        lesson_id = candidate.get("recurrence_class")
        if not isinstance(lesson_id, str):
            continue
        sources[lesson_id] = {str(source["artifact_path"]) for source in candidate["sources"]}
    return sources


def _fail(message: str) -> None:
    raise ValueError(f"lesson ledger invalid: {message}")


def _committed_transitions(repo_root: Path, path: Path) -> list[dict[str, Any]] | None:
    relative = path.relative_to(repo_root)
    result = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode:
        return None
    previous = json.loads(result.stdout)
    return previous.get("transitions") if isinstance(previous, dict) and isinstance(previous.get("transitions"), list) else None


def validate_lesson_ledger(*, repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, Any]:  # noqa: C901
    path = lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON: {exc.msg}")
    if not isinstance(payload, dict) or payload.get("kind") != KIND or payload.get("schema_version") != SCHEMA_VERSION:
        _fail(f"expected kind `{KIND}` at schema version {SCHEMA_VERSION}")
    if set(payload) != TOP_LEVEL_KEYS:
        _fail("unexpected or missing top-level fields")
    transitions = payload.get("transitions")
    lessons = payload.get("lessons")
    if not isinstance(transitions, list) or not isinstance(lessons, dict):
        _fail("`transitions` must be a list and `lessons` an object")

    available_sources = _candidate_sources(repo_root, output_dir, summary_path)
    replayed: dict[str, dict[str, str]] = {}
    transition_ids: set[str] = set()
    for expected_sequence, transition in enumerate(transitions, start=1):
        if not isinstance(transition, dict):
            _fail(f"transition {expected_sequence} must be an object")
        if set(transition) != TRANSITION_KEYS:
            _fail(f"transition {expected_sequence} has deferred graduation/register fields or lacks a required field")
        transition_id = transition.get("transition_id")
        lesson_id = transition.get("lesson_id")
        source_retro = transition.get("source_retro")
        if transition.get("sequence") != expected_sequence:
            _fail("transition sequences must start at 1 and be contiguous")
        if not all(isinstance(value, str) and value for value in (transition_id, lesson_id, source_retro)):
            _fail(f"transition {expected_sequence} needs non-empty transition_id, lesson_id, and source_retro")
        if transition_id in transition_ids:
            _fail(f"duplicate transition_id `{transition_id}`")
        transition_ids.add(transition_id)
        if lesson_id in replayed:
            _fail(f"duplicate lesson_id `{lesson_id}`")
        if lesson_id not in available_sources or source_retro not in available_sources[lesson_id]:
            _fail(f"transition `{transition_id}` citation does not declare recurrence-class `{lesson_id}`")
        replayed[lesson_id] = {"source_retro": source_retro, "transition_id": transition_id}
    if any(not isinstance(entry, dict) or set(entry) != LESSON_KEYS for entry in lessons.values()):
        _fail("materialized lessons may contain only source_retro and transition_id")
    committed = _committed_transitions(repo_root, path)
    if committed is not None and transitions[: len(committed)] != committed:
        _fail("committed transitions were rewritten or removed; append new transitions instead")
    if lessons != replayed:
        _fail("materialized lessons do not equal the deterministic transition replay")
    return {"lesson_count": len(replayed), "transition_count": len(transitions), "path": str(path.relative_to(repo_root))}
