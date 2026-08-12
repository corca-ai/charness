"""Validate append-only lesson seeds, declared sessions, and cited scores."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.recent_lessons_lib import build_lesson_selection_index

LEDGER_FILENAME = "lesson-ledger.json"
KIND = "charness.lesson-ledger"
SCHEMA_VERSION = 3
TOP_LEVEL_KEYS = {
    "kind",
    "schema_version",
    "transitions",
    "legacy_score_event_count",
    "session_events",
    "score_events",
    "lessons",
}
TRANSITION_KEYS = {"sequence", "transition_id", "lesson_id", "source_retro"}
LEGACY_EVENT_KEYS = {"event_id", "source_retro", "lesson_id", "score"}
EVENT_OPTIONAL_KEYS = {"anchor"}
SCORE_EVENT_KEYS = LEGACY_EVENT_KEYS | {"session_id"}
SESSION_EVENT_KEYS = {"session_id", "snapshot", "snapshot_sha256"}
SNAPSHOT_KEYS = {
    "kind",
    "schema_version",
    "selection_policy_version",
    "seed",
    "eligible_count",
    "bucket_counts",
    "lesson_ids",
}
LESSON_KEYS = {"source_retro", "transition_id", "score_total", "score_count"}
PREVIEW_KIND = "charness.lesson-selection-preview"
PREVIEW_SCHEMA_VERSION = 1
SNAPSHOT_BUCKET_KEYS = {"recent", "value", "uncertainty", "archive", "archive_fallback_uncertainty"}


def lesson_ledger_path(output_dir: Path) -> Path:
    return output_dir / LEDGER_FILENAME


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def snapshot_sha256(snapshot: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(snapshot).encode("utf-8")).hexdigest()


def _fail(message: str) -> None:
    raise ValueError(f"lesson ledger invalid: {message}")


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _candidate_sources(
    repo_root: Path, output_dir: Path, summary_path: Path
) -> dict[str, set[str]]:
    index = build_lesson_selection_index(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )
    return {
        candidate["recurrence_class"]: {
            str(source["artifact_path"]) for source in candidate["sources"]
        }
        for candidate in index["candidates"]
        if isinstance(candidate.get("recurrence_class"), str)
    }


def _committed_state(
    repo_root: Path, path: Path
) -> tuple[list[Any], list[Any], int, list[Any]] | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{path.relative_to(repo_root)}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        return None
    try:
        previous = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        _fail(f"committed ledger is invalid JSON: {exc.msg}")
    if (
        not isinstance(previous, dict)
        or previous.get("kind") != KIND
        or not isinstance(previous.get("transitions"), list)
    ):
        _fail("committed ledger has an unrecognized shape")
    version = previous.get("schema_version")
    if version == 1:
        return previous["transitions"], [], 0, []
    if version == 2 and isinstance(previous.get("score_events"), list):
        return previous["transitions"], previous["score_events"], len(previous["score_events"]), []
    if (
        version == SCHEMA_VERSION
        and isinstance(previous.get("score_events"), list)
        and isinstance(previous.get("session_events"), list)
        and type(previous.get("legacy_score_event_count")) is int
    ):
        return (
            previous["transitions"],
            previous["score_events"],
            previous["legacy_score_event_count"],
            previous["session_events"],
        )
    _fail("committed ledger has an unsupported session shape")


def _replay_transitions(
    transitions: list[Any], available_sources: dict[str, set[str]]
) -> dict[str, dict[str, Any]]:
    replayed: dict[str, dict[str, Any]] = {}
    ids: set[str] = set()
    for sequence, transition in enumerate(transitions, start=1):
        if not isinstance(transition, dict) or set(transition) != TRANSITION_KEYS:
            _fail(f"transition {sequence} has deferred fields or lacks a required field")
        if type(transition.get("sequence")) is not int or transition["sequence"] != sequence:
            _fail("transition sequences must start at 1 and be contiguous")
        transition_id, lesson_id, source = (
            transition.get("transition_id"),
            transition.get("lesson_id"),
            transition.get("source_retro"),
        )
        if not all(_nonblank(value) for value in (transition_id, lesson_id, source)):
            _fail(
                f"transition {sequence} needs non-empty transition_id, lesson_id, and source_retro"
            )
        if transition_id in ids or lesson_id in replayed:
            _fail(f"duplicate transition_id or lesson_id `{transition_id}`")
        if source not in available_sources.get(lesson_id, set()):
            _fail(
                f"transition `{transition_id}` citation does not declare recurrence-class `{lesson_id}`"
            )
        ids.add(transition_id)
        replayed[lesson_id] = {
            "source_retro": source,
            "transition_id": transition_id,
            "score_total": 0,
            "score_count": 0,
        }
    return replayed


def _replay_sessions(events: list[Any], replayed: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    sessions: dict[str, set[str]] = {}
    for position, event in enumerate(events, start=1):
        if not isinstance(event, dict) or set(event) != SESSION_EVENT_KEYS:
            _fail(f"session event {position} has unexpected or missing fields")
        session_id, snapshot, digest = (
            event.get("session_id"),
            event.get("snapshot"),
            event.get("snapshot_sha256"),
        )
        if not _nonblank(session_id) or not isinstance(snapshot, dict) or not _nonblank(digest):
            _fail(f"session event {position} needs non-empty identity and snapshot")
        if session_id in sessions:
            _fail(f"duplicate session_id `{session_id}`")
        if set(snapshot) != SNAPSHOT_KEYS or not _nonblank(snapshot.get("seed")):
            _fail(f"session `{session_id}` has invalid snapshot shape")
        if (
            snapshot.get("kind") != PREVIEW_KIND
            or type(snapshot.get("schema_version")) is not int
            or snapshot["schema_version"] != PREVIEW_SCHEMA_VERSION
            or type(snapshot.get("selection_policy_version")) is not int
            or snapshot["selection_policy_version"] < 1
            or type(snapshot.get("eligible_count")) is not int
            or snapshot["eligible_count"] < 0
            or not isinstance(snapshot.get("bucket_counts"), dict)
        ):
            _fail(f"session `{session_id}` has invalid snapshot types")
        bucket_counts = snapshot["bucket_counts"]
        if set(bucket_counts) != SNAPSHOT_BUCKET_KEYS or any(
            type(count) is not int or count < 0 for count in bucket_counts.values()
        ):
            _fail(f"session `{session_id}` has invalid bucket_counts")
        lesson_ids = snapshot.get("lesson_ids")
        if (
            not isinstance(lesson_ids, list)
            or not lesson_ids
            or not all(_nonblank(item) for item in lesson_ids)
            or len(lesson_ids) != len(set(lesson_ids))
        ):
            _fail(f"session `{session_id}` lesson_ids must be a non-empty ordered unique list")
        if any(lesson_id not in replayed for lesson_id in lesson_ids):
            _fail(f"session `{session_id}` names unseeded lesson")
        if snapshot["eligible_count"] < len(lesson_ids) or sum(bucket_counts.values()) != len(
            lesson_ids
        ):
            _fail(f"session `{session_id}` has inconsistent snapshot counts")
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            _fail(f"session `{session_id}` snapshot_sha256 must be a lowercase SHA-256 digest")
        if digest != snapshot_sha256(snapshot):
            _fail(f"session `{session_id}` snapshot_sha256 does not match canonical snapshot")
        sessions[session_id] = set(lesson_ids)
    return sessions


def _replay_scores(
    events: list[Any],
    legacy_count: int,
    replayed: dict[str, dict[str, Any]],
    available_sources: dict[str, set[str]],
    sessions: dict[str, set[str]],
) -> None:
    ids: set[str] = set()
    sources: set[tuple[str, str]] = set()
    for position, event in enumerate(events, start=1):
        legacy = position <= legacy_count
        allowed = (
            LEGACY_EVENT_KEYS | EVENT_OPTIONAL_KEYS
            if legacy
            else SCORE_EVENT_KEYS | EVENT_OPTIONAL_KEYS
        )
        required = LEGACY_EVENT_KEYS if legacy else SCORE_EVENT_KEYS
        if not isinstance(event, dict) or not required <= set(event) <= allowed:
            _fail(f"score event {position} has unexpected or missing fields")
        event_id, source, lesson_id, score = (
            event.get(key) for key in ("event_id", "source_retro", "lesson_id", "score")
        )
        if not all(_nonblank(value) for value in (event_id, source, lesson_id)):
            _fail(
                f"score event {position} needs non-empty non-whitespace event_id, source_retro, and lesson_id"
            )
        if type(score) is not int or not -3 <= score <= 3:
            _fail(f"score event `{event_id}` score must be an integer in -3..3")
        anchor = event.get("anchor")
        if "anchor" in event and not _nonblank(anchor):
            _fail(f"score event `{event_id}` anchor must be non-empty non-whitespace when present")
        if abs(score) >= 2 and "anchor" not in event:
            _fail(f"score event `{event_id}` with magnitude at least two needs an anchor")
        if not legacy:
            session_id = event.get("session_id")
            if not _nonblank(session_id) or session_id not in sessions:
                _fail(f"score event `{event_id}` names unknown session")
            if lesson_id not in sessions[session_id]:
                _fail(f"score event `{event_id}` lesson is absent from session `{session_id}`")
        if event_id in ids or (source, lesson_id) in sources:
            _fail(f"duplicate score event_id or score source for `{lesson_id}`")
        if lesson_id not in replayed or source not in available_sources.get(lesson_id, set()):
            _fail(f"score event `{event_id}` names an unseeded lesson or invalid citation")
        ids.add(event_id)
        sources.add((source, lesson_id))
        replayed[lesson_id]["score_total"] += score
        replayed[lesson_id]["score_count"] += 1


def replay_validated_ledger_payload(
    *, repo_root: Path, output_dir: Path, summary_path: Path, path: Path, payload: Any
) -> dict[str, dict[str, Any]]:
    if (
        not isinstance(payload, dict)
        or payload.get("kind") != KIND
        or payload.get("schema_version") != SCHEMA_VERSION
        or set(payload) != TOP_LEVEL_KEYS
    ):
        _fail(f"expected kind `{KIND}` at schema version {SCHEMA_VERSION}")
    transitions, events, sessions, lessons, legacy_count = (
        payload.get(key)
        for key in (
            "transitions",
            "score_events",
            "session_events",
            "lessons",
            "legacy_score_event_count",
        )
    )
    if (
        not all(
            isinstance(value, expected)
            for value, expected in (
                (transitions, list),
                (events, list),
                (sessions, list),
                (lessons, dict),
            )
        )
        or type(legacy_count) is not int
        or not 0 <= legacy_count <= len(events)
    ):
        _fail("ledger has invalid containers or legacy_score_event_count")
    available = _candidate_sources(repo_root, output_dir, summary_path)
    replayed = _replay_transitions(transitions, available)
    declared = _replay_sessions(sessions, replayed)
    committed = _committed_state(repo_root, path)
    if committed is None:
        if legacy_count != 0:
            _fail("legacy_score_event_count is only allowed when migrating a committed v2 ledger")
    else:
        old_transitions, old_events, old_legacy, old_sessions = committed
        if transitions[: len(old_transitions)] != old_transitions:
            _fail("committed transitions were rewritten or removed; append new transitions instead")
        if events[: len(old_events)] != old_events:
            _fail("committed score events were rewritten or removed; append new events instead")
        if sessions[: len(old_sessions)] != old_sessions:
            _fail("committed session events were rewritten or removed; append new events instead")
        if legacy_count != old_legacy:
            _fail("committed legacy_score_event_count was rewritten")
    _replay_scores(events, legacy_count, replayed, available, declared)
    if any(
        not isinstance(entry, dict)
        or set(entry) != LESSON_KEYS
        or type(entry["score_total"]) is not int
        or type(entry["score_count"]) is not int
        for entry in lessons.values()
    ):
        _fail("materialized lessons may contain only integer replay fields")
    if lessons != replayed:
        _fail("materialized lessons do not equal deterministic replay")
    return replayed


def validate_lesson_ledger(
    *, repo_root: Path, output_dir: Path, summary_path: Path
) -> dict[str, Any]:
    path = lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON: {exc.msg}")
    replayed = replay_validated_ledger_payload(
        repo_root=repo_root,
        output_dir=output_dir,
        summary_path=summary_path,
        path=path,
        payload=payload,
    )
    return {
        "lesson_count": len(replayed),
        "transition_count": len(payload["transitions"]),
        "score_event_count": len(payload["score_events"]),
        "path": str(path.relative_to(repo_root)),
    }
