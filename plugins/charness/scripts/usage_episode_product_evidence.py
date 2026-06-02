"""Product-evidence summaries for privacy-bounded usage episodes."""

from __future__ import annotations

from collections import Counter
from typing import Any

PRODUCT_EVIDENCE_NON_CLAIM = (
    "First-value refs are a minimum evidence floor, not satisfaction proof."
)

SATISFACTION_SIGNALS = {"accepted", "human_confirmed", "closed_issue", "released"}
FRICTION_SIGNALS = {"corrected", "retried", "ignored", "follow_up_requested"}
NON_DELIVERED_OUTCOMES = {"abandoned", "corrected", "escalated", "failed"}


def product_evidence(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    first_value_count = sum(
        1 for record in records if isinstance(record.get("first_value_ref"), dict)
    )
    feedback_records = [
        record for record in records if isinstance(record.get("feedback_signal"), str)
    ]
    satisfaction_count = sum(
        1
        for record in feedback_records
        if record["feedback_signal"] in SATISFACTION_SIGNALS
    )
    friction_count = sum(
        1
        for record in records
        if record.get("feedback_signal") in FRICTION_SIGNALS
        or record.get("outcome_status") in NON_DELIVERED_OUTCOMES
    )
    missing_feedback_count = total - len(feedback_records)
    return {
        "first_value_floor_count": first_value_count,
        "first_value_floor_rate": _rate(first_value_count, total),
        "first_value_kind": _nested_counter(records, "first_value_ref", "kind"),
        "feedback_coverage_count": len(feedback_records),
        "feedback_coverage_rate": _rate(len(feedback_records), total),
        "satisfaction_signal_count": satisfaction_count,
        "satisfaction_signal_rate": _rate(satisfaction_count, total),
        "friction_or_followup_signal_count": friction_count,
        "friction_or_followup_signal_rate": _rate(friction_count, total),
        "missing_feedback_signal_count": missing_feedback_count,
        "unclassified_feedback_signal_count": _unclassified_feedback_count(
            feedback_records
        ),
        "veto_gaps": _veto_gaps(
            records=records,
            missing_feedback_count=missing_feedback_count,
            satisfaction_count=satisfaction_count,
            unclassified_feedback_count=_unclassified_feedback_count(
                feedback_records
            ),
        ),
    }


def _rate(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def _counter(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(record.get(field, "<missing>")) for record in records).items()))


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


def _unclassified_feedback_count(records: list[dict[str, Any]]) -> int:
    classified = SATISFACTION_SIGNALS | FRICTION_SIGNALS
    return sum(1 for record in records if record.get("feedback_signal") not in classified)


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
