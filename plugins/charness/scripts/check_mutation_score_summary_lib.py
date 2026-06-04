from __future__ import annotations

from collections import Counter
from pathlib import Path

SURVIVED_DETAIL_LIMIT = 10
PARTIAL_RUN_COMPLETION_FLOOR = 0.75


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


def blocking_signal_labels(metrics: dict[str, float | int | bool | str]) -> list[str]:
    partial = metrics["exec_timed_out"] or metrics.get("incomplete_exec")
    checks = (
        (metrics["pending"], "pending mutants"),
        (partial, "partial execution"),
        (partial and not metrics.get("per_file_completion_ok", True), "per-file partial completion"),
        (metrics["status"] == "PASS-partial", "partial recovery closeout"),
        (not metrics["reachable"], "no reachable mutants"),
        (metrics["no_tests"], "no mutation possible"),
        (metrics.get("scope_gap", 0), "sampled mutants without coverage"),
        (metrics.get("changed_scope_gap_count", 0), "changed-line coverage/selection"),
        (not metrics.get("sample_manifest_ok", True), "sample manifest"),
    )
    return [label for active, label in checks if active]


def build_summary_lines(
    records: list[tuple[dict, dict | None]],
    repo_root: Path,
    metrics: dict[str, float | int | bool],
) -> list[str]:
    score_result = "PASS" if metrics["reachable"] and float(metrics["score"]) >= float(metrics["score_break"]) else "FAIL"
    blocking_labels = blocking_signal_labels(metrics)
    blocking_result = "FAIL" if blocking_labels else "PASS"
    blocking_detail = ", ".join(blocking_labels) or "none"
    lines = [
        "# Mutation Testing Summary",
        "",
        f"- Status: **{metrics['status']}**",
        f"- Mutation score: **{score_result}** "
        f"({metrics['score']:.1f}% reachable score vs {metrics['score_break']:.0f}% threshold)",
        f"- Blocking signals: **{blocking_result}** ({blocking_detail})",
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
            "- Blocking signal: changed lines were left test-uncovered, or eligible changed files were dropped by selection/workload budgets, before mutation."
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
