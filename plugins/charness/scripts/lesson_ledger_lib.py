"""Validate the local, append-only lesson ledger and its replayed scores.

The ledger is deliberately not a selector or a contract register. It records
retro-cited lesson transitions and score events, then checks that its
materialized view is exactly their deterministic replay.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.recent_lessons_lib import build_lesson_selection_index

LEDGER_FILENAME = "lesson-ledger.json"
KIND = "charness.lesson-ledger"
SCHEMA_VERSION = 2
TOP_LEVEL_KEYS = {"kind", "schema_version", "transitions", "score_events", "lessons"}
TRANSITION_KEYS = {"sequence", "transition_id", "lesson_id", "source_retro"}
EVENT_REQUIRED_KEYS = {"event_id", "source_retro", "lesson_id", "score"}
EVENT_OPTIONAL_KEYS = {"anchor"}
LESSON_KEYS = {"source_retro", "transition_id", "score_total", "score_count"}


def lesson_ledger_path(output_dir: Path) -> Path:
    return output_dir / LEDGER_FILENAME


def _candidate_sources(repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, set[str]]:
    index = build_lesson_selection_index(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    sources: dict[str, set[str]] = {}
    for candidate in index["candidates"]:
        lesson_id = candidate.get("recurrence_class")
        if isinstance(lesson_id, str):
            sources[lesson_id] = {str(source["artifact_path"]) for source in candidate["sources"]}
    return sources


def _fail(message: str) -> None:
    raise ValueError(f"lesson ledger invalid: {message}")


def _committed_state(repo_root: Path, path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | None:
    relative = path.relative_to(repo_root)
    result = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode:
        return None
    try:
        previous = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        _fail(f"committed ledger is invalid JSON: {exc.msg}")
    if not isinstance(previous, dict) or previous.get("kind") != KIND:
        _fail("committed ledger has an unrecognized shape")
    if not isinstance(previous.get("transitions"), list):
        _fail("committed ledger has no transition list")
    if previous.get("schema_version") == 1:
        return previous["transitions"], []
    if previous.get("schema_version") != SCHEMA_VERSION or not isinstance(previous.get("score_events"), list):
        _fail("committed ledger has an unsupported score-event shape")
    return previous["transitions"], previous["score_events"]


def _replay_transitions(transitions: list[Any], available_sources: dict[str, set[str]]) -> dict[str, dict[str, Any]]:
    replayed: dict[str, dict[str, Any]] = {}
    transition_ids: set[str] = set()
    for expected_sequence, transition in enumerate(transitions, start=1):
        if not isinstance(transition, dict):
            _fail(f"transition {expected_sequence} must be an object")
        if set(transition) != TRANSITION_KEYS:
            _fail(f"transition {expected_sequence} has deferred graduation/register fields or lacks a required field")
        transition_id = transition.get("transition_id")
        lesson_id = transition.get("lesson_id")
        source_retro = transition.get("source_retro")
        if type(transition.get("sequence")) is not int or transition["sequence"] != expected_sequence:
            _fail("transition sequences must start at 1 and be contiguous")
        if not all(isinstance(value, str) and value for value in (transition_id, lesson_id, source_retro)):
            _fail(f"transition {expected_sequence} needs non-empty transition_id, lesson_id, and source_retro")
        if transition_id in transition_ids:
            _fail(f"duplicate transition_id `{transition_id}`")
        if lesson_id in replayed:
            _fail(f"duplicate lesson_id `{lesson_id}`")
        if source_retro not in available_sources.get(lesson_id, set()):
            _fail(f"transition `{transition_id}` citation does not declare recurrence-class `{lesson_id}`")
        transition_ids.add(transition_id)
        replayed[lesson_id] = {
            "source_retro": source_retro,
            "transition_id": transition_id,
            "score_total": 0,
            "score_count": 0,
        }
    return replayed


def _replay_scores(score_events: list[Any], replayed: dict[str, dict[str, Any]], available_sources: dict[str, set[str]]) -> None:
    event_ids: set[str] = set()
    scored_sources: set[tuple[str, str]] = set()
    for position, event in enumerate(score_events, start=1):
        if not isinstance(event, dict) or not EVENT_REQUIRED_KEYS <= set(event) <= EVENT_REQUIRED_KEYS | EVENT_OPTIONAL_KEYS:
            _fail(f"score event {position} has unexpected or missing fields")
        event_id = event.get("event_id")
        source_retro = event.get("source_retro")
        lesson_id = event.get("lesson_id")
        score = event.get("score")
        anchor = event.get("anchor")
        if not all(isinstance(value, str) and value for value in (event_id, source_retro, lesson_id)):
            _fail(f"score event {position} needs non-empty event_id, source_retro, and lesson_id")
        if type(score) is not int or not -3 <= score <= 3:
            _fail(f"score event `{event_id}` score must be an integer in -3..3")
        if "anchor" in event and (not isinstance(anchor, str) or not anchor):
            _fail(f"score event `{event_id}` anchor must be a non-empty string when present")
        if abs(score) >= 2 and "anchor" not in event:
            _fail(f"score event `{event_id}` with magnitude at least two needs an anchor")
        if event_id in event_ids:
            _fail(f"duplicate score event_id `{event_id}`")
        if lesson_id not in replayed:
            _fail(f"score event `{event_id}` names unseeded lesson `{lesson_id}`")
        if source_retro not in available_sources.get(lesson_id, set()):
            _fail(f"score event `{event_id}` citation does not declare recurrence-class `{lesson_id}`")
        source_key = (source_retro, lesson_id)
        if source_key in scored_sources:
            _fail(f"duplicate score for lesson `{lesson_id}` from `{source_retro}`")
        event_ids.add(event_id)
        scored_sources.add(source_key)
        replayed[lesson_id]["score_total"] += score
        replayed[lesson_id]["score_count"] += 1


def validate_lesson_ledger(*, repo_root: Path, output_dir: Path, summary_path: Path) -> dict[str, Any]:
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
    score_events = payload.get("score_events")
    lessons = payload.get("lessons")
    if not isinstance(transitions, list) or not isinstance(score_events, list) or not isinstance(lessons, dict):
        _fail("transitions and score_events must be lists and lessons an object")

    available_sources = _candidate_sources(repo_root, output_dir, summary_path)
    replayed = _replay_transitions(transitions, available_sources)
    _replay_scores(score_events, replayed, available_sources)
    if any(not isinstance(entry, dict) or set(entry) != LESSON_KEYS for entry in lessons.values()):
        _fail("materialized lessons may contain only seed provenance and replayed score fields")
    for lesson_id, entry in lessons.items():
        if type(entry["score_total"]) is not int or type(entry["score_count"]) is not int:
            _fail(f"materialized lesson `{lesson_id}` score fields must be integers")
    committed = _committed_state(repo_root, path)
    if committed is not None:
        committed_transitions, committed_events = committed
        if transitions[: len(committed_transitions)] != committed_transitions:
            _fail("committed transitions were rewritten or removed; append new transitions instead")
        if score_events[: len(committed_events)] != committed_events:
            _fail("committed score events were rewritten or removed; append new events instead")
    if lessons != replayed:
        _fail("materialized lessons do not equal the deterministic transition and score-event replay")
    return {
        "lesson_count": len(replayed),
        "transition_count": len(transitions),
        "score_event_count": len(score_events),
        "path": str(path.relative_to(repo_root)),
    }
