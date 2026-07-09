#!/usr/bin/env python3
"""Offline witness-coverage verdicts for a skill's prompt-mutation units (S2
of the prompt-mutation-pilot goal,
charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md).

Reads a checked-in witness map (`evals/cautilus/<skill>-claim-fidelity/
witness-map.json` by default), resolves its hash-less unit prefixes against
the LIVE unit manifest (worktree split, via `prompt_mutant_lib` -- same
discovery `generate_prompt_mutants.py split` uses), and reports a verdict per
live unit: WITNESSED (a deterministic + causally-rationalized witness),
UNTESTED (unmapped, judge-only, or authored untested/excluded), or EXCLUDED.
Static analysis only -- no network, no git mutation, read-only over the repo.
See witness_coverage_lib.py for the verdict logic; this module is CLI wiring
only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from witness_coverage_lib import WitnessCoverageError, compute_coverage, render_markdown

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Static witness-coverage verdicts for a skill's prompt-mutation units. Advisory tooling for the "
            "prompt-mutation-pilot goal; never a commit/CI gate."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument(
        "--witness-map",
        type=Path,
        default=None,
        help="Defaults to evals/cautilus/<skill>-claim-fidelity/witness-map.json.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Present for CLI-shape compatibility; output is JSON unless --markdown."
    )
    parser.add_argument("--markdown", action="store_true", help="Print a compact human-readable debt report instead of JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    try:
        report = compute_coverage(repo_root, args.skill, args.scenario, args.witness_map)
    except WitnessCoverageError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.markdown:
        print(render_markdown(report), end="")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if not report["ok"]:
        problems = []
        if report["stale_entries"]:
            problems.append(f"stale entries (no live unit match): {report['stale_entries']}")
        if report["ambiguous_entries"]:
            problems.append(
                "ambiguous entries (multiple live unit matches): "
                f"{[a['unit'] for a in report['ambiguous_entries']]}"
            )
        if report["spec_floor_errors"]:
            problems.append(
                "spec-floor errors (witness value absent from the spec's floors): "
                f"{[(e['unit'], e['channel'], e['value']) for e in report['spec_floor_errors']]}"
            )
        print("witness_coverage: FATAL -- " + "; ".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
