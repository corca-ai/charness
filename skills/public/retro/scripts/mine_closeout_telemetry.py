#!/usr/bin/env python3
"""Mine the local closeout-telemetry stream for recurring operational waste.

Direction E2a of spec achieve-efficiency-improvements. ``retro`` reads
the per-repo closeout-telemetry stream written by E1
(``scripts/slice_closeout_telemetry.py``) and surfaces the objective waste that
RECURS across runs: gates that are repeatedly over budget, and repeated
over-slice (artifact-only-commit) runs.

Teeth (critique R1b): a recurring (``recurs:``) waste item dispositions to a
**filed issue** — tracked work the handoff chunker reasons over — NOT to the
recent-lessons digest, which has a ~14-day half-life and would decay the item
back out (the Problem-4 prose-decay trap this spec exists to fix). "noticed in a
retro" is not enough; recurring operational waste becomes tracked work.

Honest scope: this mines THIS repo's local, gitignored stream only. Waste that
happened while running the patched skills in another repo (e.g. acme) needs that
repo's own stream — charness has no cross-repo telemetry visibility.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path

# Sibling of the usage-episode stream; keep in sync with the E1 emitter default
# (scripts/slice_closeout_telemetry.CLOSEOUT_TELEMETRY_DEFAULT_PATH).
DEFAULT_STREAM_PATH = Path(".charness/usage-episodes/closeout_telemetry.jsonl")
DEFAULT_RECUR_MIN = 2
DISPOSITION_RECURRING = "file-issue"
DISPOSITION_ONE_OFF = "watch"
RECUR_MARKER = "recurs:"
CROSS_REPO_CLAIM = (
    "Mines this repo's local closeout-telemetry stream only; waste from running "
    "the skills in another repo lives in that repo's own stream (no cross-repo "
    "telemetry visibility)."
)


def _iter_records(lines: list[str]):
    """Yield well-formed closeout_telemetry records, tolerating malformed lines
    and ignoring any other jsonl event_type sharing the stream directory."""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except (ValueError, TypeError):
            continue
        if isinstance(record, dict) and record.get("event_type") == "closeout_telemetry":
            yield record


def _read_retained_records(lines: list[str]) -> tuple[list[dict], dict[str, object]]:
    """Read schema-1 records while retaining an audit of excluded input."""
    retained: list[dict] = []
    audit = {
        "physical_lines": len(lines),
        "blank_lines": 0,
        "nonblank_lines": 0,
        "malformed_lines": 0,
        "foreign_event_lines": 0,
        "unsupported_schema_lines": 0,
        "retained_records": 0,
    }
    for line in lines:
        stripped = line.strip()
        if not stripped:
            audit["blank_lines"] += 1
            continue
        audit["nonblank_lines"] += 1
        try:
            record = json.loads(stripped)
        except (ValueError, TypeError):
            audit["malformed_lines"] += 1
            continue
        if not isinstance(record, dict):
            audit["malformed_lines"] += 1
            continue
        if record.get("event_type") != "closeout_telemetry":
            audit["foreign_event_lines"] += 1
            continue
        if record.get("schema_version") != 1:
            audit["unsupported_schema_lines"] += 1
            continue
        retained.append(record)
    audit["retained_records"] = len(retained)
    return retained, audit


def _finite_elapsed(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _elapsed_summary(observations: list[tuple[float | None, float | None]]) -> dict[str, object]:
    values = [elapsed for elapsed, _ in observations if elapsed is not None]
    budgets = [budget for _, budget in observations if budget is not None]
    paired = [
        (elapsed, budget)
        for elapsed, budget in observations
        if elapsed is not None and budget is not None
    ]
    summary: dict[str, object] = {
        "numeric_observations": len(values),
        "excluded_elapsed_values": len(observations) - len(values),
        "total_seconds": round(sum(values), 2) if values else None,
        "mean_seconds": round(statistics.mean(values), 2) if values else None,
        "median_seconds": round(statistics.median(values), 2) if values else None,
        "min_seconds": min(values) if values else None,
        "max_seconds": max(values) if values else None,
        "paired_observations": len(paired),
    }
    unique_budgets = sorted(set(budgets))
    summary["budget_seconds"] = unique_budgets[0] if len(unique_budgets) == 1 else None
    summary["budget_seconds_values"] = unique_budgets
    if paired and len(paired) == len(observations):
        summary["excess_seconds"] = round(
            sum(value - budget for value, budget in paired), 2
        )
    else:
        summary["excess_seconds"] = None
    return summary


def mine_detailed(
    lines: list[str], *, stream_status: str = "present", recur_min: int = DEFAULT_RECUR_MIN
) -> dict:
    """Produce the opt-in operator receipt for the current readable stream."""
    records, audit = _read_retained_records(lines)
    result = _mine_records(records, recur_min=recur_min, finite_elapsed=True)
    timestamps = sorted(
        str(record["timestamp"]) for record in records if record.get("timestamp")
    )
    statuses = Counter(str(record.get("status") or "unknown") for record in records)
    detail: dict[str, object] = {
        "stream_read": {"status": stream_status},
        "population": {
            **audit,
            "window_start": timestamps[0] if timestamps else None,
            "window_end": timestamps[-1] if timestamps else None,
            "status_counts": dict(sorted(statuses.items())),
            "scope": "current readable stream only; rotation and lost history are unknown",
        },
        "non_claims": [
            "historical runner, profile, run identity, command exit status, and suite pass/fail are unavailable",
            "over-slice occurrences and trailing run length are a separate unit from elapsed seconds",
            "recurrence is a cost signal, not permission to weaken, skip, reschedule, or move proof",
        ],
        "unit_separation": "over_slice is occurrences/run length; gate_runtime is elapsed seconds",
    }
    for finding in result["findings"]:
        if finding["kind"] != "gate_runtime":
            continue
        matched: list[tuple[dict, dict]] = []
        for record in records:
            entries = (record.get("gate_runtime") or {}).get("over_budget") or []
            for entry in entries:
                if f"{entry.get('phase')}:{entry.get('command')}" == finding["key"]:
                    matched.append((record, entry))
        observations: list[tuple[float | None, float | None]] = []
        for _, entry in matched:
            parsed = _finite_elapsed(entry.get("elapsed_seconds"))
            budget = _finite_elapsed(entry.get("budget_seconds"))
            observations.append((parsed, budget))
        matched_records: list[dict] = []
        matched_record_ids: set[int] = set()
        for record, _ in matched:
            if id(record) not in matched_record_ids:
                matched_record_ids.add(id(record))
                matched_records.append(record)
        matching_timestamps = [
            str(record["timestamp"])
            for record, _ in matched
            if record.get("timestamp")
        ]
        finding["detail"] = {
            "matching_records": len(matched_records),
            "matching_entries": len(matched),
            "record_status_counts": dict(
                sorted(
                    Counter(
                        str(record.get("status") or "unknown")
                        for record in matched_records
                    ).items()
                )
            ),
            "window_start": min(matching_timestamps, default=None),
            "window_end": max(matching_timestamps, default=None),
            "elapsed_seconds": _elapsed_summary(observations),
        }
    result["detail"] = detail
    return result


def _aggregate(
    records: list[dict], *, finite_elapsed: bool = False
) -> tuple[int, dict, int, list[int]]:
    gate_counts: dict[str, dict] = {}
    over_slice_count = 0
    over_slice_runs: list[int] = []
    examined = 0
    for record in records:
        examined += 1
        gate_runtime = record.get("gate_runtime") or {}
        for entry in gate_runtime.get("over_budget") or []:
            phase = entry.get("phase")
            command = str(entry.get("command") or "")
            key = f"{phase}:{command}"
            agg = gate_counts.setdefault(
                key, {"phase": phase, "command": command, "count": 0, "elapsed_seconds": []}
            )
            agg["count"] += 1
            if finite_elapsed:
                parsed = _finite_elapsed(entry.get("elapsed_seconds"))
                if parsed is not None:
                    agg["elapsed_seconds"].append(parsed)
            else:
                try:
                    agg["elapsed_seconds"].append(float(entry.get("elapsed_seconds")))
                except (TypeError, ValueError):
                    pass
        over_slice = record.get("over_slice") or {}
        if over_slice.get("over"):
            over_slice_count += 1
            run = over_slice.get("trailing_artifact_only_run")
            if isinstance(run, int):
                over_slice_runs.append(run)
    return examined, gate_counts, over_slice_count, over_slice_runs


def _disposition(recurring: bool) -> tuple[str, str]:
    if recurring:
        return DISPOSITION_RECURRING, RECUR_MARKER
    return DISPOSITION_ONE_OFF, ""


def _mine_records(
    records: list[dict], recur_min: int = DEFAULT_RECUR_MIN, *, finite_elapsed: bool = False
) -> dict:
    """Aggregate a closeout-telemetry stream into waste findings. A waste item
    seen in >= ``recur_min`` records is recurring and routes to a filed issue;
    a one-off routes to ``watch`` (never the decaying digest)."""
    recur_min = max(2, recur_min)
    examined, gate_counts, over_slice_count, over_slice_runs = _aggregate(
        records, finite_elapsed=finite_elapsed
    )
    findings: list[dict] = []
    for key, agg in sorted(gate_counts.items(), key=lambda kv: (-kv[1]["count"], kv[0])):
        recurring = agg["count"] >= recur_min
        disposition, marker = _disposition(recurring)
        secs = agg["elapsed_seconds"]
        findings.append(
            {
                "kind": "gate_runtime",
                "key": key,
                "phase": agg["phase"],
                "command": agg["command"],
                "occurrences": agg["count"],
                "peak_elapsed_seconds": max(secs) if secs else None,
                "recurring": recurring,
                "marker": marker,
                "disposition": disposition,
            }
        )
    if over_slice_count:
        recurring = over_slice_count >= recur_min
        disposition, marker = _disposition(recurring)
        findings.append(
            {
                "kind": "over_slice",
                "key": "over_slice",
                "occurrences": over_slice_count,
                "peak_run": max(over_slice_runs) if over_slice_runs else None,
                "recurring": recurring,
                "marker": marker,
                "disposition": disposition,
            }
        )
    recurring_findings = [f for f in findings if f["recurring"]]
    return {
        "stream_event_type": "closeout_telemetry",
        "records_examined": examined,
        "recur_min": recur_min,
        "findings": findings,
        "recurring_count": len(recurring_findings),
        "disposition_summary": (
            f"{len(recurring_findings)} recurring waste item(s) -> file issue "
            "(tracked work the chunker reasons over); NOT the recent-lessons digest "
            "(it decays)."
            if recurring_findings
            else "no recurring waste in the mined window."
        ),
        "cross_repo_claim": CROSS_REPO_CLAIM,
    }


def mine(lines: list[str], recur_min: int = DEFAULT_RECUR_MIN) -> dict:
    """Aggregate a closeout-telemetry stream into waste findings."""
    return _mine_records(list(_iter_records(lines)), recur_min=recur_min)


def _read_lines(repo_root: Path, stream_path: Path) -> list[str]:
    try:
        return (repo_root / stream_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def _read_lines_for_detail(repo_root: Path, stream_path: Path) -> tuple[list[str], str]:
    try:
        return (repo_root / stream_path).read_text(encoding="utf-8").splitlines(), "present"
    except FileNotFoundError:
        return [], "missing"
    except OSError:
        return [], "unreadable"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repository root used to resolve the closeout-telemetry stream path.",
    )
    parser.add_argument(
        "--stream-path",
        type=Path,
        default=DEFAULT_STREAM_PATH,
        help="Closeout-telemetry JSONL path relative to --repo-root.",
    )
    parser.add_argument(
        "--recur-min",
        type=int,
        default=DEFAULT_RECUR_MIN,
        help="Minimum occurrence count that marks a waste item as recurring.",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Emit an operator receipt with stream audit and elapsed summaries.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    if args.detail:
        lines, stream_status = _read_lines_for_detail(repo_root, args.stream_path)
        result = mine_detailed(lines, stream_status=stream_status, recur_min=args.recur_min)
    else:
        result = mine(_read_lines(repo_root, args.stream_path), recur_min=args.recur_min)
    result["stream_path"] = str(args.stream_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
