# Session structural improvement
Date: 2026-08-06
Goal: charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md

## Context

This retro covers the local proof and structural quality work after the #508/#509
sequence reached its final local publish boundary. The immediate problem was a
runtime-budget refusal for `validate-inventory-consumption-declaration`, despite
the validator taking about 2.4 seconds when run alone. Trustworthy evidence is
the source/plugin diff, focused pytest results, the bounded fresh-eye findings,
the critique validator, and the standing quality runner; the causal claim that
contention caused the refusal is still moderate until a controlled A/B sample
exists.

## Window

The window is the 2026-08-06 session from the initial worktree/quality audit
through the repaired runner and its concrete review. It includes the proposal
round, the repaired-diff round, source/plugin synchronization, and focused
behavioral proof. Full post-repair quality, commit, push, and remote CI are
deliberately pending at this point in the retro record.

## Evidence Summary

- Before the repair, `./scripts/run-quality.sh --read-only` failed only
  `check-runtime-budget`: 16.075s and then 18.572s against a 15.500s budget.
- The same declaration validator ran in 2.37s and 2.41s wall time alone, while
  its runner phase was queued with nine subprocess-producing inventory gates.
- The runner now drains the first phase, runs the declaration gate as its own
  phase, flushes it immediately, and only then resumes unrelated gates. The
  checked-in plugin mirror is synchronized from the source runner.
- The focused runner/aggregate suite passed 54 tests; shell syntax and
  `git diff --check` passed. The new probe observes first-phase completion,
  declaration completion, next-phase start, runtime-record order, and failure
  receipt propagation.
- Two fresh-eye rounds returned findings before parent edits. Boundary
  fingerprints were clean for every returned reviewer. The repaired round
  caught the stale plugin mirror and the insufficient immediate-flush test.
- The critique artifact and final reviewed-input packet validate successfully;
  no runtime-budget increase or speed improvement is claimed yet.

## Waste

- runtime-budget-contention (recurrence-class: runtime-budget-contention): the
  first diagnosis treated a noisy aggregate sample as if the validator itself
  were slow. The standalone timing was gathered only after the broad gate had
  already spent two failed runs. The waste was causal uncertainty plus rerun
  cost, not the quality gate itself.
- proof-surface-review-binding (recurrence-class: proof-surface-review-binding):
  the first critique packet bound the wrong/incomplete reviewed input shape and
  required regeneration before validation. This was caught locally, but packet
  identity should have been frozen before drafting the critique record.
- mutation-producer-selection (recurrence-class: mutation-producer-selection):
  the #509 proof needed an explicit focused producer command because the
  standing suggestion path did not surface every relevant producer test. The
  existing helper is useful; the waste is manual sequencing and should be
  addressed in the next workflow slice rather than by weakening a mutation
  floor now.
- The fresh-eye rounds, source/plugin parity check, and focused regression proof
  were necessary safety work at a proof-surface boundary, not waste. No host
  metric supports claiming a token or wall-clock improvement from this session.

## Critical Decisions

- Isolate the declaration gate in the runner with `flush → declaration gate →
  flush`, because the runner owns phase scheduling and receipt aggregation. A
  broad scheduler abstraction was rejected as disproportionate to one measured
  seam.
- Add a next-phase behavioral probe and runtime-record ordering assertions. A
  source-order assertion alone could not prove the immediate flush, and a
  two-label timing test could false-green under scheduler delay.
- Keep the 15.5-second budget unchanged. The repair changes measurement
  conditions, but it does not establish a cross-host A/B distribution; raising
  the floor now would trade a visible signal for an unproven green.
- Treat the generated plugin mirror and critique packet as part of the same
  change surface. Verification follows sync, and the final packet excludes a
  self-referential critique artifact while naming the exact reviewed files.

## Trends vs Last Retro

Compared with the prior lessons, the session continued the useful pattern of
measured runtime ownership and explicit proof boundaries, but repeated two
known traps: shaping a remedy before verifying its premise and letting a
durable review record lag its reviewed input identity. The improvement is that
the current round caught both through bounded fresh-eye review before commit;
the remaining gap is to make A/B runtime sampling and mutation-producer
selection part of the normal workflow instead of relying on reviewer discovery.

## North Star Alignment

The North Star says the harness should brief a capable judge and keep teeth only
where a wrong answer escapes. P1/P2 held: this was judgment on reversible local
runner work, and ownership stayed at one runner phase rather than spreading a
new abstraction across validators. P3 held by preserving the existing receipt
and failure semantics while adding only the boundary needed for the measured
contention seam. P4 held provisionally through distinct fresh-eye observers,
clean boundary fingerprints, and a separate behavioral test channel; final push
and remote CI still require a different observer and channel. P5 held by
retaining the budget and making the residual uncertainty visible rather than
adding a new floor.

The mis-application was treating the first broad runtime sample as sufficient
causal evidence and allowing the first critique input identity to be incomplete.
Those are North Star failures because they let a terminal-looking signal outrun
the judge's context. The relevant failure signature was a green-or-nearly-green
gate that measured contended scheduling rather than the owned validator, plus a
proof record whose identity was not yet durable.

## Expert Counterfactuals

- Engelbart would have asked which recurring workflow action should become a
  reusable augmentation: capture an isolated runtime sample and freeze its
  identity before analysis. That points to the next-session workflow change,
  not a one-off threshold edit.
- Weinberg would have forced the controlled comparison earlier: same host,
  same validator, first-phase contention versus isolated phase, repeated enough
  to separate scheduler noise from validator cost. Until then, “contention was
  causal” remains moderate.
- Gawande would have required a small operational checklist at the phase
  boundary: source change, generated mirror, next-phase drain, runtime record,
  failure receipt. The repaired probe now encodes that checklist's critical
  behavior.
- Minto would have separated the claim “the phase is isolated” from “the
  budget should change”; the former is proven locally, the latter is deferred.

## Sibling Search

- same layer: `scripts/run-quality.sh` phase orchestration | decision: same waste, fix now | proof: focused probe and runtime-record order assert first drain, isolated declaration completion, and next-phase start
- abstraction up: `.charness/quality/runtime-signals.json` and the runtime budget policy | decision: valid follow-up outside the slice | proof: current samples are host-local and no controlled A/B cohort exists | follow-up: deferred next-session-runtime-samples
- specialization down: `scripts/validate_inventory_consumption_declaration.py` | decision: intentional boundary | proof: standalone timing is low and validator semantics were unchanged; scheduling remains owned by the runner
- mental-model siblings: `scripts/suggest_mutation_coverage_command.py` and the #509 proof workflow | decision: valid follow-up outside the slice | proof: the helper exists but the focused producer set still required manual expansion | follow-up: deferred next-session-mutation-producer

## Next Improvements

- workflow: run a controlled isolated-vs-contended runtime sample before any
  budget retune; freeze quality/critique packet identity before broad review;
  invoke the mutation-coverage suggestion helper before assembling a focused
  producer command.
- capability: strengthen the quality workflow's runtime profile and mutation
  producer discovery so the operator receives a complete evidence command,
  while keeping both as advisory or existing-gate reuse until evidence earns a
  floor.
- memory: this retro, the final critique packet, and the next-session draft goal
  must remain in the handoff; preserve #508/#509 as OPEN/local-only until an
  independent remote observer verifies the final push and each closeout floor.

## Packet Consumed

Packet Consumed: `charness-artifacts/retro/2026-08-06-session-retro-packet.md`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-06-session-retro.md
