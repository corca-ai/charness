#!/usr/bin/env python3
"""Summarize privacy-bounded Charness usage episode JSONL records."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from usage_episode_feedback import delivery_records, reconcile_feedback
from usage_episode_product_evidence import (
    PRODUCT_EVIDENCE_NON_CLAIM,
    _counter,
    _nested_counter,
    product_evidence,
)
from usage_episode_records import parse_timestamp as _parse_timestamp
from usage_episode_records import read_valid_records as _read_valid_records
from usage_episode_records import resolve_records_path as _resolve_records_path
from usage_episode_records import schema_root as _schema_root

from yaml_output import emit_yaml

DEFAULT_ADAPTER = Path(".agents/usage-episodes-adapter.yaml")
# The heading the deleted prose renderer printed above the list. It stays in the
# payload because it is what marks the list as NON-claims rather than findings: a
# summary that shows the sentences without it reads them as things the report is
# asserting, which inverts them.
NON_CLAIMS_LABEL = "Non-claims:"
NON_CLAIMS = [
    "Usage episodes are an engineering usage signal, not product-success proof.",
    PRODUCT_EVIDENCE_NON_CLAIM,
    "Objective issue/release lifecycle signals are not human approval or general satisfaction evidence.",
    "Counts cover only records captured under the configured storage_path; missing hooks or disabled adapters are outside the denominator.",
    "The report does not infer raw prompts, transcripts, user identity, or private source content.",
]


def _warning(warning_id: str, message: str, next_action: str) -> dict[str, str]:
    return {
        "warning_id": warning_id,
        "message": message,
        "next_action": next_action,
        # The rendered attention line, carried INSIDE the payload. The `WARNING:`
        # prefix existed only in the deleted prose renderer, and a warning that
        # reads as an ordinary field is an attention state gone quiet -- the exact
        # failure `skills/public/quality/references/attention-state-visibility.json`
        # declares this file against.
        "attention": f"WARNING: {message} Next action: {next_action}",
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_adapter(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: adapter must be a mapping")
    return data


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _date_counter(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        counts[_parse_timestamp(record["timestamp"]).date().isoformat()] += 1
    return dict(sorted(counts.items()))


def _session_record(
    session_key: str,
    session_type: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    timestamps = [_parse_timestamp(record["timestamp"]) for record in records]
    return {
        "session_key": session_key,
        "session_type": session_type,
        "episode_count": len(records),
        "first_timestamp": min(timestamps).isoformat().replace("+00:00", "Z"),
        "last_timestamp": max(timestamps).isoformat().replace("+00:00", "Z"),
        "t_status_counts": _counter(records, "t_status"),
        "selected_job_counts": _counter(records, "selected_job"),
        "outcome_status_counts": _counter(records, "outcome_status"),
    }


def _cluster_sessions(records: list[dict[str, Any]], gap: timedelta) -> list[dict[str, Any]]:
    explicit: dict[str, list[dict[str, Any]]] = {}
    ungrouped = []
    for record in records:
        session_id = record.get("session_id")
        if isinstance(session_id, str) and session_id:
            explicit.setdefault(session_id, []).append(record)
        else:
            ungrouped.append(record)

    sessions = [
        _session_record(f"session:{session_id}", "explicit", items)
        for session_id, items in sorted(explicit.items())
    ]
    sorted_ungrouped = sorted(ungrouped, key=lambda item: _parse_timestamp(item["timestamp"]))
    cluster: list[dict[str, Any]] = []
    last_timestamp: datetime | None = None
    cluster_index = 0
    for record in sorted_ungrouped:
        timestamp = _parse_timestamp(record["timestamp"])
        if cluster and last_timestamp is not None and timestamp - last_timestamp > gap:
            cluster_index += 1
            sessions.append(_session_record(f"inferred-gap:{cluster_index}", "inferred_gap", cluster))
            cluster = []
        cluster.append(record)
        last_timestamp = timestamp
    if cluster:
        cluster_index += 1
        sessions.append(_session_record(f"inferred-gap:{cluster_index}", "inferred_gap", cluster))
    return sorted(sessions, key=lambda item: item["first_timestamp"])


def _capture_gaps(
    records: list[dict[str, Any]],
    sessions: list[dict[str, Any]],
    *,
    feedback_coverage_count: int,
) -> dict[str, Any]:
    ungrouped_count = sum(1 for record in records if not record.get("session_id"))
    t_signal_records = [record for record in records if record.get("t_status") != "none"]
    missing_t_evidence = sum(1 for record in t_signal_records if "t_evidence" not in record)
    trigger_counts = _counter(records, "trigger_type")
    entry_point_counts = _counter(records, "entry_point")
    return {
        "ungrouped_episode_count": ungrouped_count,
        "inferred_gap_session_count": sum(1 for session in sessions if session["session_type"] == "inferred_gap"),
        "missing_feedback_signal_count": len(records) - feedback_coverage_count,
        "t_signal_without_evidence_count": missing_t_evidence,
        "single_entry_point_only": len(entry_point_counts) == 1 and bool(records),
        "explicit_request_only": set(trigger_counts) == {"explicit_request"},
    }


def _report_payload(
    repo_root: Path,
    adapter_path: Path,
    records_path: Path,
    records: list[dict[str, Any]],
    *,
    gap_minutes: int,
    session_limit: int,
) -> dict[str, Any]:
    deliveries = delivery_records(records)
    feedback = reconcile_feedback(records)
    sessions = _cluster_sessions(deliveries, timedelta(minutes=gap_minutes))
    session_id_present_count = sum(1 for record in deliveries if record.get("session_id"))
    t_signal_count = sum(1 for record in deliveries if record.get("t_status") != "none")
    visible_sessions = sessions[:session_limit]
    return {
        "status": "valid",
        "valid": True,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "records_path": _portable_path(repo_root, records_path),
        "episode_count": len(deliveries),
        "delivery_episode_count": len(deliveries),
        "feedback_event_count": feedback["feedback_event_count"],
        "feedback_reconciliation": {
            "linked_count": feedback["linked_feedback_count"],
            "unlinked_count": feedback["unlinked_feedback_count"],
            "duplicate_feedback_id_count": feedback["duplicate_feedback_id_count"],
            "inline_feedback_count": feedback["inline_feedback_count"],
        },
        "session_count": len(sessions),
        "session_limit": session_limit,
        "sessions_truncated": max(0, len(sessions) - len(visible_sessions)),
        "sessions": {
            "gap_minutes": gap_minutes,
            "explicit_count": sum(1 for session in sessions if session["session_type"] == "explicit"),
            "inferred_gap_count": sum(1 for session in sessions if session["session_type"] == "inferred_gap"),
            "session_id_present_count": session_id_present_count,
            "session_grouping_rate": round(session_id_present_count / len(deliveries), 4) if deliveries else 0.0,
            "items": visible_sessions,
        },
        "counts": {
            "daily": _date_counter(deliveries),
            "selected_job": _counter(deliveries, "selected_job"),
            "core_action": _counter(deliveries, "core_action"),
            "entry_point": _counter(deliveries, "entry_point"),
            "trigger_type": _counter(deliveries, "trigger_type"),
            "outcome_status": _counter(deliveries, "outcome_status"),
            "feedback_signal": feedback["feedback_signal_counts"],
            "t_status": _counter(deliveries, "t_status"),
            "agent_surface": _nested_counter(deliveries, "agent_action", "surface"),
            "agent_capability_ref": _nested_counter(deliveries, "agent_action", "capability_ref"),
        },
        "t_signal_count": t_signal_count,
        "t_signal_rate": round(t_signal_count / len(deliveries), 4) if deliveries else 0.0,
        "capture_gaps": _capture_gaps(deliveries, sessions, feedback_coverage_count=feedback["feedback_coverage_count"]),
        "product_evidence": product_evidence(
            deliveries,
            feedback["signal_records"],
            feedback_coverage_count=feedback["feedback_coverage_count"],
        ),
        "warnings": [],
        "errors": [],
        "non_claims_label": NON_CLAIMS_LABEL,
        "non_claims": NON_CLAIMS,
    }


def _base_payload(
    status: str,
    repo_root: Path,
    adapter_path: Path,
    *,
    records_path: Path | None = None,
    valid: bool = True,
    errors: list[str] | None = None,
    warnings: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "valid": valid,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "episode_count": 0,
        "session_count": 0,
        "errors": errors or [],
        "warnings": warnings or [],
        "non_claims_label": NON_CLAIMS_LABEL,
        "non_claims": NON_CLAIMS,
    }
    if records_path is not None:
        payload["records_path"] = _portable_path(repo_root, records_path)
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--records-path", type=Path)
    parser.add_argument("--gap-minutes", type=int, default=90)
    parser.add_argument("--session-limit", type=int, default=10)
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.gap_minutes <= 0:
        raise SystemExit("--gap-minutes must be positive")
    if args.session_limit <= 0:
        raise SystemExit("--session-limit must be positive")


def _missing_adapter_payload(repo_root: Path, adapter_path: Path) -> dict[str, Any]:
    return _base_payload(
        "no_adapter",
        repo_root,
        adapter_path,
        warnings=[
            _warning(
                "usage_episodes_adapter_missing",
                f"no usage-episodes adapter found at {_portable_path(repo_root, adapter_path)}; report skipped",
                "Run setup seeding if this repo should opt into usage episode reporting, or record the opt-out in quality closeout.",
            )
        ],
    )


def _disabled_payload(repo_root: Path, adapter_path: Path) -> dict[str, Any]:
    return _base_payload(
        "disabled",
        repo_root,
        adapter_path,
        warnings=[
            _warning(
                "usage_episodes_adapter_disabled",
                f"usage-episodes adapter at {_portable_path(repo_root, adapter_path)} is disabled; report skipped",
                "Enable the adapter before relying on usage episode summaries; keep disabled state visible in quality closeout.",
            )
        ],
    )


def _no_records_payload(repo_root: Path, adapter_path: Path, records_path: Path) -> dict[str, Any]:
    return _base_payload(
        "no_records",
        repo_root,
        adapter_path,
        records_path=records_path,
        warnings=[
            _warning(
                "usage_episodes_no_records",
                f"usage-episodes adapter at {_portable_path(repo_root, adapter_path)} is enabled but no records file exists yet at {_portable_path(repo_root, records_path)}",
                "Capture is opt-in; the report will populate after the first emitted episode. Disable the adapter if no capture is expected.",
            )
        ],
    )


def main() -> int:
    args = _parse_args()
    _validate_args(args)
    repo_root = args.repo_root.resolve()
    adapter_path = args.adapter_path or repo_root / DEFAULT_ADAPTER
    if not adapter_path.is_absolute():
        adapter_path = repo_root / adapter_path
    schema_root = _schema_root(repo_root)
    manifest_schema = _load_json(schema_root / "manifest.schema.json")
    episode_schema = _load_json(schema_root / "episode.schema.json")

    if not adapter_path.is_file():
        emit_yaml(_missing_adapter_payload(repo_root, adapter_path))
        return 0

    try:
        adapter = _load_adapter(adapter_path)
        jsonschema.validate(adapter, manifest_schema)
    except (OSError, ValueError, yaml.YAMLError, jsonschema.ValidationError) as exc:
        payload = _base_payload("invalid_adapter", repo_root, adapter_path, valid=False, errors=[str(exc)])
        emit_yaml(payload)
        return 1

    if not adapter.get("enabled", False):
        emit_yaml(_disabled_payload(repo_root, adapter_path))
        return 0

    records_path = _resolve_records_path(repo_root, adapter, args.records_path)
    try:
        records_path.relative_to(repo_root)
    except ValueError:
        payload = _base_payload(
            "invalid_records_path",
            repo_root,
            adapter_path,
            records_path=records_path,
            valid=False,
            errors=["records_path must stay under repo_root"],
        )
        emit_yaml(payload)
        return 1
    if not records_path.is_file():
        emit_yaml(_no_records_payload(repo_root, adapter_path, records_path))
        return 0

    records, errors = _read_valid_records(records_path, episode_schema)
    if errors:
        payload = _base_payload(
            "invalid_records",
            repo_root,
            adapter_path,
            records_path=records_path,
            valid=False,
            errors=errors,
        )
        payload["valid_count"] = len(records)
        emit_yaml(payload)
        return 1

    payload = _report_payload(repo_root, adapter_path, records_path, records, gap_minutes=args.gap_minutes, session_limit=args.session_limit)
    emit_yaml(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
