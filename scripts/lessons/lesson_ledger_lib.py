"""Validate the append-only lesson ledger and its deterministic projections."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.git_checkout import head_oid_from_files  # noqa: E402
from scripts.lessons import lesson_score_outcome_lib as outcome_lib  # noqa: E402
from scripts.lessons.recent_lessons_lib import build_lesson_selection_index  # noqa: E402
from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

LEDGER_FILENAME = "lesson-ledger.json"
KIND = "charness.lesson-ledger"
# 9 restores explicit archive/resurrection lifecycle decisions. The v8 ledger
# remains readable and is upgraded by adding the lifecycle fields with every
# existing lesson active and no prior lifecycle event.
# 8 removed lesson archive/resurrection lifecycle state alongside the retired
# session-emission snapshots and session-bound scoring. The ledger is durable
# lesson history; presentation is an advisory projection owned by retro and is
# never a ledger event.
# 6 retired the signed `-3..3` scalar in favour of the typed outcome vocabulary
# in `lesson_score_outcome_lib`. Bumped rather than added additively because
# `score_total` changed MEANING -- it is now a sum of per-encounter valences, so
# a v5 consumer reading a v6 ledger would report a magnitude nobody recorded.
SCHEMA_VERSION = 9
PREVIOUS_SCHEMA_VERSION = 8
ACTIVE_LESSON_BUDGET = 50
TOP_LEVEL_KEYS = {
    "kind",
    "schema_version",
    "transitions",
    "active_lesson_budget",
    "lifecycle_events",
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
# Score-event shape, vocabulary, and citation now live in
# `lesson_score_outcome_lib`: they are ONE concept (what an encounter record
# means) that this module only replays, and keeping them here is what let the
# seeding rule and the scoring rule share a line for as long as they did.
LESSON_KEYS = {
    "source_retro",
    "transition_id",
    # The RANKING statistic, and no longer a magnitude sum: each encounter
    # contributes +1 or -1 via `outcome_lib.valence`. `outcome_counts` carries
    # the split the dispositions are routed by, because a scalar cannot tell
    # "the lesson is defective" from "the lesson may be perfect and never
    # landed", and those are different repairs.
    "score_total",
    "score_count",
    "outcome_counts",
    "state",
    "last_lifecycle_event_id",
}
# The whole lifecycle state machine as data, so the refusal can enumerate the
# legal moves instead of restating a rule the reader has to infer from a
# rejection. Kept as the branch table itself rather than a parallel constant:
# a message listing actions that the code no longer accepts is worse than no
# message, and this shape makes that drift impossible.
LIFECYCLE_TRANSITIONS = {("archive", "active"): "archived", ("resurrect", "archived"): "active"}
# The exact v8 shape accepted for migration. Keeping this separate from the v9
# shape makes the one-way compatibility boundary explicit.
V8_TOP_LEVEL_KEYS = {
    "kind",
    "schema_version",
    "transitions",
    "score_events",
    "lessons",
}
# How a lesson becomes seedable at all. Named once because it is the answer to
# every "nothing is eligible" dead end downstream (#621): a bullet with no
# `recurrence-class:` tag produces a candidate whose class is `None`, which
# `candidate_sources` drops, so no transition citing it can ever validate.
RECURRENCE_TAG_INSTRUCTION = (
    "a lesson becomes seedable only when a bullet in the cited retro carries a "
    "`recurrence-class: <slug>` tag whose slug equals the lesson_id"
)


def lesson_ledger_path(output_dir: Path) -> Path:
    return output_dir / LEDGER_FILENAME


def migrate_ledger_payload(payload: Any) -> tuple[Any, bool]:
    """Add the restored lifecycle shape to an on-disk v8 payload.

    The append-only transition and score histories are copied unchanged. A v8
    lesson had no lifecycle state, so migration gives every lesson the exact
    defaults used by a freshly seeded v9 lesson.
    """
    if (
        isinstance(payload, dict)
        and payload.get("kind") == KIND
        and payload.get("schema_version") == PREVIOUS_SCHEMA_VERSION
        and set(payload) == V8_TOP_LEVEL_KEYS
    ):
        migrated = copy.deepcopy(payload)
        migrated["schema_version"] = SCHEMA_VERSION
        migrated["active_lesson_budget"] = ACTIVE_LESSON_BUDGET
        migrated["lifecycle_events"] = []
        lessons = migrated.get("lessons")
        if isinstance(lessons, dict):
            for lesson in lessons.values():
                if isinstance(lesson, dict):
                    lesson["state"] = "active"
                    lesson["last_lifecycle_event_id"] = None
        return migrated, True
    return payload, False


def _fail(message: str) -> None:
    raise ValueError(f"lesson ledger invalid: {message}")


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def candidate_sources(
    repo_root: Path, output_dir: Path, summary_path: Path | None
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


_COMMITTED_LEDGER_CACHE: dict[
    tuple[str, str, str], tuple[list[Any], list[Any], int, list[Any]] | None
] = {}


def _committed_state(
    repo_root: Path, path: Path
) -> tuple[list[Any], list[Any], int, list[Any]] | None:
    relative = path.relative_to(repo_root).as_posix()
    head = head_oid_from_files(repo_root)
    cache_key = (str(repo_root.resolve()), relative, head) if head else None
    if cache_key is not None and cache_key in _COMMITTED_LEDGER_CACHE:
        return _COMMITTED_LEDGER_CACHE[cache_key]
    result = run_process(
        ["git", "show", f"HEAD:{relative}"],
        cwd=repo_root,
        timeout_seconds=None,
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
    # A newer committed schema must never be overwritten by an older writer.
    committed_version = previous.get("schema_version")
    if type(committed_version) is not int:
        _fail(
            f"committed ledger has a non-integer schema_version {committed_version!r}; it cannot be "
            "compared against this tool's, so refuse rather than assume it is older"
        )
    if committed_version > SCHEMA_VERSION:
        _fail(
            f"committed ledger is at schema version {committed_version}, newer than this tool's "
            f"{SCHEMA_VERSION}; upgrade the tool rather than writing an older shape over it"
        )
    if committed_version not in {PREVIOUS_SCHEMA_VERSION, SCHEMA_VERSION}:
        _fail(
            f"committed ledger is at unsupported schema version {committed_version}; "
            f"this writer only accepts v{SCHEMA_VERSION}"
        )
    if committed_version == PREVIOUS_SCHEMA_VERSION:
        if set(previous) == V8_TOP_LEVEL_KEYS and isinstance(previous.get("score_events"), list):
            payload = (
                previous["transitions"],
                previous["score_events"],
                ACTIVE_LESSON_BUDGET,
                [],
            )
            if cache_key is not None:
                _COMMITTED_LEDGER_CACHE[cache_key] = payload
            return payload
        _fail("committed ledger is missing a required append-only list")
    if (
        isinstance(previous.get("score_events"), list)
        and isinstance(previous.get("lifecycle_events"), list)
        and type(previous.get("active_lesson_budget")) is int
    ):
        payload = (
            previous["transitions"],
            previous["score_events"],
            previous["active_lesson_budget"],
            previous["lifecycle_events"],
        )
        if cache_key is not None:
            _COMMITTED_LEDGER_CACHE[cache_key] = payload
        return payload
    _fail("committed ledger is missing a required append-only list or its budget")


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
            # Every outcome key present at zero, for every seeded lesson, so an
            # unscored lesson renders as "no encounters yet" rather than as a
            # missing field a consumer has to guess the meaning of.
            "outcome_counts": outcome_lib.outcome_counts([]),
            "state": "active",
            "last_lifecycle_event_id": None,
        }
    return replayed


# An append-only lifecycle event that cites a human decision must cite an existing
# canonical repo-relative Markdown file. The predicate is kept beside the ledger
# replay that consumes it so lifecycle writes and validation share one rule.
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
            legal = sorted(
                f"{move} a lesson in state `{state}`" for move, state in LIFECYCLE_TRANSITIONS
            )
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


def _replay_scores(
    events: list[Any],
    replayed: dict[str, dict[str, Any]],
    available_sources: dict[str, set[str]],
) -> None:
    ids: set[str] = set()
    sources: set[tuple[str, str]] = set()
    scored: dict[str, list[dict[str, Any]]] = {}
    prefix_error = outcome_lib.legacy_prefix_error(events)
    if prefix_error is not None:
        _fail(prefix_error)
    for position, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            _fail(f"score event {position} is not an object")
        shape_error = outcome_lib.score_event_error(event)
        if shape_error is not None:
            _fail(f"score event {position} {shape_error}")
        event_id, source, lesson_id = (
            event.get(key) for key in ("event_id", "source_retro", "lesson_id")
        )
        if not all(_nonblank(value) for value in (event_id, source, lesson_id)):
            _fail(
                f"score event {position} needs non-empty non-whitespace event_id, source_retro, and lesson_id"
            )
        if event_id in ids or (source, lesson_id) in sources:
            _fail(f"duplicate score event_id or score source for `{lesson_id}`")
        if lesson_id not in replayed:
            _fail(f"score event `{event_id}` names an unseeded lesson")
        # Seeding cites evidence that the class exists. Current score events keep
        # a stable repo-relative citation for the encounter; legacy events retain
        # their original tagged-source rule.
        if outcome_lib.is_legacy_scalar(event):
            if source not in available_sources.get(lesson_id, set()):
                _fail(f"score event `{event_id}` names an invalid legacy citation")
        elif not outcome_lib.canonical_retro_citation(source):
            _fail(
                f"score event `{event_id}` source_retro must be a repo-relative "
                f"`{outcome_lib.RETRO_DIR}/<name>.md` path naming the retro that records the encounter"
            )
        ids.add(event_id)
        sources.add((source, lesson_id))
        scored.setdefault(lesson_id, []).append(event)
        replayed[lesson_id]["score_total"] += outcome_lib.valence(event)
        replayed[lesson_id]["score_count"] += 1
    for lesson_id, entry in replayed.items():
        entry["outcome_counts"] = outcome_lib.outcome_counts(scored.get(lesson_id, []))


def replay_validated_ledger_payload(
    *, repo_root: Path, output_dir: Path, summary_path: Path | None, path: Path, payload: Any
) -> dict[str, dict[str, Any]]:
    payload, _ = migrate_ledger_payload(payload)
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
    transitions, events, lessons, lifecycle_events, budget = (
        payload.get(key)
        for key in (
            "transitions",
            "score_events",
            "lessons",
            "lifecycle_events",
            "active_lesson_budget",
        )
    )
    if not all(
        isinstance(value, expected)
        for value, expected in (
            (transitions, list),
            (events, list),
            (lessons, dict),
            (lifecycle_events, list),
        )
    ):
        _fail("ledger has invalid containers")
    available = candidate_sources(repo_root, output_dir, summary_path)
    replayed = _replay_transitions(transitions, available)
    _replay_lifecycle(lifecycle_events, replayed, budget=budget, repo_root=repo_root)
    committed = _committed_state(repo_root, path)
    if committed is not None:
        old_transitions, old_events, old_budget, old_lifecycle = committed
        if transitions[: len(old_transitions)] != old_transitions:
            _fail("committed transitions were rewritten or removed; append new transitions instead")
        if events[: len(old_events)] != old_events:
            _fail("committed score events were rewritten or removed; append new events instead")
        if budget != old_budget:
            _fail("committed active_lesson_budget was rewritten")
        if lifecycle_events[: len(old_lifecycle)] != old_lifecycle:
            _fail("committed lifecycle events were rewritten or removed; append new events instead")
    _replay_scores(events, replayed, available)
    if any(
        not isinstance(entry, dict)
        or set(entry) != LESSON_KEYS
        or type(entry["score_total"]) is not int
        or type(entry["score_count"]) is not int
        or not isinstance(entry["outcome_counts"], dict)
        or set(entry["outcome_counts"]) != set(outcome_lib.outcome_counts([]))
        or any(type(count) is not int or count < 0 for count in entry["outcome_counts"].values())
        for entry in lessons.values()
    ):
        _fail(
            f"materialized lessons may contain only replayed fields; each lesson takes exactly "
            f"keys {sorted(LESSON_KEYS)} with integer score_total and score_count, and an "
            f"outcome_counts map over exactly {sorted(outcome_lib.outcome_counts([]))}"
        )
    if lessons != replayed:
        _fail("materialized lessons do not equal deterministic replay")
    return replayed


def validate_lesson_ledger(
    *, repo_root: Path, output_dir: Path, summary_path: Path | None
) -> dict[str, Any]:
    path = lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON: {exc.msg}")
    # Migrate IN MEMORY only. This function validates; it must not write.
    #
    # It used to persist the upgrade through the atomic writer, and the read paths
    # are what made that unsafe: `lesson_selection_preview_lib` calls this, and
    # `AGENTS.md` makes the preview the FIRST command a session runs. So merely
    # OPENING a session silently upgraded a consumer's ledger to a schema the
    # previously released version cannot read, while the release notes prescribe
    # rollback by reinstalling that version. Measured, not reasoned: a schema-8
    # ledger seeded into a probe repo came back schema 9 after nothing but
    # `render_lesson_selection_preview.py`.
    #
    # Nothing is lost by dropping the write. Every durable writer -- score,
    # lifecycle, and seed -- already migrates inside its own lock before writing,
    # so the upgrade still lands on the first authorized write and lands there once.
    payload, _migrated = migrate_ledger_payload(payload)
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
        "active_lesson_count": sum(lesson["state"] == "active" for lesson in replayed.values()),
        "path": str(path.relative_to(repo_root)),
    }
