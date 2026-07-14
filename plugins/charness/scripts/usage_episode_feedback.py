"""Shared privacy-safe feedback reconciliation for usage-episode records."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

FEEDBACK_SIGNALS = frozenset(
    {
        "accepted",
        "edited",
        "corrected",
        "ignored",
        "retried",
        "follow_up_requested",
        "human_confirmed",
        "closed_issue",
        "released",
    }
)
SATISFACTION_SIGNALS = frozenset({"accepted", "human_confirmed"})
OBJECTIVE_LIFECYCLE_SIGNALS = frozenset({"closed_issue", "released"})
FRICTION_SIGNALS = frozenset({"corrected", "ignored", "retried", "follow_up_requested"})
NEUTRAL_SIGNALS = frozenset({"edited"})
SOURCE_KINDS = frozenset({"operator", "issue_lifecycle", "release_lifecycle", "repository_state"})
SOURCE_SIGNALS = {
    "operator": FEEDBACK_SIGNALS,
    "issue_lifecycle": frozenset({"closed_issue"}),
    "release_lifecycle": frozenset({"released"}),
    "repository_state": frozenset({"edited", "corrected", "ignored", "retried", "follow_up_requested"}),
}


def signal_allowed_for_source(source_kind: str, feedback_signal: str) -> bool:
    return feedback_signal in SOURCE_SIGNALS.get(source_kind, frozenset())


def feedback_id_for(
    *,
    product_id: str,
    target_episode_id: str,
    feedback_signal: str,
    source_kind: str,
    evidence_ref: dict[str, str],
) -> str:
    """Return the stable idempotency key for a semantic feedback assertion."""
    semantic_fields = {
        "evidence_ref": evidence_ref,
        "feedback_signal": feedback_signal,
        "product_id": product_id,
        "source_kind": source_kind,
        "target_episode_id": target_episode_id,
    }
    serialized = json.dumps(semantic_fields, sort_keys=True, separators=(",", ":"))
    return f"feedback-{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"


def delivery_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if record.get("event_type") == "usage_episode"]


def feedback_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if record.get("event_type") == "usage_feedback"]


def _episode_target(record: dict[str, Any], episode_id_field: str) -> tuple[str, str]:
    return str(record["product_id"]), str(record[episode_id_field])


def delivery_target_index(records: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """Index deliveries by the product and episode target they can receive feedback for."""
    return {
        _episode_target(record, "episode_id"): record
        for record in delivery_records(records)
    }


def linked_delivery(
    targets: dict[tuple[str, str], dict[str, Any]], feedback: dict[str, Any]
) -> dict[str, Any] | None:
    return targets.get(_episode_target(feedback, "target_episode_id"))


def semantic_feedback_errors(records: list[dict[str, Any]]) -> list[str]:
    deliveries = delivery_target_index(records)
    seen: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for record in feedback_records(records):
        feedback_id = str(record["feedback_id"])
        expected_id = feedback_id_for(
            product_id=str(record["product_id"]),
            target_episode_id=str(record["target_episode_id"]),
            feedback_signal=str(record["feedback_signal"]),
            source_kind=str(record["source_kind"]),
            evidence_ref=dict(record["evidence_ref"]),
        )
        if feedback_id != expected_id:
            errors.append(f"non-deterministic feedback_id: {feedback_id}")
        prior = seen.get(feedback_id)
        if prior is not None:
            if prior == record:
                errors.append(f"duplicate feedback_id: {feedback_id}")
            else:
                errors.append(f"conflicting feedback_id: {feedback_id}")
        else:
            seen[feedback_id] = record
        if linked_delivery(deliveries, record) is None:
            errors.append(
                "unlinked target_episode_id: "
                f"{record['target_episode_id']} for product_id {record['product_id']}"
            )
    return errors


def reconcile_feedback(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Join explicit and legacy-inline feedback to delivery records without claims."""
    deliveries = delivery_records(records)
    targets = delivery_target_index(records)
    explicit = feedback_records(records)
    seen: set[str] = set()
    duplicate_count = 0
    linked: list[dict[str, Any]] = []
    enriched_linked: list[dict[str, Any]] = []
    unlinked_count = 0
    for record in explicit:
        feedback_id = str(record["feedback_id"])
        if feedback_id in seen:
            duplicate_count += 1
        seen.add(feedback_id)
        delivery = linked_delivery(targets, record)
        if delivery is not None:
            linked.append(record)
            # Explicit feedback has no delivery dimensions of its own.  Carry
            # its signal onto the delivery it observes so downstream summaries
            # retain delivery-only denominators and evidence references.
            enriched_linked.append(
                {
                    **delivery,
                    "feedback_signal": record["feedback_signal"],
                }
            )
        else:
            unlinked_count += 1

    inline = [record for record in deliveries if isinstance(record.get("feedback_signal"), str)]
    signal_records = [*inline, *enriched_linked]
    covered_targets = {
        (str(record["product_id"]), str(record["episode_id"])) for record in inline
    }
    covered_targets.update(
        (str(record["product_id"]), str(record["target_episode_id"])) for record in linked
    )
    signal_counts = Counter(str(record["feedback_signal"]) for record in signal_records)
    return {
        "delivery_episode_count": len(deliveries),
        "feedback_event_count": len(explicit),
        "linked_feedback_count": len(linked),
        "unlinked_feedback_count": unlinked_count,
        "duplicate_feedback_id_count": duplicate_count,
        "inline_feedback_count": len(inline),
        "feedback_coverage_count": len(covered_targets),
        "feedback_coverage_rate": _rate(len(covered_targets), len(deliveries)),
        "feedback_signal_counts": dict(sorted(signal_counts.items())),
        "signal_records": signal_records,
    }


def classification_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    values = Counter(str(record.get("feedback_signal")) for record in records)
    return {
        "satisfaction": sum(values[signal] for signal in SATISFACTION_SIGNALS),
        "objective_lifecycle": sum(values[signal] for signal in OBJECTIVE_LIFECYCLE_SIGNALS),
        "friction": sum(values[signal] for signal in FRICTION_SIGNALS),
        "neutral": sum(values[signal] for signal in NEUTRAL_SIGNALS),
        "unclassified": sum(
            count
            for signal, count in values.items()
            if signal
            not in SATISFACTION_SIGNALS
            | OBJECTIVE_LIFECYCLE_SIGNALS
            | FRICTION_SIGNALS
            | NEUTRAL_SIGNALS
        ),
    }


def _rate(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0
