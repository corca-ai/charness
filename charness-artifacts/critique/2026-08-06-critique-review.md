# Critique Review
Date: 2026-08-06

## Decision Under Review

Move `validate-inventory-consumption-declaration` out of the first parallel
quality phase and run it after that phase has drained, so its runtime budget
measures the gate rather than avoidable CPU contention. Add a runner test that
pins this dependency-aware ordering.

Success means the gate still runs and fails normally, its recorded runtime is
closer to the observed standalone cost, and the full quality result retains all
existing checks. Out of scope: weakening the validator, changing its budget,
removing its coverage, or changing mutation-coverage production.

## Diff Scope

The concrete slice changes `scripts/run-quality.sh`, its checked-in plugin
export, and the runner's behavioral tests. It does not change the declaration
validator's verdict logic or the runtime budget.

## Failure Angles

- Problem framing: the move must address the measured false runtime signal,
  not merely make the quality run slower or hide a real regression.
- Diagnostic ownership: the runner owns phase scheduling; the validator owns
  inventory drift semantics. The change must not move the validator's verdict
  into a runner-specific approximation.
- Operational safety: a failure in the moved gate must still be surfaced in the
  final summary and must still affect the exit code.
- Communication: the reason for the barrier must remain legible in the runner
  comments and in the ordering test.

## Angles

- Weinberg diagnostic: the runner owns phase scheduling and runtime-sample
  timing; the declaration validator remains the owner of inventory drift.
- Gawande operational: `flush_phase` still records the gate, prints failures,
  updates the receipt, and propagates a non-zero result.
- Minto structure: the runner comment names the exceptional barrier and the
  test names the start-after-drain and failure-propagation contracts.

## Findings

- The first proposal review found that a source-order-only test would be too
  weak and that the initial packet did not bind the pending source diff. That
  packet was not used as final approval.
- The concrete review found the plugin export stale and the immediate flush
  under-tested. Both were repaired before this record was finalized.
- The final focused runner tests prove first-phase drain, isolated declaration
  completion before the next phase, runtime-record order, and failure receipt
  propagation. They do not prove a cross-host runtime improvement.

## Defect Class Cross-Link

This is the recurring runtime-measurement and gate-contention class recorded in
`charness-artifacts/retro/recent-lessons.md`; the repair preserves the gate and
changes only its owner-controlled scheduling boundary.

## Capability Gap

No new capability is required. The existing runtime recorder and runtime-budget
consumer remain the evidence path; the runner now supplies a less-contended
sample for this one known fan-out gate.

## Counterweight Pass

- The standalone 2.4s sample is not enough to prove all hosts behave the same;
  retain the runtime budget and continue collecting per-profile signals.
- A broad scheduler refactor is not justified by this one gate; keep the slice
  to one known contender and one ordering invariant.

## Counterweight Triage

- Act Before Ship: sync the checked-in plugin export and prove the immediate
  post-gate flush; both are applied in the concrete diff.
- Bundle Anyway: retain the existing budget and add explicit runtime-record
  order assertions; applied in the behavioral test.
- Over-Worry: a general dependency scheduler or serialization of all gates has
  no evidence and is out of scope.
- Valid but Defer: collect repeated post-change samples before retuning the
  15.5s budget; defer to the next session goal.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: plugins/charness/scripts/run-quality.sh:639 | action: fix | note: generated plugin export retained the old phase placement; synced from the source runner
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_runner_runtime_aggregate.py:160 | action: fix | note: behavioral proof now covers the first drain, isolated gate completion, next-phase start, and runtime-record order
- F3 | bin: valid-but-defer | evidence: contested | ref: .charness/quality/runtime-signals.json:validate-inventory-consumption-declaration | action: defer | note: runtime improvement is not a cross-host A/B claim; keep the budget and collect fresh samples under the next-session goal
- F4 | bin: over-worry | evidence: weak | ref: scripts/run-quality.sh:709 | action: document | note: no general scheduler or broad serialization is justified by this one measured fan-out gate

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: host did not expose a separate application-confirmation signal; the requested fields are recorded as requested only.
- Delivery state: findings-received.
- Boundary fingerprint: both review rounds returned `verdict: clean` with no drift before parent writes; snapshots are `/tmp/charness-runtime-critique-snapshot.json` and `/tmp/charness-runtime-concrete-snapshot.json`.

## Fresh-Eye Satisfaction

parent-delegated — proposal round and concrete-diff round used distinct unnamed
bounded reviewers; concrete findings were received before parent edits.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-06-runtime-isolation-final2-packet-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-06-runtime-isolation-final2-packet-packet.json`
- Packet SHA256: `0bcf3a9347240c3c1780363beaf36f2fa55585fa3227c6f7858cdbdb9cfb5ea6`
- Identity SHA256: `977fdeb998c145ac62979e631b40389ebe40a964bb389f73e0def09c3a8dceba`

## Boundary Ownership

- Producer: `scripts/run-quality.sh` produces the phase schedule and per-gate elapsed sample.
- Consumer: the runtime-budget checker consumes the sample, while the quality runner consumes the validator exit code.
- Owning surface: quality runner phase orchestration.
- Verdict: owned-correctly

## Pre-Merge Action

Complete the generated-surface sync, run the full quality closeout, and keep the
runtime-budget residual visible if a host still reports a violation. Do not
raise or remove the budget merely to obtain a green run.
