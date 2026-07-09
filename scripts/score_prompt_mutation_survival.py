#!/usr/bin/env python3
"""S3 deterministic survival scorer for the prompt-mutation-pilot goal
(charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md).

Reads a `run_skill_efficiency_ab.py` output dir (`--ab-dir`: `results.json` +
`preserved/<arm>__<i>/` bundles), a skill's checked-in witness map
(`--witness-map`), and a `generate_prompt_mutants.py generate` manifest
(`--mutant-manifest`: unit_id -> snapshot SHA), and scores each mutant arm's
unit DETECTED / NO-OBSERVED-EFFECT / INVALID-FOR-VERDICT from deterministic
witnesses only (required_command_fragment / required_summary_fragment /
trace_command_marker -- never a cautilus judge channel, per the goal's
Boundaries). Refuses (`EXPERIMENT-INVALID`, nonzero exit) with NO mutant
verdicts if any mutant unit's witness did not fire in every baseline run. See
score_prompt_mutation_survival_lib.py for the scoring rules; this module is
CLI wiring only. Advisory tooling -- never a commit/CI gate.

Arm mapping (`--arm NAME=VALUE`, repeated): NAME must match an arm name in
`--ab-dir`'s results.json; VALUE is either the literal `BASELINE` (exactly
one arm must carry it) or a `unit_id` exactly as minted by
`generate_prompt_mutants.py generate`'s manifest. Example:
  --arm baseline=BASELINE --arm m1=plugins/charness/skills/x/SKILL.md#a@0123456789
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from score_prompt_mutation_survival_lib import (
    SurvivalScorerError,
    parse_arm_specs,
    render_markdown,
    score_survival,
)

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def _resolve(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic survival scorer for prompt-mutation-pilot arms (S3). Advisory tooling; "
            "never a commit/CI gate."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--ab-dir", type=Path, required=True, help="run_skill_efficiency_ab.py output dir.")
    parser.add_argument("--witness-map", type=Path, required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument(
        "--mutant-manifest", type=Path, required=True, help="generate_prompt_mutants.py generate's manifest JSON."
    )
    parser.add_argument(
        "--arm",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Repeatable. NAME is an arm in --ab-dir's results.json; VALUE is 'BASELINE' (exactly one "
        "arm) or a unit_id from --mutant-manifest.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Present for CLI-shape compatibility; output is JSON unless --markdown."
    )
    parser.add_argument("--markdown", action="store_true", help="Print a human-readable report instead of JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    try:
        arm_specs = parse_arm_specs(args.arm)
        report = score_survival(
            _resolve(repo_root, args.ab_dir),
            _resolve(repo_root, args.witness_map),
            args.scenario,
            _resolve(repo_root, args.mutant_manifest),
            arm_specs,
        )
    except SurvivalScorerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.markdown:
        print(render_markdown(report), end="")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if not report["experiment_valid"]:
        print("score_prompt_mutation_survival: EXPERIMENT-INVALID -- see experiment_invalid_reasons", file=sys.stderr)
        return 1
    if not report.get("sentinels", {}).get("all_fired", True):
        print("score_prompt_mutation_survival: SENTINEL-FAILURE -- see sentinels.failures", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
