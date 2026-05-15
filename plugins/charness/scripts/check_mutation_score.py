#!/usr/bin/env python3
"""Compute mutation score from a Cosmic Ray dump and gate on adapter score_break.

Reads `reports/mutation/cosmic-ray-dump.jsonl` (`cosmic-ray dump` output),
reads `mutation_testing.score_break` and `report_paths.summary_md` from
`.agents/quality-adapter.yaml`, writes a GitHub-issue-renderable summary, and
exits non-zero when the reachable-mutant score breaks the threshold.

Contract: skills/public/quality/references/mutation-testing.md §commands.summary.
Denominator: killed / (killed + survived). No-tests mutants are reported
separately as a scope-gap signal and do not enter the score.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.quality_adapter_lib import load_quality_adapter  # noqa: E402


def iter_dump_records(stats_path: Path) -> list[tuple[dict, dict | None]]:
    records: list[tuple[dict, dict | None]] = []
    for line_no, line in enumerate(stats_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            item = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_no}: {exc}") from exc
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"expected [work_item, result] pair on line {line_no}")
        work_item, result = item
        if not isinstance(work_item, dict):
            raise ValueError(f"expected work item object on line {line_no}")
        if result is not None and not isinstance(result, dict):
            raise ValueError(f"expected result object or null on line {line_no}")
        records.append((work_item, result))
    return records


def summarize_cosmic_ray(records: list[tuple[dict, dict | None]]) -> dict[str, int]:
    counts = {
        "total": len(records),
        "killed": 0,
        "survived": 0,
        "incompetent": 0,
        "no_tests": 0,
        "pending": 0,
        "abnormal": 0,
        "skipped": 0,
    }
    for _work_item, result in records:
        if result is None:
            counts["pending"] += 1
            continue
        worker_outcome = result.get("worker_outcome")
        test_outcome = result.get("test_outcome")
        if worker_outcome == "no-test":
            counts["no_tests"] += 1
        elif worker_outcome in {"abnormal", "exception"}:
            counts["abnormal"] += 1
        elif worker_outcome == "skipped":
            counts["skipped"] += 1

        if test_outcome == "killed":
            counts["killed"] += 1
        elif test_outcome == "survived":
            counts["survived"] += 1
        elif test_outcome == "incompetent":
            counts["incompetent"] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--stats",
        type=Path,
        default=Path("reports/mutation/cosmic-ray-dump.jsonl"),
        help="Path to cosmic-ray dump output (default: reports/mutation/cosmic-ray-dump.jsonl).",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    stats_path = args.stats if args.stats.is_absolute() else (repo_root / args.stats)
    if not stats_path.is_file():
        sys.stderr.write(
            f"mutation stats not found at {stats_path}. Run `cosmic-ray dump` first.\n"
        )
        return 2

    try:
        stats = summarize_cosmic_ray(iter_dump_records(stats_path))
    except ValueError as exc:
        sys.stderr.write(f"could not parse mutation stats: {exc}\n")
        return 2

    payload = load_quality_adapter(repo_root)
    if payload.get("errors"):
        sys.stderr.write("quality adapter validation failed; resolve errors first.\n")
        for err in payload["errors"]:
            sys.stderr.write(f"  - {err}\n")
        return 2

    block = (payload.get("data") or {}).get("mutation_testing") or {}
    score_break = float(block.get("score_break", 60))
    summary_rel = (block.get("report_paths") or {}).get("summary_md") or "reports/mutation/summary.md"
    summary_path = repo_root / summary_rel

    killed = stats["killed"]
    survived = stats["survived"]
    no_tests = stats["no_tests"]
    incompetent = stats["incompetent"]
    pending = stats["pending"]
    abnormal = stats["abnormal"]
    skipped = stats["skipped"]
    total = stats["total"]
    reachable = killed + survived
    score = (killed / reachable * 100.0) if reachable else 100.0
    passed = score >= score_break

    lines = [
        "# Mutation Testing Summary",
        "",
        f"- Status: **{'PASS' if passed else 'FAIL'}** "
        f"({score:.1f}% reachable score vs {score_break:.0f}% threshold)",
        f"- Total mutants: {total}",
        f"- Killed: {killed}",
        f"- Survived: {survived}",
        f"- No tests (scope gap): {no_tests}",
        f"- Incompetent: {incompetent}",
    ]
    if pending:
        lines.append(f"- Pending: {pending}")
    if abnormal:
        lines.append(f"- Worker abnormal/exception: {abnormal}")
    if skipped:
        lines.append(f"- Skipped: {skipped}")
    lines += [
        "",
        "Score denominator: `killed / (killed + survived)` (reachable mutants only;",
        "see `skills/public/quality/references/mutation-testing.md` §commands.summary).",
        "No-tests mutants represent test-scope gaps rather than test weakness, so they",
        "are surfaced as a separate signal above and do not enter the score.",
        "",
    ]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    sys.stdout.write(f"summary written to {summary_path}\n")
    sys.stdout.write(
        f"score: {score:.1f}% threshold: {score_break:.0f}% status: {'PASS' if passed else 'FAIL'}\n"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
