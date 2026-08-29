"""One derived-`lessons` materializer for every ledger test fixture.

WHY SHARED (S3, 2026-08-15). Eight test files each carried their own copy of
"what the `lessons` map should look like given these events", and the schema-6
outcome vocabulary had to change all eight identically. A fixture that
INDEPENDENTLY reconstructs the derived view is the whole point -- handing the
validator its own replay output would make `lessons != replayed` tautological --
but eight copies of that reconstruction buy no extra independence over one, and
they cost every future schema change eight chances to diverge silently.

So: one reconstruction, still written against the CONTRACT rather than against
`lesson_ledger_lib`'s replay. It walks the events itself and applies the rules as
a reader of the spec would state them. The one thing it imports from production
is the outcome KEY SET, because a hand-written literal there would drift the
first time the vocabulary changes and every test would then pass against a map
the validator rejects for a reason unrelated to what the test is about.
"""

from __future__ import annotations

import copy
from typing import Any

from scripts import lesson_score_outcome_lib as outcome_lib


def blank_lesson(source_retro: str, transition_id: str) -> dict[str, Any]:
    """A freshly seeded lesson: active, no encounters."""
    return {
        "source_retro": source_retro,
        "transition_id": transition_id,
        "score_total": 0,
        "score_count": 0,
        "outcome_counts": outcome_lib.outcome_counts([]),
        "state": "active",
        "last_lifecycle_event_id": None,
    }


def outcome_event(
    *,
    event_id: str,
    lesson_id: str,
    source_retro: str,
    outcome: str = "changed-an-action",
    anchor: str | None = None,
) -> dict[str, Any]:
    """One schema-9 encounter record.

    The default anchor satisfies the `changed-an-action` counterfactual bar, so a
    test that does not care about anchor shape does not have to know the rule.
    A test that DOES care passes its own and asserts the refusal.
    """
    if anchor is None:
        anchor = "took the measured path here rather than the assumed one, which would have shipped a false count"
    return {
        "event_id": event_id,
        "source_retro": source_retro,
        "lesson_id": lesson_id,
        "outcome": outcome,
        "anchor": anchor,
    }


def materialize(payload: dict[str, Any]) -> dict[str, Any]:
    """Recompute `lessons` from the payload's events, in place.

    Stated as the contract states it: every score event is one encounter, and
    `score_total` is a sum of VALENCES (+1 when the
    lesson did its job, -1 otherwise) rather than of magnitudes -- including for
    legacy-scalar events, which contribute the sign of their scalar and never its
    size.
    """
    for lesson in payload["lessons"].values():
        lesson["score_total"] = 0
        lesson["score_count"] = 0
        lesson["outcome_counts"] = outcome_lib.outcome_counts([])
        lesson["state"] = "active"
        lesson["last_lifecycle_event_id"] = None
    for event in payload["lifecycle_events"]:
        lesson = payload["lessons"].get(event["lesson_id"])
        if lesson is not None:
            lesson["state"] = "archived" if event["action"] == "archive" else "active"
            lesson["last_lifecycle_event_id"] = event["event_id"]
    scored: dict[str, list[dict[str, Any]]] = {}
    for event in payload["score_events"]:
        lesson = payload["lessons"].get(event["lesson_id"])
        if lesson is None:
            continue
        scored.setdefault(event["lesson_id"], []).append(event)
        score = event.get("score")
        if "score" in event:
            lesson["score_total"] += (score > 0) - (score < 0)
        else:
            lesson["score_total"] += 1 if event.get("outcome") == "changed-an-action" else -1
        lesson["score_count"] += 1
    for lesson_id, events in scored.items():
        payload["lessons"][lesson_id]["outcome_counts"] = outcome_lib.outcome_counts(events)
    return payload


def legacy_v8_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the pre-lifecycle v8 shape without changing append-only history."""
    legacy = copy.deepcopy(payload)
    legacy["schema_version"] = 8
    legacy.pop("active_lesson_budget", None)
    legacy.pop("lifecycle_events", None)
    for lesson in legacy.get("lessons", {}).values():
        lesson.pop("state", None)
        lesson.pop("last_lifecycle_event_id", None)
    return legacy
