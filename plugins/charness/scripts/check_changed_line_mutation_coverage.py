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
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mutation_changed_files_lib import (  # noqa: E402
    changed_line_numbers,
    changed_line_scope_gap_targets,
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
    parser.add_argument(
        "--skip-if-no-coverage",
        action="store_true",
        help=(
            "When no coverage JSON exists, skip non-blocking (exit 0) instead of "
            "running the slow probe. The pre-push (read-only) wiring uses this so the "
            "teeth stay cheap; the coverage source is produced by the full/closeout run "
            "and reused here."
        ),
    )
    parser.add_argument(
        "--require-fresh-coverage",
        action="store_true",
        help=(
            "Only trust a coverage JSON whose sibling marker `<coverage-json>.head` "
            "records the current head SHA; otherwise skip non-blocking. The pre-push "
            "wiring sets this so a STALE coverage source (produced for an older commit) "
            "cannot raise false 'uncovered changed line' positives. The closeout "
            "producer writes the marker when it refreshes coverage."
        ),
    )
    parser.add_argument(
        "--write-head-marker",
        action="store_true",
        help=(
            "Producer mode: after coverage exists for the analyzed head, write the "
            "sibling `<coverage-json>.head` marker recording that head SHA so the "
            "pre-push consumer (`--require-fresh-coverage`) can trust the coverage."
        ),
    )
    return parser.parse_args()


def _resolve_sha(repo_root: Path, ref: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", ref],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, OSError):
        return None
    return result.stdout.strip() or None


def _emit(report: dict) -> None:
    print(json.dumps(report, indent=2, sort_keys=True))


def _coverage_source_skip(args, repo_root: Path, coverage_json: Path, base_sha: str, head_sha: str) -> dict | None:
    """Return a non-blocking skip report when the coverage source cannot be
    trusted for a cheap pre-push verdict, else None.

    Two guards keep the pre-push (read-only) wiring both cheap and safe:
    - ``--require-fresh-coverage``: a coverage JSON whose sibling ``.head`` marker
      does not record the analyzed head is STALE (it may predate the changed
      lines), so trusting it would raise false positives; skip instead.
    - ``--skip-if-no-coverage``: no coverage JSON at all; skip rather than fall
      through to the slow probe.
    """
    base = {"ok": True, "blocking": [], "base_sha": base_sha, "head_sha": head_sha}
    if args.require_fresh_coverage and coverage_json.is_file():
        head_marker = coverage_json.with_name(coverage_json.name + ".head")
        recorded_head = head_marker.read_text(encoding="utf-8").strip() if head_marker.is_file() else None
        current_head = _resolve_sha(repo_root, head_sha)
        if recorded_head is None or current_head is None or recorded_head != current_head:
            return {**base, "reason": (
                f"coverage source is stale: marker {recorded_head or 'absent'} != head "
                f"{current_head or 'unresolved'}; changed-line teeth skipped (non-blocking). "
                "Re-run the closeout producer to refresh coverage for this head."
            )}
    if args.skip_if_no_coverage and not coverage_json.is_file():
        return {**base, "reason": (
            f"no coverage source at {args.coverage_json}: changed-line teeth skipped "
            "(non-blocking). Coverage is produced by the full/closeout run and reused here."
        )}
    return None


def _ensure_coverage(args, repo_root: Path, coverage_json: Path, head_sha: str) -> None:
    """Produce coverage when needed (the slow probe), and in producer mode stamp
    the `.head` marker so the pre-push consumer's `--require-fresh-coverage` can
    trust the coverage was built for this head. Skip guards run before this, so
    here a missing/stale reuse target means "run the probe"."""
    if not args.reuse_coverage or not coverage_json.is_file():
        config = args.config if args.config.is_absolute() else repo_root / args.config
        run_test_coverage(repo_root, read_test_command(config), coverage_json)
    if args.write_head_marker:
        resolved_head = _resolve_sha(repo_root, head_sha)
        if resolved_head:
            coverage_json.with_name(coverage_json.name + ".head").write_text(
                resolved_head + "\n", encoding="utf-8"
            )


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
    skip = _coverage_source_skip(args, repo_root, coverage_json, base_sha, head_sha)
    if skip is not None:
        _emit(skip)
        return 0
    _ensure_coverage(args, repo_root, coverage_json, head_sha)
    statement_lines = load_file_statement_lines(repo_root, coverage_json)

    blocking = classify_changed_line_scope_gap(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed_before_coverage,
        statement_lines=statement_lines,
        coverage_enabled=True,
    )
    blocking_targets = changed_line_scope_gap_targets(
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
        "blocking_targets": blocking_targets,
        "targeted_mutant_proof": {
            "required": bool(blocking),
            "contract": (
                "Before hand-mutating, cite/display one blocking_targets path:line "
                "entry, mutate that exact line, record the failing test, then revert."
            ),
        },
    })
    if blocking:
        missing_targets = sorted(set(blocking) - set(blocking_targets))
        if missing_targets:
            sys.stderr.write(
                "changed-line blocker could not produce exact proof targets for: "
                f"{', '.join(missing_targets)}\n"
            )
        sys.stderr.write(
            f"\n{len(blocking)} changed file(s) have uncovered changed lines; the mutation gate "
            "drops them before mutation (the #260 blocking signal). Use blocking_targets to bind "
            "manual mutant proof to the exact path:line before editing, then cover the listed lines "
            "before merge.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
