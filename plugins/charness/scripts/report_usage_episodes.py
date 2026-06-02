#!/usr/bin/env python3
"""Summarize privacy-bounded Charness usage episode JSONL records."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from usage_episode_product_evidence import PRODUCT_EVIDENCE_NON_CLAIM, product_evidence

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_ADAPTER = Path(".agents/usage-episodes-adapter.yaml")
DEFAULT_STORAGE = Path(".charness/usage-episodes")
EVENT_FILENAME = "usage_episode.jsonl"
NON_CLAIMS = [
    "Usage episodes are an engineering usage signal, not product-success proof.",
    PRODUCT_EVIDENCE_NON_CLAIM,
    "Counts cover only records captured under the configured storage_path; missing hooks or disabled adapters are outside the denominator.",
    "The report does not infer raw prompts, transcripts, user identity, or private source content.",
]


def _warning(warning_id: str, message: str, next_action: str) -> dict[str, str]:
    return {
        "warning_id": warning_id,
        "message": message,
        "next_action": next_action,
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_root(repo_root: Path) -> Path:
    candidate = repo_root / "integrations" / "usage-episodes"
    if (candidate / "manifest.schema.json").is_file() and (candidate / "episode.schema.json").is_file():
        return candidate
    return REPO_ROOT / "integrations" / "usage-episodes"


def _load_adapter(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: adapter must be a mapping")
    return data


def _storage_dir(repo_root: Path, adapter: dict[str, Any]) -> Path:
    raw = adapter.get("storage_path")
    if isinstance(raw, str) and raw:
        return repo_root / raw
    return repo_root / DEFAULT_STORAGE


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _resolve_records_path(repo_root: Path, adapter: dict[str, Any], explicit: Path | None) -> Path:
    if explicit is None:
        return (_storage_dir(repo_root, adapter) / EVENT_FILENAME).resolve()
    candidate = explicit if explicit.is_absolute() else repo_root / explicit
    return candidate.resolve()


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _read_valid_records(path: Path, episode_schema: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    validator = jsonschema.Draft7Validator(episode_schema, format_checker=jsonschema.FormatChecker())
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
            continue
        try:
            validator.validate(row)
        except jsonschema.ValidationError as exc:
            path_text = ".".join(str(part) for part in exc.absolute_path)
            suffix = f" at {path_text}" if path_text else ""
            errors.append(f"{path}:{line_number}: schema error{suffix}: {exc.message}")
            continue
        try:
            _parse_timestamp(row["timestamp"])
        except ValueError:
            errors.append(f"{path}:{line_number}: schema error at timestamp: {row['timestamp']!r} is not date-time")
            continue
        records.append(row)
    return records, errors


def _counter(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(record.get(field, "<missing>")) for record in records).items()))


def _nested_counter(records: list[dict[str, Any]], object_field: str, field: str) -> dict[str, int]:
    values: Counter[str] = Counter()
    for record in records:
        nested = record.get(object_field)
        if isinstance(nested, dict):
            values[str(nested.get(field, "<missing>"))] += 1
        else:
            values["<missing>"] += 1
    return dict(sorted(values.items()))


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


def _capture_gaps(records: list[dict[str, Any]], sessions: list[dict[str, Any]]) -> dict[str, Any]:
    ungrouped_count = sum(1 for record in records if not record.get("session_id"))
    t_signal_records = [record for record in records if record.get("t_status") != "none"]
    missing_t_evidence = sum(1 for record in t_signal_records if "t_evidence" not in record)
    trigger_counts = _counter(records, "trigger_type")
    entry_point_counts = _counter(records, "entry_point")
    return {
        "ungrouped_episode_count": ungrouped_count,
        "inferred_gap_session_count": sum(1 for session in sessions if session["session_type"] == "inferred_gap"),
        "missing_feedback_signal_count": sum(1 for record in records if "feedback_signal" not in record),
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
    sessions = _cluster_sessions(records, timedelta(minutes=gap_minutes))
    session_id_present_count = sum(1 for record in records if record.get("session_id"))
    t_signal_count = sum(1 for record in records if record.get("t_status") != "none")
    visible_sessions = sessions[:session_limit]
    return {
        "status": "valid",
        "valid": True,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "records_path": _portable_path(repo_root, records_path),
        "episode_count": len(records),
        "session_count": len(sessions),
        "session_limit": session_limit,
        "sessions_truncated": max(0, len(sessions) - len(visible_sessions)),
        "sessions": {
            "gap_minutes": gap_minutes,
            "explicit_count": sum(1 for session in sessions if session["session_type"] == "explicit"),
            "inferred_gap_count": sum(1 for session in sessions if session["session_type"] == "inferred_gap"),
            "session_id_present_count": session_id_present_count,
            "session_grouping_rate": round(session_id_present_count / len(records), 4) if records else 0.0,
            "items": visible_sessions,
        },
        "counts": {
            "daily": _date_counter(records),
            "selected_job": _counter(records, "selected_job"),
            "core_action": _counter(records, "core_action"),
            "entry_point": _counter(records, "entry_point"),
            "trigger_type": _counter(records, "trigger_type"),
            "outcome_status": _counter(records, "outcome_status"),
            "feedback_signal": _counter(records, "feedback_signal"),
            "t_status": _counter(records, "t_status"),
            "agent_surface": _nested_counter(records, "agent_action", "surface"),
            "agent_capability_ref": _nested_counter(records, "agent_action", "capability_ref"),
        },
        "t_signal_count": t_signal_count,
        "t_signal_rate": round(t_signal_count / len(records), 4) if records else 0.0,
        "capture_gaps": _capture_gaps(records, sessions),
        "product_evidence": product_evidence(records),
        "warnings": [],
        "errors": [],
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
        "non_claims": NON_CLAIMS,
    }
    if records_path is not None:
        payload["records_path"] = _portable_path(repo_root, records_path)
    return payload


def _print_result(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print("ADVISORY: usage episode report is an engineering signal, not product-success proof.")
    for warning in payload.get("warnings", []):
        print(f"WARNING: {warning['message']} Next action: {warning['next_action']}")
    status = payload["status"]
    if status != "valid":
        print(f"{status}: {payload.get('episode_count', 0)} usage episode record(s)")
        for error in payload.get("errors", []):
            print(f"- {error}")
    else:
        print(
            f"Usage episodes: {payload['episode_count']} record(s) across "
            f"{payload['session_count']} session group(s)."
        )
        sessions = payload["sessions"]
        print(
            "Session grouping: "
            f"{sessions['session_id_present_count']}/{payload['episode_count']} records "
            f"carry session_id; inferred gap sessions: {sessions['inferred_gap_count']}."
        )
        print(f"T signals: {payload['t_signal_count']} ({payload['t_signal_rate']:.1%}).")
        evidence = payload["product_evidence"]
        print(
            "Product evidence: "
            f"first_value_floor={evidence['first_value_floor_count']}/{payload['episode_count']} "
            f"({evidence['first_value_floor_rate']:.1%}), "
            f"feedback_coverage={evidence['feedback_coverage_rate']:.1%}, "
            f"satisfaction_signals={evidence['satisfaction_signal_count']}, "
            f"friction_or_followup={evidence['friction_or_followup_signal_count']}."
        )
        gaps = payload["capture_gaps"]
        print(
            "Capture gaps: "
            f"ungrouped={gaps['ungrouped_episode_count']}, "
            f"missing_feedback={gaps['missing_feedback_signal_count']}, "
            f"single_entry_point_only={gaps['single_entry_point_only']}, "
            f"explicit_request_only={gaps['explicit_request_only']}."
        )
        if evidence["veto_gaps"]:
            print("Product-success veto gaps: " + ", ".join(evidence["veto_gaps"]) + ".")
    print("Non-claims:")
    for non_claim in payload.get("non_claims", []):
        print(f"- {non_claim}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--records-path", type=Path)
    parser.add_argument("--gap-minutes", type=int, default=90)
    parser.add_argument("--session-limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
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
        _print_result(_missing_adapter_payload(repo_root, adapter_path), as_json=args.json)
        return 0

    try:
        adapter = _load_adapter(adapter_path)
        jsonschema.validate(adapter, manifest_schema)
    except (OSError, ValueError, yaml.YAMLError, jsonschema.ValidationError) as exc:
        payload = _base_payload("invalid_adapter", repo_root, adapter_path, valid=False, errors=[str(exc)])
        _print_result(payload, as_json=args.json)
        return 1

    if not adapter.get("enabled", False):
        _print_result(_disabled_payload(repo_root, adapter_path), as_json=args.json)
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
        _print_result(payload, as_json=args.json)
        return 1
    if not records_path.is_file():
        _print_result(_no_records_payload(repo_root, adapter_path, records_path), as_json=args.json)
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
        _print_result(payload, as_json=args.json)
        return 1

    payload = _report_payload(repo_root, adapter_path, records_path, records, gap_minutes=args.gap_minutes, session_limit=args.session_limit)
    _print_result(payload, as_json=args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
