#!/usr/bin/env python3
"""Report lesson-evaluation disposition continuity for eligible durable retros."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_continuity = import_repo_module(__file__, "scripts.lesson_evaluation_continuity_lib")
# The ledger read, the retro scan, and the receipt scan moved into `lesson_evaluation_records_lib`
# when the retro run planner had to read the SAME facts to route an author to the
# session that still owes a score. They stay one implementation on purpose: a
# router that disagreed with this gate about which sessions exist would silently
# skip the session the gate later fails the repo over.
_records = import_repo_module(__file__, "scripts.lesson_evaluation_records_lib")
# AGREEMENT lives apart from AUTHORING/INTEGRITY: this gate asks whether what a
# retro claims matches what the ledger holds, which is the reconcile half.
_reconcile = import_repo_module(__file__, "scripts.lesson_evaluation_reconcile_lib")


def build_report(repo_root: Path, *, as_of: date) -> dict[str, Any]:
    output_dir = _records.retro_output_dir(repo_root)
    sessions, score_events = _records.load_validated_ledger(repo_root)
    candidates = _records.collect_retro_candidates(repo_root)
    dispositions, receipt_violations = _records.collect_dispositions(candidates)
    receipts, collected_receipt_violations = _records.collect_receipts(
        output_dir=output_dir, sessions=sessions
    )
    receipt_violations = [*receipt_violations, *collected_receipt_violations]
    report = _reconcile.reconcile_records(
        retros=dispositions,
        sessions=sessions,
        score_events=score_events,
        receipts=receipts,
        receipt_violations=receipt_violations,
        as_of=as_of,
        recurrence_sources=_records.recurrence_sources(repo_root),
    )
    # The denominator includes invalid-disposition retros too; the pure core sees
    # only successfully parsed rows, so restore the observable cohort count here.
    report["eligible_retro_count"] = len(candidates)
    report["disposition_count"] = len(dispositions)
    report["ok"] = report["eligible_retro_count"] == report["disposition_count"] and not report["violations"]
    return report


# The only claim the deleted human renderer carried that the payload did not:
# `score_event_count` was labelled "(not a health measure)" inline. Output is
# unconditionally YAML now, so the non-claim rides in the payload or a reader
# starts treating a rising score count as improving health.
NON_CLAIMS = (
    "score_event_count counts recorded score events; it is NOT a health measure",
)


def report_payload(report: dict[str, Any]) -> dict[str, Any]:
    return {**report, "non_claims": list(NON_CLAIMS)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        report = build_report(args.repo_root.resolve(), as_of=args.as_of)
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    emit_yaml(report_payload(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
