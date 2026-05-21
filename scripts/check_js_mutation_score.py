#!/usr/bin/env python3
"""Append StrykerJS mutation results to the repo mutation summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.quality_adapter_lib import load_quality_adapter  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--report-json", type=Path, default=Path("reports/mutation/stryker-js.json"))
    return parser.parse_args()


def mutation_config(repo_root: Path) -> tuple[float, Path] | None:
    payload = load_quality_adapter(repo_root)
    if payload.get("errors"):
        for error in payload["errors"]:
            sys.stderr.write(f"quality adapter error: {error}\n")
        return None
    block = (payload.get("data") or {}).get("mutation_testing") or {}
    score_break = float(block.get("score_break", 60))
    summary_rel = (block.get("report_paths") or {}).get("summary_md") or "reports/mutation/summary.md"
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


def append_summary(summary_path: Path, metrics: dict[str, object], score_break: float) -> None:
    counts = metrics["counts"]
    assert isinstance(counts, dict)
    passed = (
        float(metrics["score"]) >= score_break
        and int(metrics["reachable"]) > 0
        and int(counts.get("NoCoverage", 0)) == 0
        and int(counts.get("Timeout", 0)) == 0
    )
    lines = [
        "",
        "## StrykerJS Mutation Slice",
        "",
        f"- Status: **{'PASS' if passed else 'FAIL'}** "
        f"({float(metrics['score']):.1f}% reachable score vs {score_break:.0f}% threshold)",
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
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    existing = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
    summary_path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def append_missing_report_summary(summary_path: Path, report_path: Path) -> None:
    lines = [
        "",
        "## StrykerJS Mutation Slice",
        "",
        "- Status: **FAIL** (StrykerJS JSON report missing)",
        f"- Missing report: `{report_path}`",
        "- Blocking signal: JS mutation full mode did not produce a fresh JSON report.",
    ]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    existing = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
    summary_path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    config = mutation_config(repo_root)
    if config is None:
        return 2
    score_break, summary_path = config
    report_path = args.report_json if args.report_json.is_absolute() else repo_root / args.report_json
    if not report_path.is_file():
        append_missing_report_summary(summary_path, report_path)
        sys.stderr.write(f"StrykerJS report not found at {report_path}; failing JS mutation summary.\n")
        return 1
    metrics = summarize_report(report_path)
    append_summary(summary_path, metrics, score_break)
    sys.stdout.write(
        f"StrykerJS score: {float(metrics['score']):.1f}% threshold: {score_break:.0f}% "
        f"reachable: {metrics['reachable']}\n"
    )
    counts = metrics["counts"]
    assert isinstance(counts, dict)
    passed = (
        int(metrics["reachable"]) > 0
        and float(metrics["score"]) >= score_break
        and int(counts.get("NoCoverage", 0)) == 0
        and int(counts.get("Timeout", 0)) == 0
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
