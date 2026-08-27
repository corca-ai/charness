#!/usr/bin/env python3
"""The changed-line gate's exit-code vocabulary, and which byte a run earns.

Lives beside the gate rather than inside it because the DIFFERENCES between these
bytes are a contract other modules read -- `release_changed_line_coverage`
decides whether to refuse from them, and `run-quality.sh` renders them. Keeping the values and the
ordering rule in one place is what stops a consumer from transcribing a literal
that later drifts from the meaning.
"""
from __future__ import annotations

#: Exit code for "no verdict was produced" — a startup refusal (contaminated
#: inputs) or an untrusted result (the repo moved mid-run). Deliberately distinct
#: from 1 (a real changed-line blocker) so callers can tell "I refused to judge"
#: from "I judged and it failed".
REFUSED_EXIT = 2
#: RAN, judged its whole analyzed set CLEAN, and could not analyze part of the
#: changed set. Distinct from 0, from 1, and from 3 on purpose.
#:
#: This gate already COMPUTED the scope-limiting fact -- `unanalyzed_changed_pool_files`
#: -- and wrote it to stderr in the operator's own words ("A clean verdict says
#: NOTHING about the rest"), and then returned the same byte it returns when there is
#: no blind spot at all. A warning that carries no signal the pipeline answers for
#: reads as narration beside a green; measured consequence: a local pass on
#: `b876abe5` over 6 of 7 files, a push, and a remote block on the 7th, which is the
#: exact ordering the release-final lane exists to enforce.
#:
#: NOT 3. Exit 3 is "established nothing"; this run established something about most
#: of its scope, and 3 is refusable at push time (`--refuse-unestablished`) while
#: this is deliberately NOT -- the operator's policy (a) keeps an unmapped changed
#: pool file non-blocking for a direct diagnostic, because a stop there is a stop on
#: the MAPPER's blind spot rather than on a coverage gap. The final release runner
#: still refuses every nonzero result: an unproven release is not publishable proof.
#: NOT 1: nothing was proven wrong, and a blocker that names no blocking line is a
#: refusal nobody can act on.
PARTIAL_EXIT = 4
# "Ran, established nothing" -- distinct from both a pass and a block. The runner
# renders this as UNPROVEN and counts it in neither column, because a green over a
# scope this gate never read is the exact class it exists to refuse, and printing
# PASS next to its own "this run proves nothing" warning is that class appearing in
# the verdict line. Deliberately NOT returned when no eligible file changed at all:
# an empty scope is honestly nothing to prove, and marking every such run UNPROVEN
# would train the reader to skip the word.
UNESTABLISHED_EXIT = 3


def _verdict_exit_code(blocking: list, fg_warning: str | None, unanalyzed: list) -> int:
    """Which byte a completed run deserves. ORDER IS THE CONTRACT.

    Strongest answer first, and "strongest" means most refusable, not most severe:

    1. ``blocking`` -> 1. A real uncovered changed line is the actionable answer and
       must never be downgraded to a scope caveat.
    2. ``fg_warning`` -> 3 (UNESTABLISHED). Changed pool files have uncommitted
       worktree edits ``base..HEAD`` cannot see, so a clean verdict is clean about a
       tree that is not this one.
    3. ``unanalyzed`` -> 4 (PARTIAL). Part of the changed set was never read.
    4. otherwise 0.

    Steps 2 and 3 were ORDERED THE OTHER WAY in the first cut of the partial repair,
    on the reasoning that "both are non-blocking non-passes, so either byte is honest
    when both hold". That is false and it cost a refusal: 3 is REFUSABLE at push time
    (``--refuse-unestablished``) and 4 is deliberately not, so a dirty pool that also
    had a limited scope stopped blocking a push it used to block. The operator's
    decision that created 4 was about the unmapped-file cause (policy (a)) and said
    nothing about the dirty-pool cause; widening the non-blocking answer into a case
    nobody decided is a policy change shipped under a defect-repair banner. Nothing
    is lost by the ordering -- ``unanalyzed_changed_pool_files`` is in the payload and
    on stderr either way; only the BYTE is exclusive.
    """
    if blocking:
        return 1
    if fg_warning:
        return UNESTABLISHED_EXIT
    if unanalyzed:
        return PARTIAL_EXIT
    return 0
