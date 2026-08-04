# Achieve Goal: Reduce closeout runtime by removing structural waste

Status: active
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-reduce-closeout-runtime-structural-waste.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: draft/backlog awaiting activation; no implementation work
  has started under this goal.
- Current slice: inactive draft; first slice is a short, evidence-led search for
  structural runtime waste.
- Current slice intent: find a recurring, removable cost in the real closeout
  journey before considering parallelism or another micro-optimization.
- Next action: activate, measure the affected path, and rank structural
  candidates by end-to-end seconds saved, proof risk, and rollback cost.
- Verification cadence: cheap deterministic checks at each boundary; fresh-eye
  proof for any proof-surface or contract change; full local proof at closeout.
- Gate cadence: candidate spikes use the narrowest honest checks; final proof
  uses the applicable locked quality path. Do not spend a full closeout ritual
  on a candidate that has already missed the materiality bar.
- History boundary: move completed measurements and rejected candidates into the
  Slice Log and Auto-Retro; do not leave the next session to rediscover them.

## Goal

Aggressively reduce the real local closeout journey by removing structural waste
before attempting parallelism. The search order is deliberate:

1. delete duplicated or low-signal execution;
2. remove unnecessary code and dead setup that lies on a recurring path;
3. remove or collapse avoidable bootstrap and process-start overhead;
4. only then consider bounded parallelism as a separate follow-up.

The goal is about actual elapsed time, not a smaller source listing or a faster
isolated helper. A candidate is worth shipping only when it preserves the proof
contract and produces material end-to-end relief on the current host. The user
has already judged an approximately eight-second saving with roughly an hour of
rollback cost to be economically poor; this goal therefore uses a fixed initial
materiality bar of at least ten seconds on the real closeout path, chosen before
implementation. If the measured path does not support that bar, the candidate
is rejected or the goal records that the target has changed rather than
accumulating more ceremony.

The goal may end with a structural cleanup that is both materially faster and
proof-preserving, or with an evidence-backed no-safe-change disposition for the
candidate actually tested.

## Non-Goals

- Do not weaken, skip, downgrade, relocate, or hide a proof gate to obtain a
  green or faster run.
- Do not make global worker-count changes, cache-reuse claims, CI relocation, or
  test-suite pruning the first move. Parallelism is explicitly deferred until
  the structural pass is exhausted.
- Do not delete a test merely because it is slow. First identify whether it
  duplicates a cheaper proof; retain a thin real-boundary smoke when the process,
  packaging, isolation, or CLI contract is what the test proves.
- Do not treat clone totals, dead-code advisories, or bootstrap-copy counts as
  reduction targets. They choose inspection points; runtime and behavior decide.
- Do not collapse intentional portability/generated surfaces without proving
  source-tree and installed-plugin entrypoints still work.
- Do not publish, push, release, close issues, run remote CI, or run Cautilus.
- Do not turn a local Linux result into a cross-host runtime promise.

## Boundaries

- This is local, reversible work on the current host/runtime profile. The real
  target is the closeout journey, including its expensive standing and proof
  phases, not an arbitrary microbenchmark.
- The current proof facts remain invariant: changed scope, freshness, coverage,
  failure visibility, recovery evidence, and consumer verdict must remain
  observable through the same or a stronger channel.
- A duplicate candidate must have a named owner and a clear structural response:
  deletion, in-process extraction with a thin boundary smoke, shared helper, or
  generated/machine-owned surface. “The scanner found it” is not an owner.
- A bootstrap candidate must distinguish removable per-run setup from the
  intentional portability fence. The existing canonical shim consistency gate
  is evidence that some copied bootstrap is deliberate, not permission to
  preserve every copy forever.
- Any change to a validator, runner, gate, or verdict renderer is a proof-surface
  change. It requires delegated fresh-eye review; a verdict-logic repair owes a
  second review of the repaired surface.
- If a candidate misses the ten-second end-to-end bar, is too expensive to
  revert, or changes the proof being measured, restore it promptly and record
  the exact rejection. Do not rescue it with a longer ritual or parallelism.

## User Acceptance

The user can inspect one durable goal record and answer:

1. Which real closeout phase was targeted, and what repeated structural cost made
   it a better target than parallelism or a micro-optimization?
2. Which duplicated execution, unnecessary code, or bootstrap work was removed?
3. Did at least three comparable before/after observations show at least ten
   seconds of end-to-end relief on the same command, corpus, and host profile?
4. Do focused correctness and controlled failure checks show that proof was not
   weakened or hidden?
5. If no change shipped, which candidates were falsified, why was the search
   stopped, and what exact observation would reopen it?

Acceptance check matrix:

| Criterion | Decisive check | Required evidence |
| --- | --- | --- |
| Valuable target | Compare the real closeout journey and phase timings | command/corpus identity, phase owner, frequency, serial position, and proof sensitivity |
| Structural remedy | Inspect the owning code and candidate scorecard before editing | named owner, deletion/dedup/bootstrap rationale, blast radius, rollback path, and expected elapsed-time contribution |
| Material relief | Three comparable interleaved or alternating before/after observations | raw samples, fixed statistic, ten-second threshold, host/profile facts, and exclusions |
| Proof preservation | Separate correctness and controlled-failure channels | same failure visibility, freshness/coverage facts, recovery receipt, and consumer verdict |
| Honest closeout | Fresh-eye review and strongest applicable local gate | review artifact, final quality result, retro, claims check, and complete goal validator |

## Agent Verification Plan

### Low-Cost Checks

- Read the completed closeout goal, its retro, claims review, D51, recent
  lessons, and the North Star before selecting a remedy.
- Reproduce the current local closeout journey and split its elapsed time by
  named phase. Record command, base/head, corpus, environment, cache state when
  available, and whether the phase is standing, release-only, or proof-only.
- Run the structural inventories as advisory inputs: standing-test economics,
  nose clone families, dead-code candidates, structural-waste candidates, and
  hardcoded discovery. Rank candidates by likely end-to-end seconds, not by
  duplicate-line count.
- Read the exact implementation before shaping a remedy. In particular inspect
  repeated subprocess/CLI test paths, shared adapter/bootstrap loaders, and the
  current bootstrap-shim consistency contract.
- Fill the per-candidate quality scorecard before changing code. Stop a
  candidate early if no plausible path to ten seconds exists.

### High-Confidence Checks

- Pick one bounded candidate only after the scorecard names the producer,
  consumer, preservation invariant, falsifier, and rollback operation.
- Prefer deleting duplicate executable proof, moving ordinary behavior below a
  process boundary while retaining a thin boundary smoke, removing dead setup,
  or collapsing genuinely repeated bootstrap work. Do not hide assertions in a
  helper just to satisfy a duplicate scanner.
- Measure the candidate on the real closeout command with at least three
  comparable before and after observations. If the candidate is below ten
  seconds, revert immediately; do not spend an hour polishing a low-value
  result.
- Run correctness and controlled failure fixtures separately from timing. Check
  success, producer failure, stale/unproven evidence, non-zero status, failure
  names, recovery receipts, and no-fresh-marker behavior where applicable.
- If the change touches a proof surface, obtain the delegated fresh-eye review
  before locking claims. If verdict logic changed, perform the required second
  repaired-surface review.
- Finish with the strongest applicable local quality gate, a bound retro,
  claims review, synchronized artifacts, and the complete goal validator.

### External Or Live Proof

N/A — no remote, provider, release, publication, issue, or live behavior claim
is in scope.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Map the real closeout cost and rank structural candidates | A small speed delta is not enough; the next move must attack recurring structure | phase timing, candidate scorecards, and a stop/choose decision | pending |
| B | Spike the highest-value deletion/dedup/bootstrap candidate | Test economic value before a broad refactor | narrow before/after timing, preservation checks, and immediate revert decision | pending |
| C | Implement the smallest structural remedy | Ship only a change whose owner, boundary, and proof contract are clear | focused tests, generated/plugin sync where needed, and three comparable runs | pending |
| D | Lock proof and prepare the next decision | Runtime relief is provisional until separately observed and reviewed | final quality, fresh-eye review, retro, claims review, validator, and next-session handoff | pending |

## Candidate Order and Current Leads

These are inspection leads, not preselected fixes:

- **Repeated executable proof/process starts:** the standing-test inventory found
  232 subprocess-bearing test files overall, 212 nested CLI files, and 194
  standing files. First determine which repeated process bodies duplicate
  in-process proof and which genuinely prove a delivery boundary.
- **Bootstrap work:** the clone inventory found a 22-member repeated bootstrap
  family. Inspect whether the per-process work beyond the intentional portability
  fence is removable or shareable; preserve the source/installed-tree contract.
- **Repeated adapter validation:** a 17-member family around
  `validate_adapter_data` is large enough to inspect, but it may be
  design-shaped rather than safely extractable. Measure startup and import cost
  before proposing a shared abstraction.
- **Unnecessary code:** dead-code advisory findings are candidates only. Remove
  a finding in this goal only if it lies on a recurring closeout/test path or its
  deletion unlocks a measurable reduction elsewhere.
- **Parallelism:** explicitly deferred until the above candidates are either
  shipped or honestly falsified.

## Prior Closeout Audit

The previous closeout-related goal was strong on proof discipline but weak on
economic targeting.

What was done well:

- It measured the current critical path instead of trusting old telemetry.
- It separated timing, correctness, controlled failure, and claims review.
- It preserved the focused proof after the worker-cap candidate failed the fixed
  materiality test; it did not weaken a gate to manufacture relief.
- The first claims review caught stale or mismatched evidence, and the repaired
  claims received a final independent read.

What needs to change:

- The chosen candidate could at most produce a small improvement, while the
  investigation and rollback burden became large. That is a selection failure,
  not a proof failure.
- A packet-path mismatch and stale timing details created avoidable closeout
  repair work. The next goal freezes command, artifact path, and timing bundle
  before broad validation.
- The structural inventories should have been used before spending another
  long cycle on a low-yield runner-shape experiment.

## Operator Decision Queue

1. Confirm whether ten seconds is the right initial end-to-end bar, or whether
   the user wants a higher bar such as twenty seconds.
2. Confirm whether the first closeout target is the full read-only quality path,
   the standing pytest phase, or the mutation/changed-line phase. Default:
   start with the largest recurring phase in the local profile.
3. Clarify the intended meaning of “bootstrap removal”: repeated per-run setup
   around tests/CLI entrypoints, copied skill-runtime shims, or both. Default:
   inspect both, but preserve intentional portability fences until measured.

## Coordination Cues

Routing: quality first for runtime/candidate selection; critique and impl join
only after one structural candidate is fixed. Use retro at closeout and handoff
to carry rejected candidates and the next owner.

Gather: n/a — no external source is being introduced.

Release: n/a — no release surface is in scope.

Issue closeout: n/a — no tracked issue is being resolved.

## Discuss Before Activation

- Discuss before activation: RESOLVED in this session — the user supplied the
  main direction: structural deletion and deduplication first, bootstrap cleanup
  next, parallelism later. The initial ten-second bar, the largest recurring
  local phase as the default target, and inspection of both removable setup and
  intentional bootstrap fences are the stated defaults. The goal remains local,
  reversible, and does not authorize any external or irreversible action.

## Slice Log

No slices executed; this draft replaces the earlier low-value broad-vs-focused
equivalence experiment as the next-session goal.

## Context Sources

1. [Design North Star](../../docs/design-north-star.md) — judgment on
   reversible work, and distinct evidence at proof boundaries.
2. [Completed bottleneck goal](2026-08-04-reduce-current-closeout-bottleneck.md)
   — local baseline, falsified worker-cap candidate, and closeout proof record.
3. [Bound retro](../retro/2026-08-04-reduce-current-closeout-bottleneck-retro.md)
   and [claims review](../critique/2026-08-04-reduce-current-closeout-bottleneck-claims-review.md)
   — recorded waste, repairs, and no-safe-change disposition.
4. [Recent lessons](../retro/recent-lessons.md) — repeat traps around stale
   artifacts, broad verification cost, and proof-boundary review.
5. [D51](../../docs/deferred-decisions.md#d51-release-branchci-barrier-and-quality-gate-runtime)
   — owner and reopen context for quality-gate runtime work.
6. Current quality inventories — standing-test economics, structural waste,
   clone families, dead-code advisory, and runtime summary; all are advisory
   signals pending candidate-level measurement.

## Interview Decisions

- User priority: actual speed improvement over an elegant microbenchmark.
- User priority: duplicate execution/code removal and bootstrap cleanup before
  parallelism.
- Economic rule: an approximately eight-second saving with an hour-scale
  rollback burden is not a success; the initial end-to-end bar is ten seconds.
- Proof rule: preserve the closeout contract and use separate timing,
  correctness, failure, and independent-review channels.
- Superseded direction: broad-vs-focused semantic equivalence is not the next
  session's goal unless a later structural change makes it necessary.

## Plan Critique Findings

The first draft was too conservative: it turned an observed small speed delta
into a long equivalence investigation before asking whether the candidate could
ever repay the effort. This revision moves economic triage and structural
deletion ahead of equivalence work. Equivalence remains a preservation check
only when a selected candidate changes producer/consumer shape.

## Off-Goal Findings

The portability bootstrap fence, global runner policy, CI relocation, release
ordering, and historical telemetry remain separate concerns unless the selected
structural candidate directly proves they are on the measured path.

## Final Verification

Retro: not yet applicable — this goal is an inactive draft with no executed
slice.

Host log probe: not yet applicable — no goal-scoped runtime window exists.

Disposition review: not yet applicable — no closeout claims exist until
activation.

## User Verification Instructions

Review the structural-first order, the ten-second economic bar, and the three
decision defaults. Activate with:

    /goal @charness-artifacts/goals/2026-08-04-reduce-closeout-runtime-structural-waste.md

Activation authorizes local measurement and reversible implementation only. It
does not authorize publication, push, release, issue close, Cautilus, or proof
weakening.

## Auto-Retro

Retro dispositions: none — no slices have executed under this revised goal.

Structural follow-up: the earlier closeout experiment's main lesson is to
select for recurring structural seconds before selecting for elegant runner
equivalence.
