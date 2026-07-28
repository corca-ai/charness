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
Exit 2 when the run is REFUSED up front (contaminated inputs) or when its result
is UNTRUSTED because the repo moved mid-run — both are "no verdict", not a
verdict; see ``dirty_pool_refusal`` and ``run_state_drift``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

#: Exit code for "no verdict was produced" — a startup refusal (contaminated
#: inputs) or an untrusted result (the repo moved mid-run). Deliberately distinct
#: from 1 (a real changed-line blocker) so callers can tell "I refused to judge"
#: from "I judged and it failed".
REFUSED_EXIT = 2

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.changed_line_run_trust import (  # noqa: E402
    _git_lines,
    _head_resolves_to_head,
    _mark_untrusted,
    _pin_run_state,
    contaminating_pool_changes,
    dirty_pool_refusal,
    false_green_message,
    false_green_warning,
    run_state_drift,
    uncommitted_pool_changes,
)
from scripts.mutation_changed_files_lib import (  # noqa: E402
    changed_line_numbers,
    changed_line_scope_gap_targets,
    changed_pool_fingerprint,
    classify_changed_line_scope_gap,
    coverage_fingerprint_marker_path,
    write_coverage_fingerprint_marker,
)
from scripts.mutation_sampling_lib import (  # noqa: E402
    load_file_statement_lines,
    read_test_command,
    run_test_coverage,
)
from scripts.sample_mutation_files import list_changed, list_eligible  # noqa: E402

#: Re-export surface. These names moved to `changed_line_run_trust` when this file
#: outgrew the length cap, but callers outside it — `mutation_coverage_producer` and
#: four test modules — still reference them HERE. Naming them keeps the move
#: behavior-preserving for those callers AND keeps a linter from reading the imports as
#: unused: `ruff --fix` deleted them once and took eight tests with it.
__all__ = [
    "_git_lines",
    "_head_resolves_to_head",
    "_mark_untrusted",
    "_pin_run_state",
    "contaminating_pool_changes",
    "dirty_pool_refusal",
    "false_green_message",
    "false_green_warning",
    "run_state_drift",
    "uncommitted_pool_changes",
]


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
            "Only trust a coverage JSON whose sibling marker `<coverage-json>.fingerprint` "
            "matches the current changed-pool content fingerprint; otherwise skip "
            "non-blocking. The pre-push wiring sets this so a STALE coverage source "
            "(produced before the changed lines existed) cannot raise false 'uncovered "
            "changed line' positives. The closeout producer writes the marker when it "
            "refreshes coverage."
        ),
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help=(
            "Escape hatch: proceed even when mutation-pool files have uncommitted "
            "worktree/index changes that base..HEAD cannot see. The run then costs the "
            "full probe and its verdict is ADVISORY ONLY — the payload records "
            "`dirty_pool_unverified: true` plus the offending files, so a clean result "
            "cannot be cited as changed-line proof for them."
        ),
    )
    parser.add_argument(
        "--limit-to-file",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Repo-relative mutation-pool path to analyze; repeatable. Narrows the "
            "BLOCKING set to these files only. The incremental pre-push producer sets "
            "this because its coverage was collected from a focused test subset: focused "
            "coverage is a SUBSET of full coverage, so an unmapped file's changed lines "
            "would read as uncovered when the full suite covers them. Every changed pool "
            "file outside the limit is reported as `unanalyzed_changed_pool_files` and "
            "named on stderr, so a clean verdict here can never be read as covering them."
        ),
    )
    parser.add_argument(
        "--write-fresh-marker",
        action="store_true",
        help=(
            "Producer mode: after coverage exists for the analyzed range, write the "
            "sibling `<coverage-json>.fingerprint` marker recording the changed-pool "
            "content fingerprint so the pre-push consumer (`--require-fresh-coverage`) "
            "can trust the coverage. Uses a plain (no dynamic_context) probe so the "
            "coverage JSON stays small."
        ),
    )
    return parser.parse_args()


def _emit(report: dict) -> None:
    print(json.dumps(report, indent=2, sort_keys=True))


def _attach_warning(report: dict, warning: str | None) -> dict:
    if warning:
        report["warning"] = warning
    return report


def _coverage_source_skip(args, repo_root: Path, coverage_json: Path, base_sha: str, head_sha: str) -> dict | None:
    """Return a non-blocking skip report when the coverage source cannot be
    trusted for a cheap pre-push verdict, else None.

    Two guards keep the pre-push (read-only) wiring both cheap and safe:
    - ``--require-fresh-coverage``: a coverage JSON whose sibling ``.fingerprint``
      marker does not match the current changed-pool content fingerprint is STALE
      (it may predate the changed lines), so trusting it would raise false
      positives; skip instead. The fingerprint is content-based and computed over
      base→worktree, so it stays valid across the producer's pre-commit run and
      the consumer's post-commit (pre-push) check of the same code.
    - ``--skip-if-no-coverage``: no coverage JSON at all; skip rather than fall
      through to the slow probe.
    """
    base = {"ok": True, "blocking": [], "base_sha": base_sha, "head_sha": head_sha}
    if args.require_fresh_coverage and coverage_json.is_file():
        marker = coverage_fingerprint_marker_path(coverage_json)
        recorded = marker.read_text(encoding="utf-8").strip() if marker.is_file() else None
        current = changed_pool_fingerprint(repo_root, base_sha)
        if recorded is None or recorded != current:
            return {**base, "reason": (
                f"coverage source is stale: fingerprint marker {recorded or 'absent'} != current "
                f"{current}; changed-line teeth skipped (non-blocking). "
                "Re-run the closeout producer to refresh coverage for this range."
            )}
    if args.skip_if_no_coverage and not coverage_json.is_file():
        return {**base, "reason": (
            f"no coverage source at {args.coverage_json}: changed-line teeth skipped "
            "(non-blocking). Coverage is produced by the full/closeout run and reused here."
        )}
    return None


def _ensure_coverage(args, repo_root: Path, coverage_json: Path, base_sha: str) -> None:
    """Produce coverage when needed, and in producer mode stamp the
    `.fingerprint` marker so the pre-push consumer's `--require-fresh-coverage`
    can trust the coverage was built for this changed-pool content. Skip guards
    run before this, so here a missing/stale reuse target means "run the probe".

    The producer probe drops `dynamic_context` (lever A): the changed-line
    verdict only needs executed-vs-missing lines, and per-test context is what
    blew the coverage JSON up to ~1.34 GB. Subprocess capture is retained."""
    if not args.reuse_coverage or not coverage_json.is_file():
        config = args.config if args.config.is_absolute() else repo_root / args.config
        run_test_coverage(
            repo_root, read_test_command(config), coverage_json,
            dynamic_context=not args.write_fresh_marker,
        )
    if args.write_fresh_marker:
        write_coverage_fingerprint_marker(repo_root, coverage_json, base_sha)


def coverage_not_verified_warning(changed_eligible: list[str], reason: str) -> str:
    """Recurrence tripwire (#335): the gate is SKIPPING the changed-line check while
    eligible mutation-pool files actually changed in this range.

    The #219 -> #251 -> #260 -> #320 -> #321 -> #335 seam recurs because a silent
    skip (no/stale coverage) reads IDENTICALLY to a clean pass: the author's
    pre-push attestation goes green, the uncovered changed lines reach ``main``, and
    only the scheduled cron — which accumulates everything since its last run — flags
    them post-merge and auto-files. Making the unverified skip LOUD at author time is
    the structural reduction: the obligation becomes visible before the change lands.
    Non-blocking by design (it names the fix; it does not change the verdict).
    """
    files = ", ".join(changed_eligible)
    return (
        f"{len(changed_eligible)} eligible mutation-pool file(s) changed but their "
        f"changed lines were NOT verified for coverage ({reason.rstrip('.')}). An "
        "unverified skip reads as a clean pass, so uncovered changed lines reach main "
        "and the next scheduled mutation run flags them (the #335 recurrence). First run "
        "`python3 scripts/suggest_mutation_coverage_command.py --repo-root . --detail` "
        "to find a focused producer command; if it cannot map the change, run "
        "`python3 scripts/run_slice_closeout.py --produce-mutation-coverage "
        "--verification-lock` as the full fallback before the lines land. "
        f"Files: {files}"
    )


def _surface_skip(skip: dict, changed_before_coverage: list[str]) -> dict:
    """Annotate a non-blocking skip and surface the #335 recurrence obligation loudly.

    The skip path is only reached with a non-empty ``changed_before_coverage`` (the
    empty case returns earlier), so a skip ALWAYS means "eligible files changed but
    went unverified" — the recurrence driver. Write the obligation to stderr and
    record it structurally; the verdict itself stays unchanged (exit 0)."""
    not_verified = coverage_not_verified_warning(changed_before_coverage, str(skip.get("reason", "coverage unavailable")))
    sys.stderr.write(f"WARNING (changed-line mutation gate): {not_verified}\n")
    skip["coverage_not_verified"] = True
    skip["changed_eligible_files"] = changed_before_coverage
    return skip


def _apply_file_limit(args, changed_before_coverage: list[str]) -> tuple[list[str], list[str]]:
    """Split the changed pool set into (analyzed, unanalyzed) per ``--limit-to-file``.

    An EMPTY limit means "analyze everything", not "analyze nothing" — the flag is
    absent on every existing caller and its absence must not silently empty the
    blocking set. A limit naming a path that did not change in this range is not an
    error: the caller derives its list from a mapping that may be broader than the
    range, and intersecting is the honest read.
    """
    limit = [str(path).strip() for path in (getattr(args, "limit_to_file", None) or []) if str(path).strip()]
    if not limit:
        return changed_before_coverage, []
    allowed = set(limit)
    analyzed = [path for path in changed_before_coverage if path in allowed]
    unanalyzed = [path for path in changed_before_coverage if path not in allowed]
    return analyzed, unanalyzed


def _emit_no_base_sha() -> int:
    """No-base-sha verdict, made loud (#358): the exit stays 0 (matching the gate,
    whose changed-line classifier is inert without a range), but the payload now
    carries a machine-readable `changed_line_proof` bit and stderr names the
    `mutation-dispatch-no-base-sha-false-proof` class, so an `ok: true` here can
    no longer be read as changed-line proof. Claim-time refusal is owned by
    `scripts/check_mutation_run_proof.py`."""
    sys.stderr.write(
        "WARNING (changed-line mutation gate): no base_sha, so this verdict proves NOTHING "
        "about changed-line coverage (the mutation-dispatch-no-base-sha-false-proof class). "
        "Before citing a run as changed-line proof, run "
        "`python3 scripts/check_mutation_run_proof.py --claim changed-line ...`.\n"
    )
    _emit({
        "ok": True,
        "blocking": [],
        "changed_line_proof": "not-provable",
        "reason": "no base_sha: the changed-line classifier is non-blocking by construction (matches workflow_dispatch, which computes no base_sha)",
    })
    return 0


def _emit_dirty_refusal(uncommitted: list[str], metadata: dict) -> int:
    """Startup refusal — emitted BEFORE any coverage/probe work."""
    message = dirty_pool_refusal(uncommitted)
    sys.stderr.write(f"ERROR (changed-line mutation gate): {message}\n")
    _emit({
        "ok": False,
        "blocking": [],
        "refused": True,
        "reason": message,
        **metadata,
        "changed_line_proof": "refused",
    })
    return REFUSED_EXIT


def _run_metadata(base_sha: str, head_sha: str, pinned: dict[str, str], contaminated: list[str]) -> dict:
    """Additive payload metadata shared by every verdict this run can emit."""
    metadata: dict[str, object] = {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "resolved_head_sha": pinned["resolved_head_sha"],
    }
    if contaminated:
        metadata["dirty_pool_unverified"] = True
        metadata["uncommitted_pool_files"] = contaminated
        metadata["changed_line_proof"] = "unverified-dirty-worktree"
    return metadata


def _finalize(report: dict, repo_root: Path, base_sha: str, head_sha: str, pinned: dict, exit_code: int) -> int:
    """Emit the report, downgrading it to UNTRUSTED when the repo moved mid-run."""
    drift = run_state_drift(repo_root, base_sha, head_sha, pinned)
    if drift:
        _mark_untrusted(report, drift)
        sys.stderr.write(f"ERROR (changed-line mutation gate): {report['untrusted_reason']}\n")
        _emit(report)
        return REFUSED_EXIT
    _emit(report)
    return exit_code


def _blocking_report(repo_root, args, base_sha, head_sha, changed_before_coverage, coverage_json) -> dict:
    """The authoritative changed-line verdict body for the analyzed (pinned) range."""
    _ensure_coverage(args, repo_root, coverage_json, base_sha)
    statement_lines = load_file_statement_lines(repo_root, coverage_json)
    scope = {
        "repo_root": repo_root,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "changed_before_coverage": changed_before_coverage,
        "statement_lines": statement_lines,
        "coverage_enabled": True,
    }
    blocking = classify_changed_line_scope_gap(**scope)
    blocking_targets = changed_line_scope_gap_targets(**scope)

    blocking_detail: dict[str, object] = {}
    for path in blocking:
        changed = changed_line_numbers(repo_root, base_sha, head_sha, path)
        if path not in statement_lines:
            blocking_detail[path] = "file not tracked by the test suite (subprocess-only or untested) -> covers as 0%"
        else:
            _executed, missing = statement_lines[path]
            blocking_detail[path] = {"changed_and_missing": sorted(changed & missing)}

    return {
        "ok": not blocking,
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
    }


def _write_blocking_stderr(blocking: list[str], blocking_targets: dict) -> None:
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


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    base_sha = (args.base_sha if args.base_sha is not None else os.environ.get("MUTATION_BASE_SHA") or "").strip() or None
    head_sha = (args.head_sha if args.head_sha is not None else os.environ.get("MUTATION_HEAD_SHA") or "").strip() or "HEAD"

    if not base_sha:
        return _emit_no_base_sha()

    # Startup preflight: detect contamination and pin the analyzed head BEFORE any
    # coverage/probe work, so a contaminated run costs ~0s instead of ~10 minutes
    # and a commit landing mid-run cannot re-resolve `HEAD` under the analysis.
    all_eligible = set(list_eligible(repo_root))
    contaminated = contaminating_pool_changes(repo_root, head_sha, all_eligible)
    pinned = _pin_run_state(repo_root, base_sha, head_sha)
    metadata = _run_metadata(base_sha, head_sha, pinned, contaminated)
    if contaminated and not args.allow_dirty:
        return _emit_dirty_refusal(contaminated, metadata)
    fg_warning = false_green_message(contaminated) if contaminated else None
    if fg_warning:
        sys.stderr.write(f"WARNING (changed-line mutation gate): {fg_warning}\n")
    analyzed_head = pinned["resolved_head_sha"]

    changed_before_coverage = [p for p in list_changed(repo_root, base_sha, analyzed_head) if p in all_eligible]
    changed_before_coverage, unanalyzed = _apply_file_limit(args, changed_before_coverage)
    if unanalyzed:
        metadata = {**metadata, "unanalyzed_changed_pool_files": unanalyzed}
        sys.stderr.write(
            "WARNING (changed-line mutation gate): this run analyzed only "
            f"{len(changed_before_coverage)} of {len(changed_before_coverage) + len(unanalyzed)} "
            "changed mutation-pool file(s). A clean verdict says NOTHING about the rest: "
            f"{', '.join(unanalyzed)}\n"
        )
    if not changed_before_coverage:
        # `unanalyzed` non-empty here means the LIMIT emptied the set, not the range.
        # Reporting "nothing changed" would be false, and false in the exact direction
        # this gate exists to refuse: a verdict rendered over a scope that was never read.
        reason = (
            "no eligible mutation-pool files changed in this range"
            if not unanalyzed
            else (
                f"every changed mutation-pool file ({len(unanalyzed)}) fell OUTSIDE "
                "--limit-to-file; this run analyzed nothing and proves nothing about them"
            )
        )
        return _finalize(_attach_warning({
            "ok": True,
            "blocking": [],
            **metadata,
            "reason": reason,
        }, fg_warning), repo_root, base_sha, head_sha, pinned, 0)

    coverage_json = args.coverage_json if args.coverage_json.is_absolute() else repo_root / args.coverage_json
    skip = _coverage_source_skip(args, repo_root, coverage_json, base_sha, head_sha)
    if skip is not None:
        skip = {**skip, **metadata}
        report = _attach_warning(_surface_skip(skip, changed_before_coverage), fg_warning)
        return _finalize(report, repo_root, base_sha, head_sha, pinned, 0)

    report = _blocking_report(
        repo_root, args, base_sha, analyzed_head, changed_before_coverage, coverage_json
    )
    blocking = list(report["blocking"])
    code = _finalize(
        _attach_warning({**report, **metadata}, fg_warning),
        repo_root, base_sha, head_sha, pinned, 1 if blocking else 0,
    )
    if blocking and code == 1:
        _write_blocking_stderr(blocking, report["blocking_targets"])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
