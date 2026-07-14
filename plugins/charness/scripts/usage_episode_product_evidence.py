"""Product-evidence summaries for privacy-bounded usage episodes."""

from __future__ import annotations

from collections import Counter
from typing import Any

from usage_episode_feedback import (
    FRICTION_SIGNALS,
    classification_counts,
)

PRODUCT_EVIDENCE_NON_CLAIM = (
    "First-value refs are a minimum evidence floor, not satisfaction proof."
)

NON_DELIVERED_OUTCOMES = {"abandoned", "corrected", "escalated", "failed"}


def product_evidence(
    records: list[dict[str, Any]],
    feedback_records: list[dict[str, Any]] | None = None,
    *,
    feedback_coverage_count: int | None = None,
) -> dict[str, Any]:
    total = len(records)
    first_value_count = sum(
        1 for record in records if isinstance(record.get("first_value_ref"), dict)
    )
    feedback_records = feedback_records or [
        record for record in records if isinstance(record.get("feedback_signal"), str)
    ]
    classes = classification_counts(feedback_records)
    satisfaction_count = classes["satisfaction"]
    objective_lifecycle_count = classes["objective_lifecycle"]
    friction_targets = {
        (str(record.get("product_id")), str(record.get("target_episode_id", record.get("episode_id"))))
        for record in feedback_records
        if record.get("feedback_signal") in FRICTION_SIGNALS
    }
    friction_count = classes["friction"] + sum(
        1
        for record in records
        if record.get("outcome_status") in NON_DELIVERED_OUTCOMES
        and (str(record.get("product_id")), str(record.get("episode_id"))) not in friction_targets
    )
    coverage_count = len(feedback_records) if feedback_coverage_count is None else feedback_coverage_count
    missing_feedback_count = total - coverage_count
    return {
        "first_value_floor_count": first_value_count,
        "first_value_floor_rate": _rate(first_value_count, total),
        "first_value_kind": _nested_counter(records, "first_value_ref", "kind"),
        "feedback_coverage_count": coverage_count,
        "feedback_coverage_rate": _rate(coverage_count, total),
        "satisfaction_signal_count": satisfaction_count,
        "satisfaction_signal_rate": _rate(satisfaction_count, total),
        "objective_lifecycle_signal_count": objective_lifecycle_count,
        "objective_lifecycle_signal_rate": _rate(objective_lifecycle_count, total),
        "friction_or_followup_signal_count": friction_count,
        "friction_or_followup_signal_rate": _rate(friction_count, total),
        "missing_feedback_signal_count": missing_feedback_count,
        "neutral_feedback_signal_count": classes["neutral"],
        "unclassified_feedback_signal_count": classes["unclassified"],
        "veto_gaps": _veto_gaps(
            records=records,
            missing_feedback_count=missing_feedback_count,
            satisfaction_count=satisfaction_count,
            unclassified_feedback_count=classes["unclassified"],
        ),
    }


def _rate(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def _nested_counter(
    records: list[dict[str, Any]], object_field: str, field: str
) -> dict[str, int]:
    values: Counter[str] = Counter()
    for record in records:
        nested = record.get(object_field)
        if isinstance(nested, dict):
            values[str(nested.get(field, "<missing>"))] += 1
        else:
            values["<missing>"] += 1
    return dict(sorted(values.items()))


def _counter(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(record.get(field, "<missing>")) for record in records).items()))


def _emitter_key(record: dict[str, Any]) -> str:
    action = record.get("agent_action")
    if not isinstance(action, dict):
        return "<missing>"
    surface = str(action.get("surface", "<missing>"))
    capability = str(action.get("capability_ref", "<missing>"))
    return f"{surface}:{capability}"


def _veto_gaps(
    *,
    records: list[dict[str, Any]],
    missing_feedback_count: int,
    satisfaction_count: int,
    unclassified_feedback_count: int,
) -> list[str]:
    gaps: list[str] = []
    if missing_feedback_count:
        gaps.append("missing_feedback")
    if unclassified_feedback_count:
        gaps.append("unclassified_feedback")
    if records and satisfaction_count == 0:
        gaps.append("no_satisfaction_signal")
    if records:
        trigger_counts = _counter(records, "trigger_type")
        entry_point_counts = _counter(records, "entry_point")
        emitter_counts = Counter(_emitter_key(record) for record in records)
        if len(emitter_counts) == 1:
            gaps.append("single_emitter")
        if len(trigger_counts) == 1:
            gaps.append("single_trigger_type")
        if len(entry_point_counts) == 1:
            gaps.append("single_entry_point")
    return gaps
