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
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.quality_adapter_lib import load_quality_adapter  # noqa: E402

SURVIVED_DETAIL_LIMIT = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--stats",
        type=Path,
        default=Path("reports/mutation/cosmic-ray-dump.jsonl"),
        help="Path to cosmic-ray dump output (default: reports/mutation/cosmic-ray-dump.jsonl).",
    )
    return parser.parse_args()


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
            continue
        elif worker_outcome in {"abnormal", "exception"}:
            counts["abnormal"] += 1
        elif worker_outcome == "skipped":
            counts["skipped"] += 1
            continue

        if test_outcome == "killed":
            counts["killed"] += 1
        elif test_outcome == "survived":
            counts["survived"] += 1
        elif test_outcome == "incompetent":
            counts["incompetent"] += 1
    return counts


def _source_line(repo_root: Path, module_path: str, line_number: int) -> str:
    try:
        return (repo_root / module_path).read_text(encoding="utf-8").splitlines()[line_number - 1].strip()
    except (OSError, IndexError):
        return ""


def summarize_survived_mutations(
    records: list[tuple[dict, dict | None]],
    repo_root: Path,
    *,
    limit: int = SURVIVED_DETAIL_LIMIT,
) -> dict[str, list[tuple]]:
    by_definition: Counter[str] = Counter()
    by_operator: Counter[str] = Counter()
    locations: list[tuple[str, int, str, str, str]] = []

    for work_item, result in records:
        if not result or result.get("worker_outcome") == "skipped":
            continue
        if result.get("test_outcome") != "survived":
            continue
        for mutation in work_item.get("mutations", []):
            definition = mutation.get("definition_name") or "<module>"
            operator = mutation.get("operator_name") or "<unknown>"
            module_path = mutation.get("module_path") or "<unknown>"
            start_pos = mutation.get("start_pos") or [0, 0]
            line_number = int(start_pos[0]) if start_pos else 0
            by_definition[definition] += 1
            by_operator[operator] += 1
            locations.append(
                (
                    str(module_path),
                    line_number,
                    definition,
                    operator,
                    _source_line(repo_root, str(module_path), line_number) if line_number else "",
                )
            )

    return {
        "definitions": by_definition.most_common(limit),
        "operators": by_operator.most_common(limit),
        "locations": locations[:limit],
    }


def load_mutation_config(repo_root: Path) -> tuple[float, Path] | None:
    payload = load_quality_adapter(repo_root)
    if payload.get("errors"):
        sys.stderr.write("quality adapter validation failed; resolve errors first.\n")
        for err in payload["errors"]:
            sys.stderr.write(f"  - {err}\n")
        return None

    block = (payload.get("data") or {}).get("mutation_testing") or {}
    score_break = float(block.get("score_break", 60))
    summary_rel = (block.get("report_paths") or {}).get("summary_md") or "reports/mutation/summary.md"
    return score_break, repo_root / summary_rel


def mutation_metrics(stats: dict[str, int], score_break: float) -> dict[str, float | int | bool]:
    killed = stats["killed"]
    survived = stats["survived"]
    reachable = killed + survived
    score = (killed / reachable * 100.0) if reachable else 0.0
    return {
        **stats,
        "reachable": reachable,
        "score": score,
        "score_break": score_break,
        "passed": reachable > 0 and stats["no_tests"] == 0 and score >= score_break,
    }


def build_summary_lines(
    records: list[tuple[dict, dict | None]],
    repo_root: Path,
    metrics: dict[str, float | int | bool],
) -> list[str]:
    lines = [
        "# Mutation Testing Summary",
        "",
        f"- Status: **{'PASS' if metrics['passed'] else 'FAIL'}** "
        f"({metrics['score']:.1f}% reachable score vs {metrics['score_break']:.0f}% threshold)",
        f"- Total mutants: {metrics['total']}",
        f"- Killed: {metrics['killed']}",
        f"- Survived: {metrics['survived']}",
        f"- No tests (scope gap): {metrics['no_tests']}",
        f"- Incompetent: {metrics['incompetent']}",
    ]
    if metrics["pending"]:
        lines.append(f"- Pending: {metrics['pending']}")
    if metrics["abnormal"]:
        lines.append(f"- Worker abnormal/exception: {metrics['abnormal']}")
    if metrics["skipped"]:
        lines.append(f"- Skipped: {metrics['skipped']}")
    if not metrics["reachable"]:
        lines.append("- Blocking signal: no reachable mutants were executed.")
    if metrics["no_tests"]:
        lines.append("- Blocking signal: no-tests mutants indicate a mutation scope gap.")
    if metrics["survived"]:
        survived_details = summarize_survived_mutations(records, repo_root)
        lines += [
            "",
            "## Survived Mutants",
            "",
            "Top definitions:",
            *[
                f"- `{definition}`: {count}"
                for definition, count in survived_details["definitions"]
            ],
            "",
            "Top operators:",
            *[
                f"- `{operator}`: {count}"
                for operator, count in survived_details["operators"]
            ],
            "",
            "Sample locations:",
            *[
                f"- `{module_path}:{line_number}` `{definition}` `{operator}`"
                + (f" - {source}" if source else "")
                for module_path, line_number, definition, operator, source in survived_details["locations"]
            ],
        ]
    return lines + [
        "",
        "Score denominator: `killed / (killed + survived)` (reachable mutants only;",
        "see `skills/public/quality/references/mutation-testing.md` §commands.summary).",
        "No-tests mutants represent test-scope gaps rather than test weakness, so they",
        "are surfaced as a separate signal above and do not enter the score. Skipped",
        "mutants are explicitly filtered low-signal work items and also stay out of",
        "the score denominator.",
        "",
    ]


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    stats_path = args.stats if args.stats.is_absolute() else (repo_root / args.stats)
    if not stats_path.is_file():
        sys.stderr.write(
            f"mutation stats not found at {stats_path}. Run `cosmic-ray dump` first.\n"
        )
        return 2

    try:
        records = iter_dump_records(stats_path)
        stats = summarize_cosmic_ray(records)
    except ValueError as exc:
        sys.stderr.write(f"could not parse mutation stats: {exc}\n")
        return 2

    config = load_mutation_config(repo_root)
    if config is None:
        return 2
    score_break, summary_path = config
    metrics = mutation_metrics(stats, score_break)
    lines = build_summary_lines(records, repo_root, metrics)

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    sys.stdout.write(f"summary written to {summary_path}\n")
    sys.stdout.write(
        f"score: {metrics['score']:.1f}% threshold: {score_break:.0f}% "
        f"status: {'PASS' if metrics['passed'] else 'FAIL'}\n"
    )
    return 0 if metrics["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
