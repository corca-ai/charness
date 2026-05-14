#!/usr/bin/env python3
"""Compute mutation score from mutmut stats and gate on adapter score_break.

Reads `mutants/mutmut-cicd-stats.json` (mutmut 3.x `export-cicd-stats` output),
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--stats",
        type=Path,
        default=Path("mutants/mutmut-cicd-stats.json"),
        help="Path to mutmut export-cicd-stats output (default: mutants/mutmut-cicd-stats.json).",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    stats_path = args.stats if args.stats.is_absolute() else (repo_root / args.stats)
    if not stats_path.is_file():
        sys.stderr.write(
            f"mutation stats not found at {stats_path}. Run `mutmut export-cicd-stats` first.\n"
        )
        return 2

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
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

    killed = int(stats.get("killed", 0))
    survived = int(stats.get("survived", 0))
    no_tests = int(stats.get("no_tests", 0))
    suspicious = int(stats.get("suspicious", 0))
    timeout = int(stats.get("timeout", 0))
    total = int(stats.get("total", killed + survived + no_tests + suspicious + timeout))
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
    ]
    if suspicious:
        lines.append(f"- Suspicious: {suspicious}")
    if timeout:
        lines.append(f"- Timeout: {timeout}")
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
