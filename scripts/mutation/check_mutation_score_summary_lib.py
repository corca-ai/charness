from __future__ import annotations

from collections import Counter
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.mutation.mutation_baseline_abort_lib import verdict_token  # noqa: E402

SURVIVED_DETAIL_LIMIT = 10
PARTIAL_RUN_COMPLETION_FLOOR = 0.75


def _source_line(repo_root: Path, module_path: str, line_number: int) -> str:
    try:
        return (
            (repo_root / module_path)
            .read_text(encoding="utf-8")
            .splitlines()[line_number - 1]
            .strip()
        )
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
        (
            partial and not metrics.get("per_file_completion_ok", True),
            "per-file partial completion",
        ),
        (metrics["status"] == "PASS-partial", "partial recovery closeout"),
        (not metrics["reachable"], "no reachable mutants"),
        (metrics["no_tests"], "no mutation possible"),
        (metrics.get("scope_gap", 0), "sampled mutants without coverage"),
        (metrics.get("changed_scope_gap_count", 0), "changed-line coverage"),
        (not metrics.get("sample_manifest_ok", True), "sample manifest"),
    )
    return [label for active, label in checks if active]


def build_summary_lines(
    records: list[tuple[dict, dict | None]],
    repo_root: Path,
    # `| str` because this reads `metrics["status"]` and `metrics["sample_manifest_issue"]`,
    # and hands the same dict to `blocking_signal_labels`, which declares the wider type.
    # `dict` is invariant in its value type, so the narrower annotation made that call a
    # type error -- and `status` is where `UNMEASURED` lands, the token this release adds.
    metrics: dict[str, float | int | bool | str],
) -> list[str]:
    reachable = int(metrics["reachable"])
    # THIRD spelling of the same rule, found by a round-2 review of the round-1 fix.
    # The status row had been routed through `verdict_token` while this row kept its
    # own `else "FAIL"`, so a zero-denominator run published two adjacent lines that
    # contradicted each other:
    #     - Status: **UNMEASURED**
    #     - Mutation score: **FAIL** (0.0% reachable score vs 60% threshold)
    # A triager reading the auto-filed issue sees the second line and concludes the
    # score collapsed -- which is the misdiagnosis (#612) this whole slice exists to
    # remove, reproduced by the slice's own repair.
    score_result = verdict_token(
        reachable, float(metrics["score"]) >= float(metrics["score_break"])
    )
    # And with no denominator the `0.0%` is the `else 0.0` fallback, not a
    # measurement, so it must not be presented as one scored against a threshold.
    score_detail = (
        f"({metrics['score']:.1f}% reachable score vs {metrics['score_break']:.0f}% threshold)"
        if reachable
        else "(no reachable mutant produced a verdict; no score was computed)"
    )
    blocking_labels = blocking_signal_labels(metrics)
    blocking_result = "FAIL" if blocking_labels else "PASS"
    blocking_detail = ", ".join(blocking_labels) or "none"
    lines = [
        "# Mutation Testing Summary",
        "",
        f"- Status: **{metrics['status']}**",
        f"- Mutation score: **{score_result}** {score_detail}",
        f"- Blocking signals: **{blocking_result}** ({blocking_detail})",
        f"- Total mutants: {metrics['total']}",
        f"- Executable mutants: {metrics['executable_total']} (total minus skipped)",
        f"- Executed: {metrics['executed']} ({metrics['executed_ratio'] * 100:.1f}% of executable total)",
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
    # "status reflects partial completion" is FALSE when the status is UNMEASURED:
    # there, the status reflects a zero denominator, not a completion ratio. Telling a
    # reader triaging a timeout that the status encodes completion sends them to the
    # wrong question.
    status_reflects = (
        "status reflects a zero denominator, not the completion ratio"
        if not reachable
        else f"status reflects partial completion (floor {PARTIAL_RUN_COMPLETION_FLOOR * 100:.0f}% of executable mutants)"
    )
    if metrics["exec_timed_out"]:
        lines.append(f"- Exec timeout fired; {status_reflects}.")
    elif metrics.get("incomplete_exec"):
        lines.append(f"- Exec did not complete all executable mutants; {status_reflects}.")
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
        lines.append(
            "- Blocking signal: sampled mutants were not covered by the selected test command."
        )
    if metrics.get("changed_scope_gap_count", 0):
        lines.append(
            "- Blocking signal: changed lines were left test-uncovered before mutation "
            "(budget/capacity drops of covered changed files are advisory, not blocking)."
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
            *[f"- `{operator}`: {count}" for operator, count in survived_details["operators"]],
            "",
            "Sample locations:",
            *[
                f"- `{module_path}:{line_number}` `{definition}` `{operator}`"
                + (f" - {source}" if source else "")
                for module_path, line_number, definition, operator, source in survived_details[
                    "locations"
                ]
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
