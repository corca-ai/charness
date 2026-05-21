#!/usr/bin/env python3
"""Compute mutation score from a Cosmic Ray dump and gate on adapter score_break.

Reads `reports/mutation/cosmic-ray-dump.jsonl` (`cosmic-ray dump` output),
reads `mutation_testing.score_break` and `report_paths.summary_md` from
`.agents/quality-adapter.yaml`, writes a GitHub-issue-renderable summary, and
exits non-zero when the reachable-mutant score breaks the threshold.

Contract: skills/public/quality/references/mutation-testing.md §commands.summary.
Denominator: killed / (killed + survived). Native no-mutation-possible outcomes
and Charness coverage scope gaps are reported separately and do not enter the
score.
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

from scripts.mutation_sample_manifest_score_lib import (  # noqa: E402
    changed_scope_gap_section_lines,
    sample_manifest_scope_gap_details,
)
from scripts.quality_adapter_lib import load_quality_adapter  # noqa: E402

SURVIVED_DETAIL_LIMIT = 10
PARTIAL_RUN_COMPLETION_FLOOR = 0.75
UNCOVERED_MUTATION_SKIP_OUTPUT = "Filtered uncovered mutation line"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--stats",
        type=Path,
        default=Path("reports/mutation/cosmic-ray-dump.jsonl"),
        help="Path to cosmic-ray dump output (default: reports/mutation/cosmic-ray-dump.jsonl).",
    )
    parser.add_argument(
        "--timeout-marker",
        type=Path,
        default=Path("reports/mutation/exec-timeout.json"),
        help="Path to the exec-timeout marker emitted by run_cosmic_ray_mutation.py.",
    )
    parser.add_argument(
        "--sample-manifest",
        type=Path,
        default=Path("reports/mutation/sample.json"),
        help="Path to the sample manifest emitted by sample_mutation_files.py.",
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
        "scope_gap": 0,
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
            if str(result.get("output") or "").startswith(UNCOVERED_MUTATION_SKIP_OUTPUT):
                counts["scope_gap"] += 1
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


def mutation_metrics(
    stats: dict[str, int],
    score_break: float,
    *,
    exec_timed_out: bool = False,
    per_file_completion_ok: bool = True,
    changed_scope_gap_count: int = 0,
    sample_manifest_ok: bool = True,
    sample_manifest_issue: str = "",
) -> dict[str, float | int | bool | str]:
    killed = stats["killed"]
    survived = stats["survived"]
    reachable = killed + survived
    score = (killed / reachable * 100.0) if reachable else 0.0
    total = stats["total"]
    skipped = stats.get("skipped", 0)
    executable_total = total - skipped
    executed = executable_total - stats["pending"]
    executed_ratio = (executed / executable_total) if executable_total else 0.0
    score_passes = (
        reachable > 0
        and stats["no_tests"] == 0
        and stats.get("scope_gap", 0) == 0
        and changed_scope_gap_count == 0
        and sample_manifest_ok
        and score >= score_break
    )
    incomplete_exec = stats["pending"] > 0
    if exec_timed_out:
        completion_ok = executed_ratio >= PARTIAL_RUN_COMPLETION_FLOOR and per_file_completion_ok
        passed = False
        if not completion_ok:
            status = "FAIL-incomplete"
        elif score_passes:
            status = "PASS-partial"
        else:
            status = "FAIL"
    elif incomplete_exec:
        passed = False
        status = "FAIL-incomplete"
    else:
        passed = score_passes
        status = "PASS" if passed else "FAIL"
    return {
        **stats,
        "reachable": reachable,
        "score": score,
        "score_break": score_break,
        "executable_total": executable_total,
        "executed": executed,
        "executed_ratio": executed_ratio,
        "exec_timed_out": exec_timed_out,
        "incomplete_exec": incomplete_exec,
        "per_file_completion_ok": per_file_completion_ok,
        "changed_scope_gap_count": changed_scope_gap_count,
        "sample_manifest_ok": sample_manifest_ok,
        "sample_manifest_issue": sample_manifest_issue,
        "passed": passed,
        "status": status,
    }


def mutation_file_completion(
    records: list[tuple[dict, dict | None]],
    *,
    floor: float = PARTIAL_RUN_COMPLETION_FLOOR,
) -> tuple[bool, list[str]]:
    stats: dict[str, dict[str, int]] = {}
    for work_item, result in records:
        mutations = work_item.get("mutations") or []
        module_path = str((mutations[0] or {}).get("module_path") or "<unknown>") if mutations else "<unknown>"
        bucket = stats.setdefault(module_path, {"total": 0, "skipped": 0, "pending": 0})
        bucket["total"] += 1
        if result is None:
            bucket["pending"] += 1
            continue
        if result.get("worker_outcome") == "skipped":
            bucket["skipped"] += 1

    incomplete: list[str] = []
    for module_path, bucket in sorted(stats.items()):
        executable_total = bucket["total"] - bucket["skipped"]
        if executable_total <= 0:
            continue
        executed = executable_total - bucket["pending"]
        ratio = executed / executable_total
        if executed <= 0 or ratio < floor:
            incomplete.append(f"{module_path} {executed}/{executable_total} ({ratio*100:.1f}%)")
    return not incomplete, incomplete


def _read_timeout_marker(marker_path: Path) -> tuple[bool, int | None]:
    if not marker_path.is_file():
        return False, None
    try:
        data = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, None
    if not isinstance(data, dict):
        return False, None
    timed_out = bool(data.get("exec_timed_out"))
    raw_seconds = data.get("exec_timeout_seconds")
    seconds = int(raw_seconds) if isinstance(raw_seconds, (int, float)) else None
    return timed_out, seconds


def build_summary_lines(
    records: list[tuple[dict, dict | None]],
    repo_root: Path,
    metrics: dict[str, float | int | bool],
) -> list[str]:
    lines = [
        "# Mutation Testing Summary",
        "",
        f"- Status: **{metrics['status']}** "
        f"({metrics['score']:.1f}% reachable score vs {metrics['score_break']:.0f}% threshold)",
        f"- Total mutants: {metrics['total']}",
        f"- Executable mutants: {metrics['executable_total']} (total minus skipped)",
        f"- Executed: {metrics['executed']} ({metrics['executed_ratio']*100:.1f}% of executable total)",
        f"- Killed: {metrics['killed']}",
        f"- Survived: {metrics['survived']}",
        f"- Scope gaps (uncovered sampled mutants): {metrics.get('scope_gap', 0)}",
        f"- No mutation possible: {metrics['no_tests']}",
        f"- Incompetent: {metrics['incompetent']}",
    ]
    if metrics["pending"]:
        lines.append(f"- Pending (not executed): {metrics['pending']}")
        lines.append("- Blocking signal: mutation execution left pending mutants.")
    if metrics["abnormal"]:
        lines.append(f"- Worker abnormal/exception: {metrics['abnormal']}")
    if metrics["skipped"]:
        lines.append(f"- Skipped: {metrics['skipped']}")
    if metrics["exec_timed_out"]:
        lines.append(
            f"- Exec timeout fired; status reflects partial completion "
            f"(floor {PARTIAL_RUN_COMPLETION_FLOOR*100:.0f}% of executable mutants)."
        )
    elif metrics.get("incomplete_exec"):
        lines.append(
            f"- Exec did not complete all executable mutants; status reflects partial completion "
            f"(floor {PARTIAL_RUN_COMPLETION_FLOOR*100:.0f}% of executable mutants)."
        )
    if metrics["exec_timed_out"] or metrics.get("incomplete_exec"):
        if not metrics.get("per_file_completion_ok", True):
            lines.append("- Blocking signal: partial run did not meet per-sampled-file completion.")
    if metrics["status"] == "PASS-partial":
        lines.append("- Blocking signal: partial mutation runs cannot close a recovery issue.")
    if not metrics["reachable"]:
        lines.append("- Blocking signal: no reachable mutants were executed.")
    if metrics["no_tests"]:
        lines.append("- Blocking signal: Cosmic Ray reported mutants with no mutation possible.")
    if metrics.get("scope_gap", 0):
        lines.append("- Blocking signal: sampled mutants were not covered by the selected test command.")
    if metrics.get("changed_scope_gap_count", 0):
        lines.append(
            "- Blocking signal: changed files were excluded before mutation by coverage, mutation-line, or selection-budget filters."
        )
    if not metrics.get("sample_manifest_ok", True):
        lines.append(f"- Blocking signal: {metrics['sample_manifest_issue']}")
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
        "Native Cosmic Ray no-mutation-possible results and Charness filtered",
        "scope gaps are surfaced as separate blocking signals above and do not",
        "enter the score. Skipped mutants are explicitly filtered work items and",
        "also stay out of the score and completion denominators.",
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
    timeout_marker_path = (
        args.timeout_marker if args.timeout_marker.is_absolute() else repo_root / args.timeout_marker
    )
    sample_manifest_path = (
        args.sample_manifest if args.sample_manifest.is_absolute() else repo_root / args.sample_manifest
    )
    exec_timed_out, _ = _read_timeout_marker(timeout_marker_path)
    per_file_completion_ok, incomplete_files = mutation_file_completion(records)
    changed_scope_gap_files, changed_scope_gap_details, sample_manifest_issue = sample_manifest_scope_gap_details(
        sample_manifest_path
    )
    changed_scope_gap_count = len(changed_scope_gap_files)
    metrics = mutation_metrics(
        stats,
        score_break,
        exec_timed_out=exec_timed_out,
        per_file_completion_ok=per_file_completion_ok,
        changed_scope_gap_count=changed_scope_gap_count,
        sample_manifest_ok=not sample_manifest_issue,
        sample_manifest_issue=sample_manifest_issue,
    )
    lines = build_summary_lines(records, repo_root, metrics)
    if changed_scope_gap_files:
        try:
            insert_at = lines.index("Score denominator: `killed / (killed + survived)` (reachable mutants only;")
        except ValueError:
            insert_at = len(lines)
        lines[insert_at:insert_at] = changed_scope_gap_section_lines(
            changed_scope_gap_files,
            changed_scope_gap_details,
        )
    if incomplete_files:
        try:
            insert_at = lines.index("Score denominator: `killed / (killed + survived)` (reachable mutants only;")
        except ValueError:
            insert_at = len(lines)
        lines[insert_at:insert_at] = [
            "",
            "## Incomplete Sampled Files",
            "",
            "- Incomplete sampled files:",
            *[f"  - `{item}`" for item in incomplete_files[:10]],
            "",
        ]

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    sys.stdout.write(f"summary written to {summary_path}\n")
    sys.stdout.write(
        f"score: {metrics['score']:.1f}% threshold: {score_break:.0f}% "
        f"executed: {metrics['executed']}/{metrics['executable_total']} "
        f"status: {metrics['status']}\n"
    )
    return 0 if metrics["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
