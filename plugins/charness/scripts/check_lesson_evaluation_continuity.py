#!/usr/bin/env python3
"""Report lesson-evaluation disposition continuity for eligible durable retros."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

ROOT = repo_root_from_script(__file__)
_continuity = import_repo_module(__file__, "scripts.lesson_evaluation_continuity_lib")
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
_packet = import_repo_module(__file__, "scripts.prepare_packet_markdown_kind")

_PACKET_TITLE = re.compile(r"^# Retro Prepare Packet(?:\s+—\s+\S.*)?$")


def _retro_candidates(repo_root: Path) -> list[tuple[str, str]]:
    output_dir = repo_root / "charness-artifacts/retro"
    rows: list[tuple[str, str]] = []
    for path in sorted(output_dir.glob("*.md")):
        if path.name == "recent-lessons.md" or _packet.file_is_prepare_packet_markdown_kind(
            path,
            expected_kind="charness.retro_prepare_packet",
            expected_title_re=_PACKET_TITLE,
        ):
            continue
        text = path.read_text(encoding="utf-8")
        if _continuity.is_eligible_retro(path, text):
            rows.append((path.relative_to(repo_root).as_posix(), text))
    return rows


def build_report(repo_root: Path, *, as_of: date) -> dict[str, Any]:
    output_dir = repo_root / "charness-artifacts/retro"
    ledger_path = _ledger.lesson_ledger_path(output_dir)
    _ledger.validate_lesson_ledger(
        repo_root=repo_root,
        output_dir=output_dir,
        summary_path=output_dir / "recent-lessons.md",
    )
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    sessions = {event["session_id"]: event for event in payload["session_events"]}
    score_events = payload["score_events"]

    candidates = _retro_candidates(repo_root)
    dispositions: list[tuple[str, dict[str, Any]]] = []
    receipt_violations: list[dict[str, str]] = []
    for relpath, text in candidates:
        try:
            dispositions.append((relpath, _continuity.parse_disposition(text)))
        except ValueError as exc:
            identifier = "missing-disposition" if "found 0" in str(exc) else "invalid-disposition"
            receipt_violations.append(_continuity.violation(identifier, path=relpath, detail=str(exc)))

    receipts: dict[str, dict[str, Any]] = {}
    directory = _continuity.receipt_directory(output_dir)
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        session_id = path.stem
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if raw.get("session_id") != session_id:
                raise _continuity.LessonEvaluationError("receipt filename does not match session_id")
            receipt = _continuity.validate_receipt(
                raw, sessions=sessions, output_dir=output_dir
            )
            receipts[session_id] = receipt
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            receipt_violations.append(
                _continuity.violation("invalid-receipt", session_id=session_id, detail=str(exc))
            )
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
