# Focused Mutation Coverage Canonical-Runner Code Critique
Date: 2026-08-05

## Execution

Three parent-delegated, unnamed Codex reviewers ran over the pending candidate:
problem framing, diagnostic/boundary ownership, and operational counterweight.
Findings were received from all three. The reviewer envelope was unbound on
this Codex host; each reviewer was instructed to remain read-only and the
parent-side boundary rail was used.

## Decision Under Review

Make the changed-line mutation producer launch its mapped focused tests through
`scripts/run_standing_pytest.py`, preserving the existing test scope and
coverage/consumer proof while inheriting canonical xdist scheduling and temp
isolation.

## Diff Scope

`scripts/prepush_focused_changed_line_coverage.py`, its checked-in plugin mirror,
focused producer/runner tests, and the active goal evidence.

## Capability at Stake

The local quality-gate owner needs a materially faster focused mutation verdict
without losing changed-line mapping, subprocess coverage, failure visibility,
release-only scope, or focused-artifact ownership.

## Failure Angles

- Problem framing: the measured owner is the focused producer's serial launch,
  not the CLI family or mapper scope; the canonical runner is the smallest
  structural remedy.
- Diagnostic/boundary ownership: hand-assembled `-n` flags would duplicate
  worker caps, xdist-version handling, affinity, and external-temp policy. The
  runner owns those concerns and the producer already instruments it as a child.
- Operational counterweight: `--include-release-only` is required because the
  canonical runner otherwise narrows the bare-pytest producer scope. Worker
  coverage must be behavior-tested, not inferred from command text.

## Counterweight Pass

- Act Before Ship: reuse the canonical runner; preserve release-only scope;
  prove two worker identities and exported subprocess coverage; pin exact
  deduplicated target flags.
- Bundle Anyway: retain the focused artifact path and existing producer failure
  / consumer verdict handling; keep the source/plugin mirror synchronized.
- Over-Worry: do not change mapper policy, verdict meanings, broad coverage,
  remote CI, or add a second cleanup system.
- Valid but Defer: concurrent invocations sharing the fixed focused artifact and
  further worker/cache tuning are outside this candidate.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/prepush_focused_changed_line_coverage.py` | action: fix | note: reuse the canonical standing runner so the producer selects targets while the runner owns execution policy.
- F2 | bin: act-before-ship | evidence: strong | ref: `scripts/run_standing_pytest.py` | action: fix | note: do not copy xdist worker/scheduler/temporary-root policy because a second owner would drift.
- F3 | bin: act-before-ship | evidence: strong | ref: `tests/quality_gates/test_mutation_coverage_producer.py` | action: fix | note: worker identity and exported lines are the observable preservation proof.
- F4 | bin: bundle-anyway | evidence: strong | ref: `tests/quality_gates/test_prepush_focused_changed_line_coverage.py` | action: fix | note: wrapper translation must preserve sorted targets and the old focused scope.
- F5 | bin: valid-but-defer | evidence: moderate | ref: focused coverage artifact path | action: defer | note: cross-invocation locking is a distinct producer lifecycle concern outside this candidate.

## Reviewer Tier Evidence

- Requested tier: `high-leverage`
- Requested spawn fields: `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`
- Host exposure state: requested_fields_sent
- Application state: n/a — this Codex host exposed no provider-side application confirmation signal.
- Delivery state: findings-received
- Envelope state: unbound; read-only behavior was enforced by the packet and parent boundary rail, not a host tool restriction.
- Reviewer delivery: findings-received from three distinct unnamed one-shot reviewers; durable delivery record: `2026-08-05-mutation-xdist-review-delivery.md`.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-08-04-203346-packet.md`

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-04-203346-packet.json`
- Packet SHA256: `ff238d00a25ef4ccad2c8e7f730d9f49a6f09be120809f34ee91d0f5832baf0b`
- Identity SHA256: `7a777ee403264e9206f1df817ae28f406443435a3fa48c00018a5c36a810caae`
- Review window: `mutation-xdist-critique-r1`; durable verification receipt: `2026-08-05-mutation-xdist-review-boundary-receipt.json`. The snapshot was taken before the parent edit and verification returned `parent-attributed` with no undeclared drift for the three edited paths.

## Boundary Ownership

- Producer: `prepush_focused_changed_line_coverage.py` selects mapped targets,
  launches focused coverage, and invokes the consumer.
- Runner owner: `run_standing_pytest.py` owns xdist activation, worker width,
  scheduler compatibility, and external temp isolation.
- Consumer: `check_changed_line_mutation_coverage.py` reads the focused artifact
  and renders the changed-line verdict.
- Verdict: moved-to-owner — scheduling policy moved to its existing owner; verdict logic and
  proof floors are unchanged.

## Deliberately Not Doing

- No hand-assembled `-n 16` fallback or second worker-policy owner.
- No mapper/test pruning, changed-line floor weakening, broad-proof relocation,
  remote/provider proof, push, release, issue close, or Cautilus run.

## Pre-Merge Action

All Act Before Ship findings were implemented in commit `3c241399`, including
the source/plugin mirror and the worker-level coverage test. The real committed
gate then passed with all five changed pool files analyzed and every changed
line covered.

## Next Move

Use the three matched full `run-quality --read-only` receipts and a separate
goal-claims review to lock the measured relief before closeout.
