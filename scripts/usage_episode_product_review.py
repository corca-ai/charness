"""Corca-internal product-review summaries for usage episodes."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from typing import Any

from report_usage_episodes import NON_CLAIMS as USAGE_REPORT_NON_CLAIMS
from report_usage_episodes import _parse_timestamp
from usage_episode_feedback import delivery_records, feedback_records, reconcile_feedback
from usage_episode_product_evidence import FRICTION_SIGNALS, NON_DELIVERED_OUTCOMES, _counter

REVIEW_NON_CLAIMS = [
    "Last-seen fields are review inputs, not churn or stop-using classifiers.",
    "Update prompt state is distribution context, not satisfaction proof.",
    "The reporter packet does not prove satisfaction, dissatisfaction, root cause, or a fix.",
    "The reporter does not include raw prompts, transcripts, private source bodies, or personal content.",
]
TRIAGE_QUESTIONS = [
    "Is the observed signal expected for this repo and review window?",
    "Does a human need to follow up with the referenced Corca-internal contact or repo owner?",
    "Is the evidence strong enough to link to an existing product-success, friction, or missed-detection issue?",
]


def parse_optional_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return _parse_timestamp(value)


def build_review_payload(
    records: list[dict[str, Any]],
    *,
    window_start: datetime | None,
    window_end: datetime | None,
    release_version: str,
    update_prompt_state: str,
    corca_internal: bool,
    repo_ref: str | None,
    user_ref: str | None,
    friction_threshold: int | None,
    missed_detection_threshold: int | None,
    execute: bool,
) -> dict[str, Any]:
    deliveries = delivery_records(records)
    window_records = _filter_window(deliveries, window_start=window_start, window_end=window_end)
    window_feedback = _filter_window(
        feedback_records(records),
        window_start=window_start,
        window_end=window_end,
    )
    window_targets = {
        (str(record["product_id"]), str(record["episode_id"]))
        for record in window_records
    }
    # A linked feedback assertion belongs in a review only when both its own
    # observation time and its target delivery are in the requested window.
    feedback = reconcile_feedback([*window_records, *window_feedback])
    window_signals = [
        record
        for record in feedback["signal_records"]
        if (str(record["product_id"]), str(record["episode_id"])) in window_targets
    ]
    summary = _review_summary(
        window_records,
        signal_records=window_signals,
        window_start=window_start,
        window_end=window_end,
        release_version=release_version,
        update_prompt_state=update_prompt_state,
        corca_internal=corca_internal,
        repo_ref=repo_ref,
        user_ref=user_ref,
    )
    filing_mode = "execute_ready" if execute else "dry_run"
    packets = [
        _packet(
            signal_type="usage_observed" if window_records else "no_usage_observed",
            packet_type="review_summary",
            filing_mode="report_only",
            records=window_records,
            summary=summary,
        )
    ]
    friction = _friction_records(window_records, window_signals)
    if friction_threshold is not None and len(friction) >= friction_threshold:
        packets.append(
            _packet(
                signal_type="friction_threshold",
                packet_type="issue_comment",
                filing_mode=filing_mode,
                records=friction,
                summary=summary,
                threshold={
                    "metric": "friction_or_followup_count",
                    "observed_count": len(friction),
                    "threshold": friction_threshold,
                },
            )
        )
    missed = _missed_detection_records(friction)
    if missed_detection_threshold is not None and len(missed) >= missed_detection_threshold:
        packets.append(
            _packet(
                signal_type="missed_detection_candidate",
                packet_type="issue_comment",
                filing_mode=filing_mode,
                records=missed,
                summary=summary,
                threshold={
                    "metric": "missed_detection_candidate_count",
                    "observed_count": len(missed),
                    "threshold": missed_detection_threshold,
                },
            )
        )
    return {
        "status": "valid",
        "valid": True,
        "review_summary": summary,
        "reporter_packets": packets,
        "actionable_packet_count": _actionable_count(packets),
        "dry_run": not execute,
        "executed": False,
        "non_claims": [*USAGE_REPORT_NON_CLAIMS, *REVIEW_NON_CLAIMS],
        "errors": [],
        "warnings": [],
    }


def execute_comments(
    payload: dict[str, Any],
    *,
    gh_bin: str,
    github_repo: str,
    issue_number: int,
    include_target_refs: bool = False,
) -> int:
    actionable = [
        packet
        for packet in payload["reporter_packets"]
        if packet["packet_type"] == "issue_comment"
    ]
    if not actionable:
        payload["status"] = "no_actionable_packets"
        payload["valid"] = False
        payload["errors"].append("execute requested but no thresholded friction or missed-detection packet crossed")
        return 2
    for packet in actionable:
        packet["filing_mode"] = "executed"
        packet["comment_body"] = _packet_body(
            packet,
            payload["review_summary"],
            include_target_refs=include_target_refs,
        )
    comment_body = "\n\n".join(packet["comment_body"] for packet in actionable)
    try:
        result = subprocess.run(
            [
                gh_bin,
                "issue",
                "comment",
                str(issue_number),
                "--repo",
                github_repo,
                "--body",
                comment_body,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        payload["status"] = "gh_unavailable"
        payload["valid"] = False
        payload["errors"].append(str(exc))
        return 127
    if result.returncode != 0:
        payload["status"] = "github_comment_failed"
        payload["valid"] = False
        payload["errors"].append(result.stderr.strip() or result.stdout.strip() or "gh issue comment failed")
        return result.returncode or 1
    payload["executed"] = True
    payload["dry_run"] = False
    payload["github_target"] = {
        "repo": github_repo,
        "issue_number": issue_number,
        "comment_count": 1,
        "packet_count": len(actionable),
        "target_refs_included": include_target_refs,
    }
    return 0


# `print_review_result` lived here until the YAML migration. It was a
# format switch (`--json` payload vs a human rendering) around a payload its only
# caller already holds, so with the flag gone `report_usage_product_review.py`
# emits that payload directly through `emit_yaml`. Nothing the human rendering
# stated was lost: the ADVISORY line is a `non_claims` entry, the review window
# and signal counts are `review_summary` / `actionable_packet_count`, the
# unavailable-report branch is `status` plus `errors`, and each packet's rendered
# text is `reporter_packets[].body`.


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _filter_window(
    records: list[dict[str, Any]],
    *,
    window_start: datetime | None,
    window_end: datetime | None,
) -> list[dict[str, Any]]:
    filtered = []
    for record in records:
        timestamp = _parse_timestamp(record["timestamp"])
        if window_start is not None and timestamp < window_start:
            continue
        if window_end is not None and timestamp > window_end:
            continue
        filtered.append(record)
    return filtered


def _safe_ref(record: dict[str, Any]) -> str:
    first_value = record.get("first_value_ref")
    if isinstance(first_value, dict):
        if first_value.get("path"):
            return str(first_value["path"])
        if first_value.get("ref"):
            return str(first_value["ref"])
    context = record.get("context_ref")
    if isinstance(context, dict) and context.get("ref"):
        return str(context["ref"])
    return str(record.get("episode_id", "<missing-episode-id>"))


def _evidence_refs(records: list[dict[str, Any]], *, limit: int = 8) -> list[dict[str, str]]:
    refs = []
    for record in sorted(records, key=lambda item: item["timestamp"])[:limit]:
        refs.append(
            {
                "timestamp": record["timestamp"],
                "episode_id": str(record.get("episode_id", "<missing>")),
                "ref": _safe_ref(record),
            }
        )
    return refs


def _friction_records(
    deliveries: list[dict[str, Any]],
    signal_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    friction_targets = {
        (str(record["product_id"]), str(record["episode_id"]))
        for record in signal_records
        if record.get("feedback_signal") in FRICTION_SIGNALS
    }
    return [
        record
        for record in deliveries
        if (str(record["product_id"]), str(record["episode_id"])) in friction_targets
        or record.get("outcome_status") in NON_DELIVERED_OUTCOMES
    ]


def _missed_detection_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if record.get("classification_skipped") or record.get("t_status") == "none"
    ]


def _review_summary(
    records: list[dict[str, Any]],
    *,
    signal_records: list[dict[str, Any]],
    window_start: datetime | None,
    window_end: datetime | None,
    release_version: str,
    update_prompt_state: str,
    corca_internal: bool,
    repo_ref: str | None,
    user_ref: str | None,
) -> dict[str, Any]:
    timestamps = [_parse_timestamp(record["timestamp"]) for record in records]
    friction = _friction_records(records, signal_records)
    return {
        "scope": "corca_internal" if corca_internal else "privacy_safe",
        "window_start": _iso(window_start) if window_start else None,
        "window_end": _iso(window_end) if window_end else None,
        "release_version": release_version,
        "update_context": {
            "update_prompt_state": update_prompt_state,
            "non_claim": "Update prompt state is not satisfaction evidence.",
        },
        "target_refs": {
            "repo_ref": repo_ref,
            "user_ref": user_ref if corca_internal else None,
        },
        "usage_count": len(records),
        "first_seen_at": _iso(min(timestamps)) if timestamps else None,
        "last_seen_at": _iso(max(timestamps)) if timestamps else None,
        "product_counts": _counter(records, "product_id"),
        "entry_point_counts": _counter(records, "entry_point"),
        "trigger_type_counts": _counter(records, "trigger_type"),
        "outcome_status_counts": _counter(records, "outcome_status"),
        "feedback_signal_counts": _counter(signal_records, "feedback_signal"),
        "feedback_coverage_count": len(
            {
                (str(record["product_id"]), str(record["episode_id"]))
                for record in signal_records
            }
        ),
        "friction_or_followup_count": len(friction),
        "missed_detection_candidate_count": len(_missed_detection_records(friction)),
    }


def _packet(
    *,
    signal_type: str,
    packet_type: str,
    filing_mode: str,
    records: list[dict[str, Any]],
    summary: dict[str, Any],
    threshold: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = {
        "signal_type": signal_type,
        "packet_type": packet_type,
        "filing_mode": filing_mode,
        "threshold": threshold,
        "evidence_refs": _evidence_refs(records),
        "confidence_gaps": _confidence_gaps(records, summary),
        "non_claims": REVIEW_NON_CLAIMS,
        "triage_questions": TRIAGE_QUESTIONS,
    }
    packet["body"] = _packet_body(packet, summary)
    return packet


def _packet_body(
    packet: dict[str, Any],
    summary: dict[str, Any],
    *,
    include_target_refs: bool = True,
) -> str:
    threshold = packet.get("threshold") or {}
    threshold_text = "none"
    if threshold:
        threshold_text = (
            f"{threshold['metric']}={threshold['observed_count']} "
            f">= {threshold['threshold']}"
        )
    refs = packet.get("evidence_refs", [])
    evidence_lines = "\n".join(
        f"- {ref['timestamp']} `{ref['episode_id']}` {ref['ref']}" for ref in refs
    ) or "- none"
    target_refs = summary["target_refs"]
    if include_target_refs:
        target = ", ".join(
            f"{key}={value}" for key, value in target_refs.items() if value
        ) or "none"
    else:
        target = "redacted for mutating GitHub comment"
    return "\n".join(
        [
            "## Charness Usage Product-Review Packet",
            "",
            f"- signal_type: `{packet['signal_type']}`",
            f"- packet_type: `{packet['packet_type']}`",
            f"- filing_mode: `{packet['filing_mode']}`",
            f"- release_version: `{summary['release_version']}`",
            f"- target_refs: {target}",
            f"- first_seen_at: `{summary['first_seen_at']}`",
            f"- last_seen_at: `{summary['last_seen_at']}`",
            f"- usage_count: `{summary['usage_count']}`",
            f"- update_prompt_state: `{summary['update_context']['update_prompt_state']}`",
            f"- threshold: {threshold_text}",
            "",
            "### Evidence Refs",
            evidence_lines,
            "",
            "### Known Gaps And Non-Claims",
            "\n".join(f"- {item}" for item in REVIEW_NON_CLAIMS),
            "",
            "### Triage Questions",
            "\n".join(f"- {item}" for item in TRIAGE_QUESTIONS),
        ]
    )


def _confidence_gaps(records: list[dict[str, Any]], summary: dict[str, Any]) -> list[str]:
    gaps = []
    if not records:
        gaps.append("no_usage_records_in_window")
    if not summary["target_refs"].get("repo_ref"):
        gaps.append("repo_ref_not_provided")
    if summary["scope"] == "corca_internal" and not summary["target_refs"].get("user_ref"):
        gaps.append("corca_internal_user_ref_not_provided")
    if summary["feedback_coverage_count"] < summary["usage_count"]:
        gaps.append("missing_feedback_signal")
    return gaps


def _actionable_count(packets: list[dict[str, Any]]) -> int:
    return sum(1 for packet in packets if packet["packet_type"] == "issue_comment")
