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

ROOT = repo_root_from_script(__file__)
_continuity = import_repo_module(__file__, "scripts.lesson_evaluation_continuity_lib")
# The ledger read, the retro scan, and the receipt scan moved into `lesson_evaluation_records_lib`
# when the retro run planner had to read the SAME facts to route an author to the
# session that still owes a score. They stay one implementation on purpose: a
# router that disagreed with this gate about which sessions exist would silently
# skip the session the gate later fails the repo over.
_records = import_repo_module(__file__, "scripts.lesson_evaluation_records_lib")


def build_report(repo_root: Path, *, as_of: date) -> dict[str, Any]:
    output_dir = _records.retro_output_dir(repo_root)
    sessions, score_events = _records.load_validated_ledger(repo_root)
    candidates = _records.collect_retro_candidates(repo_root)
    dispositions, receipt_violations = _records.collect_dispositions(candidates)
    receipts, collected_receipt_violations = _records.collect_receipts(
        output_dir=output_dir, sessions=sessions
    )
    receipt_violations = [*receipt_violations, *collected_receipt_violations]
    report = _continuity.reconcile_records(
        retros=dispositions,
        sessions=sessions,
        score_events=score_events,
        receipts=receipts,
        receipt_violations=receipt_violations,
        as_of=as_of,
    )
    # The denominator includes invalid-disposition retros too; the pure core sees
    # only successfully parsed rows, so restore the observable cohort count here.
    report["eligible_retro_count"] = len(candidates)
    report["disposition_count"] = len(dispositions)
    report["ok"] = report["eligible_retro_count"] == report["disposition_count"] and not report["violations"]
    return report


def render_human(report: dict[str, Any]) -> str:
    statuses = report["status_counts"]
    reasons = report["not_evaluated_reason_counts"]
    aggregate_violations = report["aggregate_violation_counts"]
    lines = [
        "Lesson evaluation continuity: "
        f"eligible durable retros={report['eligible_retro_count']}; "
        f"dispositions={report['disposition_count']}; "
        f"effect-recorded={statuses['effect-recorded']}; "
        f"no-effect={statuses['no-effect']}; "
        f"not-evaluated/missing-start={reasons['missing-start']}; "
        f"not-evaluated/emission-unproven={reasons['emission-unproven']}; "
        f"not-evaluated/presentation-unproven={reasons['presentation-unproven']}; "
        f"score-count-mismatch={aggregate_violations['score-count-mismatch']}; "
        f"duplicate-session-reference={aggregate_violations['duplicate-session-reference']}; "
        f"unclaimed-emission={aggregate_violations['unclaimed-emission']}; "
        f"score events (not a health measure)={report['score_event_count']}; "
        f"violations={report['violation_count']}"
    ]
    lines.extend(
        f"  - {item['id']}: {item['detail']}"
        + (f" [{item['path']}]" if "path" in item else "")
        + (f" (session {item['session_id']})" if "session_id" in item else "")
        for item in report["violations"]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = build_report(args.repo_root.resolve(), as_of=args.as_of)
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_human(report), end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
