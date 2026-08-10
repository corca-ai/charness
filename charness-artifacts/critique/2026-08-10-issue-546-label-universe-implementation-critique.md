# Implementation critique — #546 (the label-universe gate, two rounds)
Date: 2026-08-10

## Decision Under Review

Whether to ship the built gate for [#546](https://github.com/corca-ai/charness/issues/546):
a reader deriving the labels `run-quality.sh` can queue, a gate refusing a budgeted
label outside that set, a queue-time assertion in the runner, and the widening of
`check_timing_layer_completeness` onto the same reader.

Two prior artifacts constrain this one: the
[revert critique](./2026-08-10-issue-546-unenforceable-budget-critique.md) (the
sample-history repair that was built, measured defective and reverted) and the
[pre-design critique](./2026-08-10-issue-546-declared-universe-pre-design-critique.md)
(nine findings against the design sketch, before code existed).

**Outcome: SHIPPED, and #546 stays OPEN.** The slice closes one of the three rot
modes the issue names. It does not close the issue, and no surface in it claims to.

## Failure Angles

- **A regex over bash on a proof surface.** If the reader misses a gate, the label
  leaves the universe and a budget naming it reads as orphaned — a blocking pre-push
  red whose remedy tells the operator to delete a correct bar. That is the reverted
  repair's defect with a new mechanism.
- **The export boundary.** `check_runtime_budget.py` is installed into consumer
  repos that have no `run-quality.sh`; a universe reader that only understands this
  runner either refuses every consumer budget or no-ops silently.
- **Widening an existing gate.** Moving `check_timing_layer_completeness` onto the
  shared reader changes what an already-enforced gate demands.
- **Claiming more than the gate decides.** #546 names three rot modes and this
  design reaches one.

## Counterweight Pass

- The false-red fear was retired by measurement, not by argument: all 38 budgeted
  labels across all four blocks resolve, so arming refuses nothing that previously
  passed. The timing-gate widening was measured too — three labels, three rows.
- The "this is just a bigger parser" worry was not over-worry, and round 1 proved
  it: the design's own safety claim was fiction until it was implemented.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/quality_label_universe.py | action: fix | note: ROUND-1 BLOCKER. The module docstring asserted that `run-quality.sh` checks each queued label against the universe. No such assertion existed, and it was the sole justification for regexing bash on a proof surface. Implemented rather than deleted: the runner now builds the universe at startup and `queue_timed` calls `assert_label_in_universe`. Round 2 then narrowed the claim to source 1, because the aggregate and startup-probe sources never pass through `queue_timed` and saying "every label" was the same overclaim one size smaller.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_timing_layer_completeness.py | action: fix | note: ROUND-1 BLOCKER. The widened gate is classified commit-time and had no `except UniverseError`, so an unresolvable queue line surfaced as a Python traceback inside the pre-commit hook, from a gate whose subject is the timing table. Handler added; round 2 moved `stale_docs_only_labels` inside the same `try` because a second call to a raising reader outside the handler is how the traceback returns.
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/quality_label_universe.py | action: fix | note: ROUND-2 BLOCKER, and the sharpest finding of the slice. The round-1 repair for F2 caught the exception class that existed; the round-1 repair for F5 then introduced a NEW one — `adapter_lib` raises bare `ValueError` on block-scalar headers and anchor-like scalars, and the adapter already contains thirteen folded scalars. Changing one `>-` to `>+` would have aborted the ENTIRE runner at startup with a traceback blaming the queue lines. Now converted to a named `UniverseError`. Before this reader existed the same adapter defect surfaced as one red gate with an accurate message; a repair must not make a diagnostic worse than what it replaced.
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: ROUND-2 BLOCKER. The F1 repair shipped a comment claiming an empty-universe fail-open for the consumer case — and the branch was dead, because the reader printed its "not derivable" prose on STDOUT at exit 0. That sentence became a one-element universe, the empty check never fired, and the first gate was refused with a remedy about queue-line quoting: fail-closed with a wrong remedy, in the branch documented as fail-open. Verified by running the reader against a runner-less repo (rc=0, prose on stdout). Repaired by making stdout labels-or-nothing and prose stderr-only.
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/quality_label_universe.py | action: fix | note: ROUND-1. A hand-rolled `startup_probes` indentation parser decided the block had ended when the list was written flush against its key — equally valid YAML — dropping every probe and orphaning `charness-version`, which is budgeted in all four blocks. Replaced with the repo's shared `adapter_lib` reader. Round 2 kept the pressure: a declared-but-unreadable probe now RAISES instead of returning `[]`, because the silent-empty path is the same orphaning defect with no message at all.
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/check_runtime_budget_universe.py | action: fix | note: ROUND-1. Pre-design F4 required arming only on a derivable universe; the first cut armed on runner PRESENCE. A runner driving its gates from a list file has zero literal call sites, so the universe would be the four aggregate labels and every other budget would read as orphaned. Now an empty call-site set is "no universe", not "an empty one", and the degrade line is WARN-prefixed so `print_phase_output` actually surfaces it rather than rendering a bare green PASS.
- F7 | bin: act-before-ship | evidence: moderate | ref: scripts/quality_label_universe.py | action: fix | note: ROUND-1. A backslash line continuation put the label on a line whose head was the previous one, so an ordinary long-line wrap either dropped the gate silently or refused a correct file with a remedy that did not apply. Continuations are joined first; round 2 added the bash rule that a comment ending in a backslash does NOT continue.
- F8 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_runner.py | action: fix | note: ROUND-2. The F1 repair added a new hot-path refusal to the runner with ZERO coverage — the assertion justifying the whole design was itself unproven. Two tests added. Writing them corrected a belief: an unregistered wrapper forwarding `"$1"` is caught by the READER (unresolvable), not the assertion; what the assertion catches is a call the line-anchored regex cannot see at all, such as a one-line `if ...; then queue_timed ...; fi`. Both shapes are now pinned, and the test docstrings record which mechanism owns which.
- F9 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_runtime_budget_universe.py | action: fix | note: ROUND-1. `test_this_repo_has_no_orphaned_budget` asserted `checked > 0`, which would have stayed green through the exact regression that matters: dropping `runtime_budget_profiles` leaves the ten top-level budgets and hides every profile block. Now pins `>= 38` and the standing-probe source. Also: the label-shape rejection branch had no test, and the first attempt to write one exercised the neighbouring branch instead (a spaced label never reaches the shape check, because `\S+` captures only `"Not`).
- F10 | bin: over-worry | evidence: strong | ref: .agents/quality-adapter.yaml | action: document | note: the fear that a profile-scoped bar would fail on a machine that never selects that profile does not materialize. Membership is machine-independent by construction, so reading the union of all four blocks costs nothing in false reds and is the only version that reaches the aarch64 block the adapter itself records as never sampled.
- F11 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/595 | note: two siblings of #546's shape on the same file — `latest_spikes` and `runtime_visibility_findings` are computed, rendered, and consulted by no exit path. Filed rather than folded in.

## Disposition

SHIPPED. Both rounds' blockers are repaired; round-2 repairs are recorded as
accepted-unreviewed per the two-round cap.

**#546 is NOT closed by this slice, and that is stated on every surface it touches.**
The gate decides the RENAME mode. A label the runner still names but never RUNS —
conditionally queued, or behind an opt-in — is in the universe and passes;
`dead-code-advisory` is the live in-repo instance, budgeted at 12500ms and queued
only under an env opt-in. Separating "legitimately conditional" from "abandoned
behind an opt-in" needs an adapter-declared expectation, because the runner does not
have that information either. The gate's own pass line says so, its docstring says
so, and the test suite's module docstring leads with it.

Two rounds, and the round reading the REPAIRS found a different class than the round
reading the design: round 1 found a claim with no mechanism, round 2 found that the
repair for it shipped a second claim with no mechanism (F4) and that an unrelated
round-1 repair had opened an unhandled exception path into the runner's startup (F3).

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer`), unnamed and synchronous.
- Requested spawn fields: subagent_type=bounded-reviewer, run_in_background=false, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: both rounds returned findings in-band. Boundary verify reports `clean` for window `w-20260810T114132Z-250569` (round 1) and `clean` for `w-20260810T115546Z-288354` (round 2); no tracked file and no index entry moved across either review window.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated, two rounds plus a pre-design round. The reviews did not polish this
slice, they changed it: round 1 turned a fictional safety mechanism into a real one,
and round 2 caught that repair's own fiction. Two of the reviewers' requests were
evidence the parent could run and they could not; both were run and both confirmed
the reviewer (the prose-on-stdout path at rc=0, and that the empty-line `&&` under
`set -e` is benign on this host's bash — repaired to an `if` anyway).

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was the uncommitted working tree. -->

## Boundary Ownership

- Producer: `quality_label_universe` and `check_runtime_budget_universe`, which render a verdict about the adapter's budget declarations, plus the runner's queue-time assertion.
- Consumer: the pre-push quality run, whose pass/fail an operator reads as protection.
- Owning surface: `scripts/**`, with `docs/conventions/validator-timing-layers.md` as the declaration the widened gate enforces.
- Verdict: single-surface
