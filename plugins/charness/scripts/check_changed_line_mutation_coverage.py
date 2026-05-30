#!/usr/bin/env python3
"""Local pre-merge teeth for the #260 changed-line mutation-coverage class.

Reproduces ONLY the *blocking* signal of the scheduled mutation gate —
``mutation_changed_files_lib.classify_changed_line_scope_gap`` over a base..head
range — so uncovered changed lines are caught before merge instead of by the
≤3h cron. This is the recurring class (#219 -> #251 -> #260) and the only one
cheap to detect locally.

It is deliberately NOT a full local mutation runner and does NOT reproduce the
score path (survived-mutant ratio); that needs a real Cosmic Ray run and stays
CI-only. Reusing the gate's own ``classify_changed_line_scope_gap`` and the
sampler's ``list_eligible``/``list_changed`` keeps this faithful to the gate
rather than a parallel reimplementation that could drift.

Usage::

    # full faithful run (collects coverage via the gate's own probe — slow):
    MUTATION_BASE_SHA=<base> MUTATION_HEAD_SHA=<head> \\
        python3 scripts/check_changed_line_mutation_coverage.py --repo-root .

    # fast: reuse a coverage report you already produced this session:
    python3 scripts/check_changed_line_mutation_coverage.py --repo-root . \\
        --base-sha <base> --head-sha <head> --reuse-coverage

Exit 1 when any changed pool file has uncovered changed lines (the blocker);
exit 0 when clean or when there is no base SHA (the changed-line classifier is
non-blocking by construction without one — matching ``workflow_dispatch``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mutation_changed_files_lib import (  # noqa: E402
    changed_line_numbers,
    classify_changed_line_scope_gap,
)
from scripts.mutation_sampling_lib import (  # noqa: E402
    load_file_statement_lines,
    read_test_command,
    run_test_coverage,
)
from scripts.sample_mutation_files import list_changed, list_eligible  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproduce the mutation gate's blocking changed-line signal locally.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--base-sha", default=None, help="Base SHA; defaults to $MUTATION_BASE_SHA.")
    parser.add_argument("--head-sha", default=None, help="Head SHA; defaults to $MUTATION_HEAD_SHA, else HEAD.")
    parser.add_argument("--config", type=Path, default=Path("cosmic-ray.toml"))
    parser.add_argument("--coverage-json", type=Path, default=Path("reports/mutation/test-coverage.json"))
    parser.add_argument(
        "--reuse-coverage",
        action="store_true",
        help="Reuse an existing coverage JSON instead of running the (slow) gate probe.",
    )
    return parser.parse_args()


def _emit(report: dict) -> None:
    print(json.dumps(report, indent=2, sort_keys=True))


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    base_sha = (args.base_sha if args.base_sha is not None else os.environ.get("MUTATION_BASE_SHA") or "").strip() or None
    head_sha = (args.head_sha if args.head_sha is not None else os.environ.get("MUTATION_HEAD_SHA") or "").strip() or "HEAD"

    if not base_sha:
        _emit({
            "ok": True,
            "blocking": [],
            "reason": "no base_sha: the changed-line classifier is non-blocking by construction (matches workflow_dispatch, which computes no base_sha)",
        })
        return 0

    all_eligible = set(list_eligible(repo_root))
    changed_before_coverage = [p for p in list_changed(repo_root, base_sha, head_sha) if p in all_eligible]
    if not changed_before_coverage:
        _emit({
            "ok": True,
            "blocking": [],
            "base_sha": base_sha,
            "head_sha": head_sha,
            "reason": "no eligible mutation-pool files changed in this range",
        })
        return 0

    coverage_json = args.coverage_json if args.coverage_json.is_absolute() else repo_root / args.coverage_json
    if not args.reuse_coverage or not coverage_json.is_file():
        config = args.config if args.config.is_absolute() else repo_root / args.config
        run_test_coverage(repo_root, read_test_command(config), coverage_json)
    statement_lines = load_file_statement_lines(repo_root, coverage_json)

    blocking = classify_changed_line_scope_gap(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed_before_coverage,
        statement_lines=statement_lines,
        coverage_enabled=True,
    )

    blocking_detail: dict[str, object] = {}
    for path in blocking:
        changed = changed_line_numbers(repo_root, base_sha, head_sha, path)
        if path not in statement_lines:
            blocking_detail[path] = "file not tracked by the test suite (subprocess-only or untested) -> covers as 0%"
        else:
            _executed, missing = statement_lines[path]
            blocking_detail[path] = {"changed_and_missing": sorted(changed & missing)}

    _emit({
        "ok": not blocking,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "changed_pool_files": changed_before_coverage,
        "blocking": blocking,
        "blocking_detail": blocking_detail,
    })
    if blocking:
        sys.stderr.write(
            f"\n{len(blocking)} changed file(s) have uncovered changed lines; the mutation gate "
            "drops them before mutation (the #260 blocking signal). Cover the listed lines before merge.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
