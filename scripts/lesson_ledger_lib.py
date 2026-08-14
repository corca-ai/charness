"""Validate append-only lesson seeds, sessions, scores, and lifecycle events."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.recent_lessons_lib import build_lesson_selection_index

LEDGER_FILENAME = "lesson-ledger.json"
KIND = "charness.lesson-ledger"
SCHEMA_VERSION = 5
ACTIVE_LESSON_BUDGET = 50
TOP_LEVEL_KEYS = {
    "kind",
    "schema_version",
    "transitions",
    "active_lesson_budget",
    "lifecycle_events",
    "session_events",
    "score_events",
    "lessons",
}
TRANSITION_KEYS = {"sequence", "transition_id", "lesson_id", "source_retro"}
LIFECYCLE_EVENT_KEYS = {
    "sequence",
    "event_id",
    "lesson_id",
    "action",
    "decision_ref",
    "rationale",
}
SCORE_EVENT_REQUIRED_KEYS = {"event_id", "source_retro", "lesson_id", "score", "session_id"}
EVENT_OPTIONAL_KEYS = {"anchor"}
SCORE_EVENT_KEYS = SCORE_EVENT_REQUIRED_KEYS | EVENT_OPTIONAL_KEYS
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
LESSON_KEYS = {
    "source_retro",
    "transition_id",
    "score_total",
    "score_count",
    "state",
    "last_lifecycle_event_id",
}
PREVIEW_KIND = "charness.lesson-selection-preview"
PREVIEW_SCHEMA_VERSION = 1
SNAPSHOT_BUCKET_KEYS = {"recent", "value", "uncertainty", "archive", "archive_fallback_uncertainty"}
# The whole lifecycle state machine as data, so the refusal below can ENUMERATE
# the legal moves instead of restating a rule the reader has to infer from a
# rejection. Kept as the branch table itself rather than a parallel constant:
# a message listing actions that the code no longer accepts is worse than no
# message, and this shape makes that drift impossible.
LIFECYCLE_TRANSITIONS = {("archive", "active"): "archived", ("resurrect", "archived"): "active"}
# How a lesson becomes seedable at all. Named once because it is the answer to
# every "nothing is eligible" dead end downstream (#621): a bullet with no
# `recurrence-class:` tag produces a candidate whose class is `None`, which
# `_candidate_sources` drops, so no transition citing it can ever validate.
RECURRENCE_TAG_INSTRUCTION = (
    "a lesson becomes seedable only when a bullet in the cited retro carries a "
    "`recurrence-class: <slug>` tag whose slug equals the lesson_id"
)


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
) -> tuple[list[Any], list[Any], list[Any], int, list[Any]] | None:
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
    if (
        previous.get("schema_version") == SCHEMA_VERSION
        and isinstance(previous.get("score_events"), list)
        and isinstance(previous.get("session_events"), list)
        and isinstance(previous.get("lifecycle_events"), list)
        and type(previous.get("active_lesson_budget")) is int
    ):
        return (
            previous["transitions"],
            previous["score_events"],
            previous["session_events"],
            previous["active_lesson_budget"],
            previous["lifecycle_events"],
        )
    _fail("committed ledger has an unsupported session shape")


def _replay_transitions(
    transitions: list[Any], available_sources: dict[str, set[str]]
) -> dict[str, dict[str, Any]]:
    replayed: dict[str, dict[str, Any]] = {}
    ids: set[str] = set()
    for sequence, transition in enumerate(transitions, start=1):
        if not isinstance(transition, dict) or set(transition) != TRANSITION_KEYS:
            _fail(
                f"transition {sequence} has deferred fields or lacks a required field; a transition "
                f"takes exactly keys {sorted(TRANSITION_KEYS)}"
            )
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
                f"transition `{transition_id}` citation does not declare recurrence-class "
                f"`{lesson_id}`; {RECURRENCE_TAG_INSTRUCTION}, and source_retro must be one of "
                "that tagged bullet's own retro artifacts"
            )
        ids.add(transition_id)
        replayed[lesson_id] = {
            "source_retro": source,
            "transition_id": transition_id,
            "score_total": 0,
            "score_count": 0,
            "state": "active",
            "last_lifecycle_event_id": None,
        }
    return replayed


# PUBLIC, and single-sourced, because it is ONE governance rule wearing two field
# names: an append-only ledger that cites a human decision must cite an EXISTING
# file, at a CANONICAL repo-relative posix path, that is Markdown. This module's
# `decision_ref` (which lifecycle event authorized archiving a lesson) and
# `contract_register_lib`'s `approval_ref` (which document approved a contract
# graduation) are the same rule, and they were verbatim-identical copies until
# 2026-08-14.
#
# Living here rather than in a new third module: `contract_register_lib` ALREADY
# imports `validate_lesson_ledger` and `lesson_ledger_path` from this module, so
# the import edge is pre-existing and no new failure surface is created -- if this
# module fails to import, the register validator was already dead. A new
# `scripts/` module would have added a mirrored export surface for nine lines.
#
# The obvious objection -- "now loosening one rule silently loosens two proof
# surfaces" -- is answered by the tests, not by copying the code: BOTH
# `tests/test_lesson_lifecycle_refusals.py` and `tests/test_contract_lifecycle_refusals.py`
# pin this predicate through their own module, so a loosening still fails each
# validator's own suite. Independent implementations would have bought
# independence of the rule at the cost of the two surfaces silently disagreeing
# about what a canonical reference is, which is the worse failure for governance
# refs that operators cross-read.
def canonical_markdown_ref(repo_root: Path, value: Any) -> bool:
    if not _nonblank(value):
        return False
    path = repo_root / value
    try:
        canonical = path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return False
    return value == canonical and path.suffix == ".md" and path.is_file()


def _replay_lifecycle(
    events: list[Any],
    replayed: dict[str, dict[str, Any]],
    *,
    budget: int,
    repo_root: Path,
) -> None:
    if type(budget) is not int or budget != ACTIVE_LESSON_BUDGET:
        _fail(f"active_lesson_budget must remain fixed at {ACTIVE_LESSON_BUDGET}")
    event_ids: set[str] = set()
    for sequence, event in enumerate(events, start=1):
        if not isinstance(event, dict) or set(event) != LIFECYCLE_EVENT_KEYS:
            _fail(
                f"lifecycle event {sequence} has unexpected or missing fields; a lifecycle event "
                f"takes exactly keys {sorted(LIFECYCLE_EVENT_KEYS)}"
            )
        if type(event.get("sequence")) is not int or event["sequence"] != sequence:
            _fail("lifecycle event sequences must start at 1 and be contiguous")
        event_id, lesson_id, action = (
            event.get("event_id"),
            event.get("lesson_id"),
            event.get("action"),
        )
        if not all(_nonblank(value) for value in (event_id, lesson_id, event.get("rationale"))):
            _fail(f"lifecycle event {sequence} needs non-empty identity and rationale")
        if event_id in event_ids:
            _fail(f"duplicate lifecycle event_id `{event_id}`")
        if lesson_id not in replayed:
            _fail(f"lifecycle event `{event_id}` names unseeded lesson")
        if not canonical_markdown_ref(repo_root, event.get("decision_ref")):
            _fail(f"lifecycle event `{event_id}` decision_ref is not existing canonical Markdown")
        current = replayed[lesson_id]["state"]
        next_state = LIFECYCLE_TRANSITIONS.get((action, current))
        if next_state is None:
            legal = sorted(f"{move} a lesson in state `{state}`" for move, state in LIFECYCLE_TRANSITIONS)
            _fail(
                f"lifecycle event `{event_id}` cannot {action} lesson in state `{current}`; the only "
                f"legal moves are {legal}"
            )
        replayed[lesson_id]["state"] = next_state
        replayed[lesson_id]["last_lifecycle_event_id"] = event_id
        event_ids.add(event_id)
    active_count = sum(lesson["state"] == "active" for lesson in replayed.values())
    if active_count > budget:
        _fail(f"active lesson count {active_count} exceeds fixed budget {budget}")


def _replay_sessions(events: list[Any], replayed: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    sessions: dict[str, set[str]] = {}
    for position, event in enumerate(events, start=1):
        if not isinstance(event, dict) or set(event) != SESSION_EVENT_KEYS:
            _fail(
                f"session event {position} has unexpected or missing fields; a session event takes "
                f"exactly keys {sorted(SESSION_EVENT_KEYS)}"
            )
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
            _fail(
                f"session `{session_id}` has invalid snapshot shape; a snapshot takes exactly keys "
                f"{sorted(SNAPSHOT_KEYS)} with a non-empty seed"
            )
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
            _fail(
                f"session `{session_id}` has invalid bucket_counts; bucket_counts takes exactly keys "
                f"{sorted(SNAPSHOT_BUCKET_KEYS)}, each a nonnegative integer"
            )
        lesson_ids = snapshot.get("lesson_ids")
        if (
            not isinstance(lesson_ids, list)
            or not lesson_ids
            or not all(_nonblank(item) for item in lesson_ids)
            or len(lesson_ids) != len(set(lesson_ids))
        ):
            _fail(
                f"session `{session_id}` lesson_ids must be a non-empty ordered unique list; an empty "
                f"list means the ledger has seeded no lesson yet, and {RECURRENCE_TAG_INSTRUCTION} "
                "(the ledger file itself is created by the `init_lesson_ledger.py` helper beside "
                "this module)"
            )
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
    replayed: dict[str, dict[str, Any]],
    available_sources: dict[str, set[str]],
    sessions: dict[str, set[str]],
) -> None:
    ids: set[str] = set()
    sources: set[tuple[str, str]] = set()
    for position, event in enumerate(events, start=1):
        if not isinstance(event, dict) or not SCORE_EVENT_REQUIRED_KEYS <= set(event) <= SCORE_EVENT_KEYS:
            _fail(
                f"score event {position} has unexpected or missing fields; a score event requires keys "
                f"{sorted(SCORE_EVENT_REQUIRED_KEYS)} and allows only {sorted(EVENT_OPTIONAL_KEYS)} beyond them"
            )
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
        _fail(
            f"expected kind `{KIND}` at schema version {SCHEMA_VERSION} with exactly the top-level "
            f"keys {sorted(TOP_LEVEL_KEYS)}"
        )
    transitions, events, sessions, lessons, lifecycle_events, budget = (
        payload.get(key)
        for key in (
            "transitions",
            "score_events",
            "session_events",
            "lessons",
            "lifecycle_events",
            "active_lesson_budget",
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
                (lifecycle_events, list),
            )
        )
    ):
        _fail("ledger has invalid containers")
    available = _candidate_sources(repo_root, output_dir, summary_path)
    replayed = _replay_transitions(transitions, available)
    _replay_lifecycle(lifecycle_events, replayed, budget=budget, repo_root=repo_root)
    declared = _replay_sessions(sessions, replayed)
    committed = _committed_state(repo_root, path)
    if committed is not None:
        old_transitions, old_events, old_sessions, old_budget, old_lifecycle = committed
        if transitions[: len(old_transitions)] != old_transitions:
            _fail("committed transitions were rewritten or removed; append new transitions instead")
        if events[: len(old_events)] != old_events:
            _fail("committed score events were rewritten or removed; append new events instead")
        if sessions[: len(old_sessions)] != old_sessions:
            _fail("committed session events were rewritten or removed; append new events instead")
        if budget != old_budget:
            _fail("committed active_lesson_budget was rewritten")
        if lifecycle_events[: len(old_lifecycle)] != old_lifecycle:
            _fail("committed lifecycle events were rewritten or removed; append new events instead")
    _replay_scores(events, replayed, available, declared)
    if any(
        not isinstance(entry, dict)
        or set(entry) != LESSON_KEYS
        or type(entry["score_total"]) is not int
        or type(entry["score_count"]) is not int
        for entry in lessons.values()
    ):
        _fail(
            f"materialized lessons may contain only integer replay fields; each lesson takes exactly "
            f"keys {sorted(LESSON_KEYS)} with integer score_total and score_count"
        )
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
        "lifecycle_event_count": len(payload["lifecycle_events"]),
        "active_lesson_count": sum(
            lesson["state"] == "active" for lesson in replayed.values()
        ),
        "path": str(path.relative_to(repo_root)),
    }
