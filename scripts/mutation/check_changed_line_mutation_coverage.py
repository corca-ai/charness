#!/usr/bin/env python3
"""Release-boundary check for the #260 changed-line mutation-coverage class.

Reproduces ONLY the *blocking* signal of the scheduled mutation gate —
``mutation_changed_files_lib.classify_changed_line_scope_gap`` over a base..head
range — so uncovered changed lines are caught at the local release boundary or
by the scheduled CI run. This is the recurring class (#219 -> #251 -> #260)
and the only one cheap to detect locally.

It is deliberately NOT a full local mutation runner and does NOT reproduce the
score path (survived-mutant ratio); that needs a real Cosmic Ray run and stays
CI-only. Reusing the gate's own ``classify_changed_line_scope_gap`` and the
sampler's ``list_eligible``/``list_changed`` keeps this faithful to the gate
rather than a parallel reimplementation that could drift.

Usage::

    # full faithful run (collects coverage via the gate's own probe — slow):
    MUTATION_BASE_SHA=<base> MUTATION_HEAD_SHA=<head> \\
        python3 scripts/mutation/check_changed_line_mutation_coverage.py --repo-root .

    # fast: reuse a coverage report you already produced this session:
    python3 scripts/mutation/check_changed_line_mutation_coverage.py --repo-root . \\
        --base-sha <base> --head-sha <head> --reuse-coverage

Exit 1 when any changed pool file has uncovered changed lines (the blocker);
exit 0 when clean or when there is no base SHA (the changed-line classifier is
non-blocking by construction without one — matching ``workflow_dispatch``).
Exit 2 when the run is REFUSED up front (contaminated inputs) or when its result
is UNTRUSTED because the repo moved mid-run — both are "no verdict", not a
verdict; see ``dirty_pool_refusal`` and ``run_state_drift``.
Exit 3 when the run RAN and ESTABLISHED NOTHING about a non-empty changed set:
coverage was unavailable, ``--limit-to-file`` emptied the set, or the pool was
contaminated so a clean verdict describes a tree that is not this one. It is
non-blocking, like exit 0 was — but exit 0 made `run-quality.sh` print PASS
beside the payload that said nothing was proven, and that green is the class this
gate exists to refuse. An EMPTY changed set still exits 0: nothing was in scope,
which is honestly nothing to prove.
Exit 4 when the run RAN, judged everything it analyzed CLEAN, could not analyze
part of its changed set (``unanalyzed_changed_pool_files`` non-empty), AND no
stronger cause held -- a real uncovered changed line is still 1 and an
untrustworthy tree is still 3, because those are actionable and refusable where
this is neither. ``_verdict_exit_code`` is the whole rule; this sentence is a
summary of it and the function is what decides. The gate already printed "A clean
verdict says NOTHING about the rest" and then returned the byte it returns with
no blind spot at all; now the scope reaches the verdict. Deliberately non-blocking
for a mapper blind spot -- see ``PARTIAL_EXIT``.
"""

from __future__ import annotations

import os
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

from scripts.gates_support import changed_line_gate_cli as _cli  # noqa: E402
from scripts.gates_support.changed_line_resume_route import resume_fields  # noqa: E402
from scripts.gates_support.changed_line_run_trust import (  # noqa: E402
    INSPECTION_FAILED,
    SCOPE_MISMATCH,
    _git_lines,
    _head_resolves_to_head,
    _mark_untrusted,
    _pin_run_state,
    contaminating_pool_changes,
    dirty_pool_refusal,
    false_green_message,
    false_green_warning,
    probe_run_trust,
    run_state_drift,
    uncommitted_pool_changes,
)
from scripts.gates_support.changed_line_run_trust import (  # noqa: E402
    write_blocking_stderr as _write_blocking_stderr,
)
from scripts.gates_support.changed_line_scope_counts import (  # noqa: E402
    apply_file_limit as _apply_file_limit,
)
from scripts.gates_support.changed_line_scope_counts import scope_counts, scope_counts_not_computed  # noqa: E402
from scripts.gates_support.changed_line_verdict_codes import (  # noqa: E402
    PARTIAL_EXIT,
    REFUSED_EXIT,
    UNESTABLISHED_EXIT,
    _verdict_exit_code,
)
from scripts.worktree.checkout_view import GitCheckout  # noqa: E402
from scripts.mutation.mutation_changed_files_lib import (  # noqa: E402
    changed_line_coverage_marker_path,
    changed_pool_fingerprint,
    read_changed_line_coverage_marker,
    write_coverage_fingerprint_marker,
)
from scripts.mutation.mutation_changed_line_verdict import (  # noqa: E402
    blocking_details,
    changed_line_scope_verdict,
)
from scripts.mutation.mutation_sampling_lib import (  # noqa: E402
    coverage_is_context_bearing,
    load_file_statement_lines,
    read_test_command,
    run_test_coverage,
)
from scripts.mutation.sample_mutation_files import list_changed, list_eligible  # noqa: E402
from scripts.mutation.subprocess_only_coverage_advisory import (  # noqa: E402
    subprocess_coverage_advisory_report,
)
from scripts.yaml_output import emit_yaml  # noqa: E402

#: Re-export surface. These names moved to `changed_line_run_trust` when this file
#: outgrew the length cap, but callers outside it — `mutation_coverage_producer` and
#: four test modules — still reference them HERE. Naming them keeps the move
#: behavior-preserving for those callers AND keeps a linter from reading the imports as
#: unused: `ruff --fix` deleted them once and took eight tests with it.
__all__ = [
    "_apply_file_limit",
    "_git_lines",
    "_head_resolves_to_head",
    "_mark_untrusted",
    "_pin_run_state",
    "contaminating_pool_changes",
    "probe_run_trust",
    "dirty_pool_refusal",
    "false_green_message",
    "false_green_warning",
    "run_state_drift",
    "uncommitted_pool_changes",
]


#: The argument surface lives in `changed_line_gate_cli` (S6b-1, length cap).
#: Re-exported here because callers and four test modules bind it at THIS
#: address, exactly like the `__all__` block above.
parse_args = _cli.parse_args


def _emit(report: dict) -> None:
    emit_yaml(report)


def _attach_warning(report: dict, warning: str | None) -> dict:
    if warning:
        report["warning"] = warning
    return report


def _coverage_source_skip(
    args, repo_root: Path, coverage_json: Path, base_sha: str, head_sha: str
) -> dict | None:
    """Return a non-blocking skip report when the coverage source cannot be
    trusted for the release-boundary verdict, else None.

    Three guards keep the release wiring both cheap and safe:
    - a context-bearing corpus at the reuse path was written by the mutation
      sampler, not by this lane; skip rather than pay a multi-GB load for columns
      this verdict never reads. Decided from a 4 KB header read, and only on a
      definite ``true`` -- an unreadable header proceeds exactly as before.
    - ``--require-fresh-coverage``: a coverage JSON whose sibling
      ``.changed-line.fingerprint`` marker is not a changed-line producer marker
      matching the current changed-pool content fingerprint is STALE (it may
      predate the changed lines or belong to another producer), so trusting it
      would raise false positives; skip instead. The fingerprint is content-based
      and computed over base→worktree, so it stays valid across the producer's
      coverage run and the release consumer's check of the same code.
    - ``--skip-if-no-coverage``: no coverage JSON at all; skip rather than fall
      through to the slow probe.
    """
    base = {"ok": True, "blocking": [], "base_sha": base_sha, "head_sha": head_sha}
    # `getattr`, for the reason every hand-built args namespace in this repo's
    # tests proves: a caller that does not set `reuse_coverage` is not reusing,
    # so the safe default is the guard OFF. Read directly, this raised
    # AttributeError inside a producer test -- a new crash on a proof surface,
    # introduced by a guard added to prevent one.
    reusing = getattr(args, "reuse_coverage", False)
    # Not when the operator ASKED for contexts. `--collect-test-contexts` exists so
    # a caller can hand-build the sampler's corpus with this very gate; declining
    # to reuse what it was just told to produce would be the tool arguing with its
    # own flag.
    wants_contexts = getattr(args, "collect_test_contexts", False)
    if (
        reusing
        and not wants_contexts
        and coverage_json.is_file()
        and coverage_is_context_bearing(coverage_json) is True
    ):
        # Someone else's corpus. This gate never reads `contexts` and its own
        # probe never writes them, so a context-bearing file at the path it is
        # about to reuse was produced with contexts by SOMETHING -- most likely the
        # cosmic-ray sampler, which needs them and defaults to this same path. The
        # payload states the observation and not the attribution, because this gate
        # can also write such a file itself under `--collect-test-contexts`, and
        # naming a writer it did not observe is the class this same slice repaired
        # one function down. Loading
        # it measured 36.5s and 20.44 GiB of peak RSS, and on a smaller host that is
        # not slow but a `MemoryError` this gate has no branch for, which would
        # surface an out-of-memory crash as a tool failure rather than as the
        # refusal-to-judge it is. Decline cheaply from a 4 KB header read instead.
        #
        # A SKIP, not a blocker: the corpus being wrong for this reader says
        # nothing about whether the changed lines are covered, and inventing a
        # verdict from that is the substitution this whole lane refuses.
        return {
            **base,
            "reason": (
                f"coverage source at {args.coverage_json} carries per-test `contexts` "
                "(`meta.show_contexts: true`), which this lane's producer never writes and "
                "this verdict never reads; changed-line teeth skipped (non-blocking) rather "
                "than paying a multi-GB load for those columns. See `resume_command` below."
            ),
            **resume_fields(repo_root, base_sha),
        }
    if args.require_fresh_coverage and coverage_json.is_file():
        marker = changed_line_coverage_marker_path(coverage_json)
        recorded = read_changed_line_coverage_marker(marker)
        current = changed_pool_fingerprint(repo_root, base_sha)
        if recorded is None or recorded != current:
            return {
                **base,
                "reason": (
                    f"coverage source is stale: fingerprint marker {recorded or 'absent'} != current "
                    f"{current}; changed-line teeth skipped (non-blocking). "
                    "See `resume_command` below: it renders the verdict itself, cheaply."
                ),
                **resume_fields(repo_root, base_sha),
            }
    if args.skip_if_no_coverage and not coverage_json.is_file():
        return {
            **base,
            "reason": (
                f"no coverage source at {args.coverage_json}: changed-line teeth skipped "
                "(non-blocking). See `resume_command` below: it renders the verdict itself "
                "from its own focused corpus rather than writing this path."
            ),
            **resume_fields(repo_root, base_sha),
        }
    return None


def _ensure_coverage(args, repo_root: Path, coverage_json: Path, base_sha: str) -> None:
    """Produce coverage when needed, and in producer mode stamp the
    `.changed-line.fingerprint` marker so the release consumer's `--require-fresh-coverage`
    can trust the coverage was built for this changed-pool content. Skip guards
    run before this, so here a missing/stale reuse target means "run the probe".

    The probe drops `dynamic_context` on BOTH arms (lever A): the changed-line
    verdict only needs executed-vs-missing lines, and per-test context is what
    blew the coverage JSON up. Subprocess capture is retained.

    Producer mode used to be the only arm that dropped it, which made the cheap
    path a side effect of `--write-fresh-marker` -- a flag about stamping the
    freshness marker, not about which columns the verdict reads. The other arm
    then paid for a `contexts` block this gate has no reader for. Measured on this
    repo (#696), same coverage data, export flag the only difference: 8.22 GB vs
    12.26 MB, and 36.5s / 20.44 GiB RSS vs 0.13s / 0.06 GiB just to LOAD it. The RSS
    is the sharper half -- on a smaller host that load raises `MemoryError`, and
    this gate has no branch for that, so an out-of-memory crash on a proof surface
    reads as a tool failure rather than as the refusal-to-judge it is.

    `--collect-test-contexts` restores collection explicitly for a caller
    hand-building the cosmic-ray sampler's corpus. Read with `getattr` because the
    parity tests construct a minimal args namespace, and the safe default when the
    attribute is absent is the cheap one."""
    if not args.reuse_coverage or not coverage_json.is_file():
        config = args.config if args.config.is_absolute() else repo_root / args.config
        test_command = args.test_command or read_test_command(config)
        run_test_coverage(
            repo_root,
            test_command,
            coverage_json,
            dynamic_context=getattr(args, "collect_test_contexts", False),
        )
    if args.write_fresh_marker:
        write_coverage_fingerprint_marker(repo_root, coverage_json, base_sha)


def coverage_not_verified_warning(changed_eligible: list[str], reason: str) -> str:
    """Recurrence tripwire (#335): the gate is SKIPPING the changed-line check while
    eligible mutation-pool files actually changed in this range.

    The #219 -> #251 -> #260 -> #320 -> #321 -> #335 seam recurs because a silent
    skip (no/stale coverage) reads IDENTICALLY to a clean pass: the author's
    release attestation goes green, the uncovered changed lines reach ``main``, and
    only the scheduled CI run — which accumulates everything since its last run —
    flags them after merge and auto-files. Making the unverified skip LOUD at the
    release boundary is the structural reduction: the obligation remains visible
    before publication.
    Non-blocking by design (it names the fix; it does not change the verdict).
    """
    files = ", ".join(changed_eligible)
    return (
        f"{len(changed_eligible)} eligible mutation-pool file(s) changed but their "
        f"changed lines were NOT verified for coverage ({reason.rstrip('.')}). An "
        "unverified skip reads as a clean pass, so uncovered changed lines reach main "
        "and the next scheduled mutation run flags them (the #335 recurrence). First run "
        "`python3 scripts/mutation/suggest_mutation_coverage_command.py --repo-root . --detail` "
        "to find a focused producer command; if it cannot map the change, run "
        "`python3 scripts/mutation/release_changed_line_coverage.py --repo-root . "
        "--base-sha <base>` at the release boundary. "
        f"Files: {files}"
    )


def _surface_skip(skip: dict, changed_before_coverage: list[str]) -> dict:
    """Annotate a non-blocking skip and surface the #335 recurrence obligation loudly.

    The skip path is only reached with a non-empty ``changed_before_coverage`` (the
    empty case returns earlier), so a skip ALWAYS means "eligible files changed but
    went unverified" — the recurrence driver. Write the obligation to stderr and
    record it structurally; the verdict itself stays non-blocking, but exits 3 (ran, established nothing) rather than 0."""
    not_verified = coverage_not_verified_warning(
        changed_before_coverage, str(skip.get("reason", "coverage unavailable"))
    )
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
    `scripts/mutation/check_mutation_run_proof.py`."""
    sys.stderr.write(
        "WARNING (changed-line mutation gate): no base_sha, so this verdict proves NOTHING "
        "about changed-line coverage (the mutation-dispatch-no-base-sha-false-proof class). "
        "Before citing a run as changed-line proof, run "
        "`python3 scripts/mutation/check_mutation_run_proof.py --claim changed-line ...`.\n"
    )
    _emit(
        {
            "ok": True,
            "blocking": [],
            # No range, so no changed set was ever derived: the pair is null rather
            # than `0 of 0`, which would claim an empty scope this run never read.
            **scope_counts_not_computed("no base_sha: no range, so no changed set was derived"),
            "changed_line_proof": "not-provable",
            "reason": "no base_sha: the changed-line classifier is non-blocking by construction (matches workflow_dispatch, which computes no base_sha)",
        }
    )
    return 0


def _emit_dirty_refusal(uncommitted: list[str], metadata: dict) -> int:
    """Startup refusal — emitted BEFORE any coverage/probe work."""
    message = dirty_pool_refusal(uncommitted)
    sys.stderr.write(f"ERROR (changed-line mutation gate): {message}\n")
    _emit(
        {
            "ok": False,
            "blocking": [],
            "refused": True,
            "reason": message,
            **metadata,
            "changed_line_proof": "refused",
        }
    )
    return REFUSED_EXIT


def _run_metadata(
    base_sha: str, head_sha: str, pinned: dict[str, str], contaminated: list[str]
) -> dict:
    """Additive payload metadata shared by every verdict this run can emit."""
    metadata: dict[str, object] = {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "resolved_head_sha": pinned["resolved_head_sha"],
        # Startup default: the refusal paths that fire before the changed set is
        # derived carry this, and `main` overwrites it with the real pair as soon
        # as the set exists. Both are the same key, so no verdict lacks one.
        **scope_counts_not_computed(
            "startup refusal: the run ended before the changed set was derived"
        ),
    }
    if contaminated:
        metadata["dirty_pool_unverified"] = True
        metadata["uncommitted_pool_files"] = contaminated
        metadata["changed_line_proof"] = "unverified-dirty-worktree"
    return metadata


def _finalize(
    report: dict, repo_root: Path, base_sha: str, head_sha: str, pinned: dict, exit_code: int
) -> int:
    """Emit the report, downgrading it to UNTRUSTED when the repo moved mid-run."""
    drift = run_state_drift(repo_root, base_sha, head_sha, pinned)
    if drift:
        _mark_untrusted(report, drift)
        sys.stderr.write(f"ERROR (changed-line mutation gate): {report['untrusted_reason']}\n")
        _emit(report)
        return REFUSED_EXIT
    _emit(report)
    return exit_code


def _blocking_report(
    repo_root, args, base_sha, head_sha, changed_before_coverage, coverage_json
) -> dict:
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
    blocking, blocking_targets, changed_lines = changed_line_scope_verdict(scope)
    blocking_detail = blocking_details(blocking, statement_lines, changed_lines)

    return {
        "ok": not blocking,
        "changed_pool_files": changed_before_coverage,
        "blocking": blocking,
        "blocking_detail": blocking_detail,
        "blocking_targets": blocking_targets,
        # Advisory only (#465): names blocked files whose candidate tests exercise them
        # where coverage was never attributed. Never suppresses a blocker, and claims
        # file-level granularity only — see the helper's docstring. `_scope` says what
        # was examined, so advisory silence is a statement rather than an absence.
        **subprocess_coverage_advisory_report(repo_root, blocking_targets, blocking=blocking),
        "targeted_mutant_proof": {
            "required": bool(blocking),
            "contract": (
                "Before hand-mutating, cite/display one blocking_targets path:line "
                "entry, mutate that exact line, record the failing test, then revert."
            ),
        },
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    base_sha = (
        args.base_sha if args.base_sha is not None else os.environ.get("MUTATION_BASE_SHA") or ""
    ).strip() or None
    head_sha = (
        args.head_sha if args.head_sha is not None else os.environ.get("MUTATION_HEAD_SHA") or ""
    ).strip() or "HEAD"

    if not base_sha:
        return _emit_no_base_sha()

    # Startup preflight: detect contamination and pin the analyzed head BEFORE any
    # coverage/probe work, so a contaminated run costs ~0s instead of ~10 minutes
    # and a commit landing mid-run cannot re-resolve `HEAD` under the analysis.
    all_eligible = set(list_eligible(repo_root))
    checkout = GitCheckout(repo_root)
    trust = probe_run_trust(repo_root, head_sha, all_eligible, checkout=checkout)
    contaminated = trust.contaminated
    pinned = _pin_run_state(
        repo_root,
        base_sha,
        head_sha,
        resolved_pair=trust.resolved_pair,
        checkout=checkout,
    )
    metadata = _run_metadata(base_sha, head_sha, pinned, contaminated)
    if trust.unestablished_kind == INSPECTION_FAILED:
        # REFUSED (2), not unestablished (3). Exit 3's leniency is granted for a
        # named reason -- a dirty worktree IS the normal mid-work state -- and a
        # git command that will not run is never that. Inheriting one cause's
        # leniency for a different cause is the substitution this family of
        # scripts exists to refuse.
        sys.stderr.write(
            f"ERROR (changed-line mutation gate): {trust.unestablished_reason}; "
            "this run produced NO verdict.\n"
        )
        return _finalize(
            {
                "ok": False,
                "blocking": [],
                "refused": True,
                **metadata,
                "changed_line_proof": "refused",
                "reason": trust.unestablished_reason,
            },
            repo_root,
            base_sha,
            head_sha,
            pinned,
            REFUSED_EXIT,
        )
    if contaminated and not args.allow_dirty:
        return _emit_dirty_refusal(contaminated, metadata)
    fg_warning = false_green_message(contaminated) if contaminated else None
    if fg_warning:
        sys.stderr.write(f"WARNING (changed-line mutation gate): {fg_warning}\n")
    analyzed_head = pinned["resolved_head_sha"]

    changed_before_coverage = [
        p for p in list_changed(repo_root, base_sha, analyzed_head) if p in all_eligible
    ]
    changed_before_coverage, unanalyzed = _apply_file_limit(args, changed_before_coverage)
    # The scope is now known, so every verdict emitted from here down states its
    # denominator — not only the limited runs that also get the `unanalyzed` list.
    metadata = {**metadata, **scope_counts(changed_before_coverage, unanalyzed)}
    if trust.unestablished_kind == SCOPE_MISMATCH and changed_before_coverage:
        # Deliberately AFTER the changed set is known. Exit 3's own contract scopes
        # it to a NON-EMPTY changed set -- "an empty changed set still exits 0" --
        # and returning 3 before this point made an empty scope refusable, which
        # `release_changed_line_coverage` names by name as an incoherent
        # blocker on the gate whose credibility is the point.
        sys.stderr.write(
            f"WARNING (changed-line mutation gate): {trust.unestablished_reason}; "
            "this run establishes no changed-line verdict.\n"
        )
        mismatch: dict = {
            "ok": True,
            "blocking": [],
            **metadata,
            "changed_line_proof": "unestablished-untrustworthy-input",
            "reason": trust.unestablished_reason,
        }
        if unanalyzed:
            # Two unestablished causes at once. Returning here dropped the limit's
            # own disclosure, so the operator saw one reason and not the other.
            mismatch["unanalyzed_changed_pool_files"] = unanalyzed
        return _finalize(mismatch, repo_root, base_sha, head_sha, pinned, UNESTABLISHED_EXIT)
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
        empty_scope: dict = {"ok": True, "blocking": [], **metadata, "reason": reason}
        if trust.unestablished_kind == SCOPE_MISMATCH:
            # Exit stays 0 — the range honestly changed no pool file — but the
            # DISCLOSURE must not vanish with it. Moving the mismatch check below
            # the changed-set computation (to stop refusing an empty scope) left
            # this path silent: the same tree judged against the checked-out HEAD
            # exits 1 with a real blocker, while this one printed `clean` and said
            # nothing about why the two disagree. `reason` is deliberately NOT
            # touched: the consumer prefix-matches it to recognise an empty scope.
            empty_scope["analyzed_head_not_checked_out_head"] = trust.unestablished_reason
            sys.stderr.write(
                f"WARNING (changed-line mutation gate): {trust.unestablished_reason}. "
                "This range changed no eligible pool file, so there was nothing to "
                "prove — but the empty scope is the ANALYZED head's, not this tree's.\n"
            )
        # `unanalyzed` non-empty means files WERE in scope and the limit emptied the
        # set: nothing was established about them, so 3 (not 4) -- this run analyzed
        # NOTHING, which is what 3 means. An empty `unanalyzed` means nothing was in
        # scope to begin with, which is honestly nothing to prove.
        #
        # `fg_warning` is consulted here for the same reason the ordering rule exists.
        # It used to be attached to the payload and dropped before the byte, so a
        # contaminated pool whose range happened to touch no eligible file exited 0 --
        # a computed blind-spot fact that reached the report and not the answer, which
        # is the class this whole slice repairs, one branch over from where round 1
        # caught it.
        empty_code = UNESTABLISHED_EXIT if (unanalyzed or fg_warning) else 0
        return _finalize(
            _attach_warning(empty_scope, fg_warning),
            repo_root,
            base_sha,
            head_sha,
            pinned,
            empty_code,
        )

    coverage_json = (
        args.coverage_json if args.coverage_json.is_absolute() else repo_root / args.coverage_json
    )
    skip = _coverage_source_skip(args, repo_root, coverage_json, base_sha, head_sha)
    if skip is not None:
        skip = {**skip, **metadata}
        # Coverage was unavailable over a NON-EMPTY changed set: the reason field
        # already said so and the exit code said PASS.
        report = _attach_warning(_surface_skip(skip, changed_before_coverage), fg_warning)
        return _finalize(report, repo_root, base_sha, head_sha, pinned, UNESTABLISHED_EXIT)

    report = _blocking_report(
        repo_root, args, base_sha, analyzed_head, changed_before_coverage, coverage_json
    )
    blocking = list(report["blocking"])
    clean_code = _verdict_exit_code(blocking, fg_warning, unanalyzed)
    payload = _attach_warning({**report, **metadata}, fg_warning)
    if clean_code == PARTIAL_EXIT:
        # The payload states it too. A caller that reads `ok`/`blocking` and never
        # the exit code would otherwise see a clean report with no field saying the
        # scope was short -- the same one-channel gap, one layer up.
        payload["changed_line_proof"] = "partial"
    code = _finalize(
        payload,
        repo_root,
        base_sha,
        head_sha,
        pinned,
        clean_code,
    )
    if blocking and code == 1:
        _write_blocking_stderr(
            blocking,
            report["blocking_targets"],
            report.get("subprocess_coverage_advisory"),
            report.get("subprocess_coverage_advisory_scope"),
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
