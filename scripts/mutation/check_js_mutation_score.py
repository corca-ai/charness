#!/usr/bin/env python3
"""Append StrykerJS mutation results to the repo mutation summary."""

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

from scripts.adapters.quality_adapter_lib import load_quality_adapter  # noqa: E402
from scripts.mutation.mutation_baseline_abort_lib import (  # noqa: E402
    DEFAULT_BASELINE_ABORT_MARKER,
    UNMEASURED_STATUS,
    baseline_abort_cause,
    read_baseline_abort_marker,
    resolve_baseline_abort_marker,
    verdict_token,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--report-json", type=Path, default=Path("reports/mutation/stryker-js.json")
    )
    parser.add_argument(
        "--baseline-abort-marker",
        type=Path,
        default=DEFAULT_BASELINE_ABORT_MARKER,
        help="Path to the coverage-baseline abort marker emitted by sample_mutation_files.py.",
    )
    return parser.parse_args()


def mutation_config(repo_root: Path) -> tuple[float, Path] | None:
    payload = load_quality_adapter(repo_root)
    if payload.get("errors"):
        for error in payload["errors"]:
            sys.stderr.write(f"quality adapter error: {error}\n")
        return None
    block = (payload.get("data") or {}).get("mutation_testing") or {}
    score_break = float(block.get("score_break", 60))
    summary_rel = (block.get("report_paths") or {}).get(
        "summary_md"
    ) or "reports/mutation/summary.md"
    return score_break, repo_root / summary_rel


def summarize_report(report_path: Path) -> dict[str, object]:
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    files = payload.get("files") or {}
    counts = {"Killed": 0, "Survived": 0, "NoCoverage": 0, "Timeout": 0, "Ignored": 0, "Other": 0}
    locations: list[str] = []
    for path, file_payload in files.items():
        if not isinstance(file_payload, dict):
            continue
        for mutant in file_payload.get("mutants") or []:
            if not isinstance(mutant, dict):
                continue
            status = str(mutant.get("status") or "Other")
            counts[status if status in counts else "Other"] += 1
            if status == "Survived" and len(locations) < 10:
                location = mutant.get("location") or {}
                start = location.get("start") if isinstance(location, dict) else None
                line = start.get("line") if isinstance(start, dict) else None
                mutator = mutant.get("mutatorName") or "<unknown>"
                locations.append(f"{path}:{line or '?'} `{mutator}`")
    killed = counts["Killed"]
    survived = counts["Survived"]
    reachable = killed + survived
    score = (killed / reachable * 100.0) if reachable else 0.0
    return {
        "counts": counts,
        "reachable": reachable,
        "score": score,
        "survived_locations": locations,
    }


def js_slice_passed(metrics: dict[str, object], score_break: float) -> bool:
    """Whether the JS slice earned a pass. ONE owner, for the renderer and the exit code.

    These four conjuncts were written twice -- here for the rendered status token and
    again in `main()` for the process exit code -- in two different orders, so they
    were byte-different and no duplicate detector would ever have flagged them. Adding
    a fifth blocking condition to one would have rendered `PASS` while the script
    exited 1, or the reverse: a summary that contradicts the verdict it ships with.
    Found by a round-2 review of this slice, in the very file whose other helper was
    justified as giving a verdict rule one owner.
    """
    counts = metrics["counts"]
    assert isinstance(counts, dict)
    return (
        int(metrics["reachable"]) > 0
        and float(metrics["score"]) >= score_break
        and int(counts.get("NoCoverage", 0)) == 0
        and int(counts.get("Timeout", 0)) == 0
    )


def append_summary(summary_path: Path, metrics: dict[str, object], score_break: float) -> None:
    counts = metrics["counts"]
    assert isinstance(counts, dict)
    passed = js_slice_passed(metrics, score_break)
    lines = [
        "",
        "## StrykerJS Mutation Slice",
        "",
        # Same rule as the cosmic-ray slice, from the same owner: with no reachable
        # mutant there is no score, so neither PASS nor FAIL is earned. Reached when
        # every JS mutant is Ignored -- a `Stryker disable all` in the mutated files,
        # or an `excludedMutations` config covering the operator set.
        # The parenthetical carries the same obligation as the token: with no
        # denominator, `0.0%` is a fallback rather than a measurement, and printing it
        # against a threshold re-asserts the scoring claim the token just withdrew.
        # Round 1 fixed the token here and left this half; round 2 caught it.
        f"- Status: **{verdict_token(int(metrics['reachable']), passed)}** "
        + (
            f"({float(metrics['score']):.1f}% reachable score vs {score_break:.0f}% threshold)"
            if int(metrics["reachable"])
            else "(no reachable JS mutant produced a verdict; no score was computed)"
        ),
        f"- Reachable mutants: {metrics['reachable']}",
        f"- Killed: {counts.get('Killed', 0)}",
        f"- Survived: {counts.get('Survived', 0)}",
        f"- No coverage: {counts.get('NoCoverage', 0)}",
        f"- Timeout: {counts.get('Timeout', 0)}",
    ]
    locations = metrics.get("survived_locations") or []
    if counts.get("NoCoverage", 0):
        lines.append("- Blocking signal: JS mutants had no coverage in the command-runner slice.")
    if counts.get("Timeout", 0):
        lines.append("- Blocking signal: JS mutation execution timed out for at least one mutant.")
    if locations:
        lines.extend(["", "Survived JS mutants:", *[f"- `{item}`" for item in locations]])
    _append_summary_section(summary_path, lines)


def _append_summary_section(summary_path: Path, lines: list[str]) -> None:
    """Append one rendered section to the shared mutation summary file.

    Extracted from the two `append_*_summary` writers, which held byte-identical
    copies of this block. The duplicate ratchet surfaced the pair when an unrelated
    comment shifted them into one detector window, and its offered remedies were to
    remove the duplication or to add a family entry to `dup-review.json`. The list
    entry would have recorded the copies rather than removing them.
    """
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    existing = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
    summary_path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def append_missing_report_summary(
    summary_path: Path, report_path: Path, *, baseline_abort_marker: dict | None = None
) -> None:
    lines = [
        "",
        "## StrykerJS Mutation Slice",
        "",
        # `UNMEASURED`, not `FAIL`, for the same reason as the cosmic-ray slice in
        # check_mutation_score.py: a missing report means no JS mutant was scored,
        # which is a different claim from a JS slice that ran and scored badly.
        # The measured JS verdicts above still render PASS/FAIL.
        f"- Status: **{UNMEASURED_STATUS}** (StrykerJS JSON report missing)",
        f"- Missing report: `{report_path}`",
    ]
    if baseline_abort_marker is not None:
        # Rendered by the lib, not restated here: this sentence used to name the
        # sampler unconditionally, which was false for every abort that happened
        # anywhere else -- and the abort that actually recurs is the other one (#590).
        lines.append(
            f"- Blocking signal: collateral — {baseline_abort_cause(baseline_abort_marker)}, "
            "so the JS slice was never invoked (see Mutation Testing Summary above)."
        )
    else:
        lines.append(
            "- Blocking signal: JS mutation full mode did not produce a fresh JSON report."
        )
    _append_summary_section(summary_path, lines)


def _marker_is_stale(marker_path: Path, repo_root: Path) -> bool:
    """True when this run's own mutation artifacts are strictly fresher than the marker.

    Mirrors `check_mutation_score._marker_is_stale`, against the artifacts THIS slice
    can see: the cosmic-ray dump proves the Python side ran past its baseline, so a
    marker older than it belongs to a previous attempt. A same-mtime tie keeps the
    marker authoritative, because on a coarse filesystem a persisted previous-run
    artifact must not mask a genuine current abort.
    """
    try:
        marker_mtime = marker_path.stat().st_mtime
    except OSError:
        # A concurrent run may delete the marker between the read that proved it
        # existed and this stat. Absent means nothing to age out, and a report must
        # not become a traceback over a race.
        return False
    for rel in ("reports/mutation/cosmic-ray-dump.jsonl", "reports/mutation/test-coverage.json"):
        candidate = repo_root / rel
        if candidate.is_file() and candidate.stat().st_mtime > marker_mtime:
            return True
    return False


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    config = mutation_config(repo_root)
    if config is None:
        return 2
    score_break, summary_path = config
    report_path = (
        args.report_json if args.report_json.is_absolute() else repo_root / args.report_json
    )
    if not report_path.is_file():
        baseline_abort_marker_path = resolve_baseline_abort_marker(
            repo_root, args.baseline_abort_marker
        )
        marker = read_baseline_abort_marker(baseline_abort_marker_path)
        if marker is not None and _marker_is_stale(baseline_abort_marker_path, repo_root):
            # A marker older than this run's own mutation artifacts describes an
            # EARLIER attempt. Without this, a real JS failure (stryker crashed, node
            # deps missing) after a since-repaired baseline reads as "collateral --
            # the baseline failed, so the JS slice was never invoked", which tells the
            # reader to stop looking at the thing that actually broke.
            marker = None
        append_missing_report_summary(summary_path, report_path, baseline_abort_marker=marker)
        sys.stderr.write(
            f"StrykerJS report not found at {report_path}; failing JS mutation summary.\n"
        )
        return 1
    metrics = summarize_report(report_path)
    append_summary(summary_path, metrics, score_break)
    sys.stdout.write(
        f"StrykerJS score: {float(metrics['score']):.1f}% threshold: {score_break:.0f}% "
        f"reachable: {metrics['reachable']}\n"
    )
    return 0 if js_slice_passed(metrics, score_break) else 1


if __name__ == "__main__":
    raise SystemExit(main())
