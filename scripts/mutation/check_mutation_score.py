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

from scripts.runtime_bootstrap import repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

from scripts.mutation import (  # noqa: E402
    check_mutation_score_summary_lib as mutation_score_summary,  # noqa: E402
)
from scripts.mutation.mutation_baseline_abort_lib import (  # noqa: E402
    DEFAULT_BASELINE_ABORT_MARKER,
    UNMEASURED_STATUS,
    baseline_abort_cause,
    read_baseline_abort_marker,
    resolve_baseline_abort_marker,
    verdict_token,
)
from scripts.mutation.mutation_sample_manifest_score_lib import (  # noqa: E402
    changed_scope_gap_section_lines,
    sample_manifest_scope_gap_details,
)
from scripts.quality_adapter_lib import load_quality_adapter  # noqa: E402

PARTIAL_RUN_COMPLETION_FLOOR = mutation_score_summary.PARTIAL_RUN_COMPLETION_FLOOR
SURVIVED_DETAIL_LIMIT = mutation_score_summary.SURVIVED_DETAIL_LIMIT
blocking_signal_labels = mutation_score_summary.blocking_signal_labels
build_summary_lines = mutation_score_summary.build_summary_lines
summarize_survived_mutations = mutation_score_summary.summarize_survived_mutations

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
    parser.add_argument(
        "--baseline-abort-marker",
        type=Path,
        default=DEFAULT_BASELINE_ABORT_MARKER,
        help="Path to the coverage-baseline abort marker emitted by sample_mutation_files.py.",
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


def load_mutation_config(repo_root: Path) -> tuple[float, Path] | None:
    payload = load_quality_adapter(repo_root)
    if payload.get("errors"):
        sys.stderr.write("quality adapter validation failed; resolve errors first.\n")
        for err in payload["errors"]:
            sys.stderr.write(f"  - {err}\n")
        return None

    block = (payload.get("data") or {}).get("mutation_testing") or {}
    score_break = float(block.get("score_break", 60))
    summary_rel = (block.get("report_paths") or {}).get(
        "summary_md"
    ) or "reports/mutation/summary.md"
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
    if reachable == 0:
        # THE PROPERTY, not a third special case. `reachable` is killed + survived --
        # the mutants that actually produced a verdict. At zero, no score exists, so
        # every status below would assert a measurement that never happened: the same
        # defect as the baseline-abort path, reached by a different route (all mutants
        # skipped or ignored, an empty dump, a Stryker config that excludes the whole
        # operator set). A fresh-eye round found these while the baseline-abort fix
        # was being reviewed, which is why this is stated as one condition over the
        # denominator rather than as two more patched call sites.
        #
        # `passed` stays False, so the exit code and CI redness are unchanged. This
        # renames an unearned verdict; it does not forgive one.
        #
        # The RULE lives in `verdict_token`, which the JS slice calls too -- one owner,
        # because the first cut wrote it once per engine and the duplicate ratchet
        # flagged the pair immediately.
        passed = False
        status = verdict_token(reachable, passed)
    elif exec_timed_out:
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
        # Through the shared owner, not a fourth inline ternary. A round-2 review
        # noted that the "one owner" claim above was overstated while this line still
        # spelled the rule fifteen lines from the call that was supposed to centralize
        # it. `reachable` is non-zero on this arm, so the UNMEASURED case cannot fire.
        status = verdict_token(reachable, passed)
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
        module_path = (
            str((mutations[0] or {}).get("module_path") or "<unknown>")
            if mutations
            else "<unknown>"
        )
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
            incomplete.append(f"{module_path} {executed}/{executable_total} ({ratio * 100:.1f}%)")
    return not incomplete, incomplete


def _baseline_abort_summary_lines(marker: dict) -> list[str]:
    lines = [
        "# Mutation Testing Summary",
        "",
        # NOT `FAIL`. `FAIL` is the verdict of a mutation run that RAN and scored
        # below the threshold; this path ran no mutants at all, so `FAIL` here
        # asserts a measurement that never happened. The two were one token from
        # 2026-08-19 to 2026-08-22: every scheduled run aborted on a red baseline
        # and published a "Mutation test regression" whose summary said FAIL, so
        # four days of "the mutation score broke" were really "nothing was
        # measured". The exit code is unchanged -- an unmeasured surface is still
        # a red workflow -- but the word no longer claims a score it never read.
        f"- Status: **{UNMEASURED_STATUS}**",
        # Same stage vocabulary as the JS slice, from the same owner. The old wording
        # said "before mutation sampling", which is only true of the sampler stage.
        f"- Blocking signal: {baseline_abort_cause(marker)} before mutation ran; no mutants ran.",
    ]
    failing_nodeids = marker.get("failing_nodeids") or []
    if failing_nodeids:
        lines.append("- Failing baseline tests:")
        lines.extend(f"  - `{nodeid}`" for nodeid in failing_nodeids)
    else:
        lines.extend(["", "```", *(marker.get("log_tail") or []), "```"])
    return lines


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


def _marker_is_stale(marker_path: Path, stats_path: Path) -> bool:
    """Return True when `stats_path` is strictly fresher than `marker_path`.

    Locally `reports/mutation/` persists across runs, so an abort marker left
    over from an earlier aborted attempt must not mask the results of a
    newer mutation run that produced a fresher stats file. A same-mtime tie
    keeps the marker authoritative: on a coarse-granularity filesystem a
    persisted previous-run stats file must not mask a genuine current abort.
    """
    if not stats_path.is_file():
        return False
    return stats_path.stat().st_mtime > marker_path.stat().st_mtime


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    stats_path = args.stats if args.stats.is_absolute() else (repo_root / args.stats)
    baseline_abort_marker_path = resolve_baseline_abort_marker(
        repo_root, args.baseline_abort_marker
    )
    marker = read_baseline_abort_marker(baseline_abort_marker_path)
    if marker is not None and not _marker_is_stale(baseline_abort_marker_path, stats_path):
        config = load_mutation_config(repo_root)
        if config is not None:
            _score_break, summary_path = config
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(
                "\n".join(_baseline_abort_summary_lines(marker)) + "\n", encoding="utf-8"
            )
            # Rendered from the marker, like the summary line. Hardcoded here it said
            # "before mutation sampling" for BOTH stages -- and this stream is tee'd
            # into run.log, which the workflow now attaches to the issue, so the fixed
            # sentence would have been republished by the slice's own new channel.
            sys.stderr.write(
                f"{baseline_abort_cause(marker)} before mutation ran; "
                "see summary for failing nodeids.\n"
            )
            return 2

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
        args.timeout_marker
        if args.timeout_marker.is_absolute()
        else repo_root / args.timeout_marker
    )
    sample_manifest_path = (
        args.sample_manifest
        if args.sample_manifest.is_absolute()
        else repo_root / args.sample_manifest
    )
    exec_timed_out, _ = _read_timeout_marker(timeout_marker_path)
    per_file_completion_ok, incomplete_files = mutation_file_completion(records)
    changed_scope_gap_files, changed_scope_gap_details, sample_manifest_issue = (
        sample_manifest_scope_gap_details(sample_manifest_path)
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
    if changed_scope_gap_files or changed_scope_gap_details:
        try:
            insert_at = lines.index(
                "Score denominator: `killed / (killed + survived)` (reachable mutants only;"
            )
        except ValueError:
            insert_at = len(lines)
        lines[insert_at:insert_at] = changed_scope_gap_section_lines(
            changed_scope_gap_files,
            changed_scope_gap_details,
        )
    if incomplete_files:
        try:
            insert_at = lines.index(
                "Score denominator: `killed / (killed + survived)` (reachable mutants only;"
            )
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
