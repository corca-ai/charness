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
import subprocess
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


def _git_lines(repo_root: Path, args: list[str]) -> list[str]:
    try:
        result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _head_resolves_to_head(repo_root: Path, head_sha: str) -> bool:
    if head_sha == "HEAD":
        return True
    resolved = _git_lines(repo_root, ["rev-parse", head_sha])
    head = _git_lines(repo_root, ["rev-parse", "HEAD"])
    return bool(resolved) and bool(head) and resolved[0] == head[0]


def uncommitted_pool_changes(repo_root: Path, eligible: set[str]) -> list[str]:
    """Eligible mutation-pool files with uncommitted worktree changes vs HEAD."""
    changed = set(_git_lines(repo_root, ["diff", "--name-only", "HEAD"]))
    changed.update(_git_lines(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(path for path in changed if path in eligible)


def contaminating_pool_changes(repo_root: Path, head_sha: str, eligible: set[str]) -> list[str]:
    """The single detector for "this run's inputs are contaminated".

    Non-empty exactly when the analyzed head resolves to ``HEAD`` *and* eligible
    mutation-pool files carry uncommitted worktree/index changes, i.e. when
    ``base..HEAD`` structurally cannot see them. Both the up-front refusal and the
    legacy late ``warning`` read this one function so they can never disagree.
    """
    if not _head_resolves_to_head(repo_root, head_sha):
        return []
    return uncommitted_pool_changes(repo_root, eligible)


def dirty_pool_refusal(uncommitted: list[str]) -> str:
    """Refuse-fast message for the contaminated-input case.

    The old behaviour emitted this as a ``warning`` only AFTER the ~10 minute
    coverage probe, so the wasted run was already paid for and a contaminated
    green read IDENTICALLY to a real green. Refusing at startup makes the cost
    ~0s and makes the contaminated state unrepresentable as a verdict.
    """
    return (
        f"REFUSING to run: {len(uncommitted)} mutation-pool file(s) have uncommitted "
        f"worktree/index changes that base..HEAD cannot see ({', '.join(uncommitted)}). "
        "A clean verdict would be a FALSE GREEN for them and is indistinguishable from a "
        "real green to the reader. Commit (or stash) those files and re-run, or pass "
        "--allow-dirty for an explicitly ADVISORY read that records itself as unverified."
    )


def _pin_run_state(repo_root: Path, base_sha: str, head_sha: str) -> dict[str, str]:
    """Snapshot what the whole run must stay anchored to.

    ``resolved_head_sha`` pins ``--head-sha HEAD`` to a concrete commit once, so a
    commit landing mid-run cannot re-resolve the range or shift the line mapping
    the ``blocking_detail`` numbers are computed against. ``head_commit`` and the
    changed-pool content fingerprint are the drift tripwires re-read at the end.
    """
    resolved = _git_lines(repo_root, ["rev-parse", head_sha])
    head_commit = _git_lines(repo_root, ["rev-parse", "HEAD"])
    try:
        fingerprint = changed_pool_fingerprint(repo_root, base_sha)
    except (subprocess.CalledProcessError, OSError):
        fingerprint = ""
    return {
        "resolved_head_sha": resolved[0] if resolved else head_sha,
        "head_commit": head_commit[0] if head_commit else "",
        "pool_fingerprint": fingerprint,
    }


def run_state_drift(repo_root: Path, base_sha: str, head_sha: str, pinned: dict[str, str]) -> str | None:
    """Re-read the pinned state at the end; describe any drift, else None.

    A commit (or a worktree edit to a changed pool file) landing WHILE the probe
    runs makes the coverage and the line mapping come from different trees — the
    reported line attributions look plausible and are wrong. There is no way to
    repair that after the fact, so the run reports "untrusted" instead of a verdict.
    """
    now = _pin_run_state(repo_root, base_sha, head_sha)
    drift = []
    if now["head_commit"] != pinned["head_commit"]:
        drift.append(
            f"HEAD moved {pinned['head_commit'][:12] or '<unknown>'} -> "
            f"{now['head_commit'][:12] or '<unknown>'} during the run"
        )
    if now["pool_fingerprint"] != pinned["pool_fingerprint"]:
        drift.append("mutation-pool worktree content changed during the run")
    return "; ".join(drift) if drift else None


def _mark_untrusted(report: dict, drift: str) -> dict:
    """A stale result must never render as ``ok: true``."""
    report["ok"] = False
    report["untrusted"] = True
    report["untrusted_reason"] = (
        f"{drift}: the coverage and the changed-line mapping no longer come from the same "
        "tree, so this run reports NO verdict. Re-run against a settled tree."
    )
    report["changed_line_proof"] = "untrusted"
    return report


def false_green_warning(repo_root: Path, head_sha: str, eligible: set[str]) -> str | None:
    """handoff-4 tripwire: warn when this run is a false-green dry-run.

    When the analyzed head resolves to ``HEAD`` and the worktree has uncommitted
    mutation-pool changes, the ``base..HEAD`` range EXCLUDES those changes — so a
    clean verdict is a false green for them (the exact trap recorded in
    ``charness-artifacts/retro/2026-06-07-producer-rerun-waste.md``: HEAD is the
    parent of the uncommitted changes, so they are judged only post-commit).
    Non-blocking — it warns; the verdict for the in-range lines stands. Since the
    refuse-fast change this is only reachable under ``--allow-dirty`` (the default
    path refuses at startup), and it shares ``contaminating_pool_changes`` with
    that refusal so the two can never disagree about what is contaminated.
    """
    uncommitted = contaminating_pool_changes(repo_root, head_sha, eligible)
    return false_green_message(uncommitted) if uncommitted else None


def false_green_message(uncommitted: list[str]) -> str:
    """The advisory (``--allow-dirty``) wording for an already-detected dirty pool."""
    return (
        f"analyzed head resolves to HEAD but {len(uncommitted)} mutation-pool file(s) have "
        f"uncommitted worktree changes excluded from base..HEAD ({', '.join(uncommitted)}); "
        "those changes are NOT analyzed, so a clean changed-line verdict is a FALSE GREEN for "
        "them. Commit them, then re-run, before trusting this result."
    )


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
    if not changed_before_coverage:
        return _finalize(_attach_warning({
            "ok": True,
            "blocking": [],
            **metadata,
            "reason": "no eligible mutation-pool files changed in this range",
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
