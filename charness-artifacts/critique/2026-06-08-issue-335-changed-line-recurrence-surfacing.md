# Critique Review
Date: 2026-06-08

## Decision Under Review

Slice 3 of the #335 goal (commit `81332c72`): structurally reduce the recurring
changed-line mutation-gate seam by converting the cheap consumer's SILENT skip
(exit 0 when coverage is absent/stale while eligible mutation-pool files changed)
into a LOUD, non-blocking author-time obligation — a surfacing, not a new hard gate.

## Failure Angles

- Band-aid risk: an ignorable stderr warning that the same closeouts which dropped
  85 lines would also have ignored — i.e. not a real structural reduction.
- Swallowed signal: the WARNING goes to stderr; if the pre-push runner hides
  non-failing output, the surfacing is a production no-op.
- Verdict drift: the skip branch must still exit 0 (no other gate's verdict may
  change on existing code); a regression here would be a real behavior change.
- Mis-targeting / noise: firing on a clean pass or when nothing eligible changed.
- Length gate: `main()` must stay ≤100 lines (hard AST gate).

## Counterweight Pass

- The band-aid worry is the central one; it is answered by EFFICACY EVIDENCE, not
  assertion (see Fresh-Eye Satisfaction): the warning string matches
  `run-quality.sh`'s attention-output regex (`:296`), which forces the log to be
  printed even on a green pass (`:300-303`). So the obligation reaches the operator
  at the exact green pre-push moment. A new hard gate / auto-produce is the goal's
  named DEFERRED follow-up — judging this slice as "should block" reviews it out of
  scope. Real ground gained: a structured `coverage_not_verified` discriminator a
  future hard gate can consume.
- Verdict, targeting, and length worries are all falsified below; none survived.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: scripts/run-quality.sh:296 | action: document | note: stderr warning is NOT swallowed — runner's attention-output grep forces a full log print on green pass, so the surfacing reaches the operator (reviewer-verified).
- F2 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_changed_line_mutation_coverage.py:271 | action: fix | note: stale-coverage skip tests did not assert the new surfacing; FOLDED — added coverage_not_verified + stderr asserts to both stale-skip tests so that path is pinned too.
- F3 | bin: over-worry | evidence: strong | ref: scripts/check_changed_line_mutation_coverage.py:287 | action: defer | note: skip branch still returns 0 and is reached only after the non-empty changed_before_coverage guard — no verdict change, no fire on clean/empty runs; main() = 95 lines after the helper extraction.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer (different agent context), read-only, shared parent worktree, git-show inspection only.
- Requested spawn fields: Agent(subagent_type=general-purpose) with the slice review packet (intent, changed files/surfaces, expected invariants, proof already run, non-claims, out-of-scope, reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: bounded reviewer (agent aeaf802a52e71e81a) ran via the Agent tool and returned VERDICT: SHIP with zero blockers; one nit (F2) folded, one (cosmetic long line) declined.

## Fresh-Eye Satisfaction

The fresh-eye reviewer returned SHIP and independently verified the mechanism's
efficacy rather than just its code: it traced the WARNING string through
`run-quality.sh:296` (attention-output grep) to `:300-303` (cat-on-attention),
confirming the once-silent skip now reaches the operator at the green pre-push
moment — the concrete signal that distinguishes a structural reduction from a
band-aid. It also confirmed the additive JSON keys have no downstream parser to
break (the only consumer uses exit code + stderr grep), the skip branch is
byte-unchanged except the surfacing call, and the verdict stays 0. One nit folded
(F2), one cosmetic nit declined.
