#!/usr/bin/env python3
"""Mine the local closeout-telemetry stream for recurring operational waste.

Direction E2a of spec achieve-efficiency-improvements. The weekly ``retro`` reads
the per-repo closeout-telemetry stream written by E1
(``scripts/slice_closeout_telemetry.py``) and surfaces the objective waste that
RECURS across runs: gates that pass but are repeatedly over budget, and repeated
over-slice (artifact-only-commit) runs.

Teeth (critique R1b): a recurring (``recurs:``) waste item dispositions to a
**filed issue** — tracked work the handoff chunker reasons over — NOT to the
recent-lessons digest, which has a ~14-day half-life and would decay the item
back out (the Problem-4 prose-decay trap this spec exists to fix). "noticed in a
retro" is not enough; recurring operational waste becomes tracked work.

Honest scope: this mines THIS repo's local, gitignored stream only. Waste that
happened while running the patched skills in another repo (e.g. ceal) needs that
repo's own stream — charness has no cross-repo telemetry visibility.
"""
from __future__ import annotations

import argparse
import json
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


def _aggregate(records: list[dict]) -> tuple[int, dict, int, list[int]]:
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


def mine(lines: list[str], recur_min: int = DEFAULT_RECUR_MIN) -> dict:
    """Aggregate a closeout-telemetry stream into waste findings. A waste item
    seen in >= ``recur_min`` records is recurring and routes to a filed issue;
    a one-off routes to ``watch`` (never the decaying digest)."""
    recur_min = max(2, recur_min)
    records = list(_iter_records(lines))
    examined, gate_counts, over_slice_count, over_slice_runs = _aggregate(records)
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


def _read_lines(repo_root: Path, stream_path: Path) -> list[str]:
    try:
        return (repo_root / stream_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--stream-path", type=Path, default=DEFAULT_STREAM_PATH)
    parser.add_argument("--recur-min", type=int, default=DEFAULT_RECUR_MIN)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    result = mine(_read_lines(repo_root, args.stream_path), recur_min=args.recur_min)
    result["stream_path"] = str(args.stream_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
