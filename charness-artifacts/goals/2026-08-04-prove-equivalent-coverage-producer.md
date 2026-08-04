# Achieve Goal: Prove whether broad coverage can replace focused closeout coverage safely

Status: draft
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-prove-equivalent-coverage-producer.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: draft/backlog awaiting activation; no implementation work
  is authorized until the user confirms this next priority.
- Current slice: inactive draft; no slice has executed.
- Current slice intent: establish whether broad plain coverage is semantically
  equivalent to the focused changed-line producer before any implementation.
- Next action: activate only after confirming this equivalence question is the
  next priority; activation does not authorize publication or gate weakening.
- Verification cadence: cheap deterministic checks at commit boundaries;
  fresh-eye proof at slice boundaries; final broad local proof at closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final proof uses the verification lock and the full applicable quality gate.
- Slice review packet: include intent, owning producer/consumer surfaces,
  semantic invariants, failure fixtures, timing method, non-claims, and
  out-of-scope lines before the fresh-eye review.
- History boundary: keep this frame current; move completed detail to the
  Slice Log, Final Verification, and Auto-Retro.

## Goal

Use the current closeout bottleneck evidence to determine whether the measured
broad plain-coverage path can produce the same changed-line proof as the
focused producer, then implement the smallest reversible improvement only if
semantic equivalence, failure preservation, and material timing relief are all
proven. The goal may end with an evidence-backed no-safe-change disposition.

## Non-Goals

- Do not weaken, skip, downgrade, or move the changed-line proof gate.
- Do not change the global `CHARNESS_PYTEST_WORKERS` default, prune the
  standing suite, reuse stale coverage, or promise a cross-host runtime.
- Do not publish, push, release, close issues, run remote CI, or run Cautilus.
- Do not call two command paths equivalent merely because both finish green;
  equivalence includes changed scope, mapped corpus, coverage export, freshness
  marker, consumer verdict, and failure behavior.
- Do not optimize the broad `over_slice` signal in the same goal.

## Boundaries

- This is local, reversible work on the current Linux host/runtime profile.
- The focused producer remains the reference implementation until a candidate
  proves semantic equivalence and material relief.
- Any producer, consumer, runner, or evidence-surface change gets delegated
  fresh-eye review; a verdict-logic repair owes a second repaired-surface read.
- A failed equivalence or relief test restores pre-change behavior and leaves
  only a durable no-safe-change record.
- External side-effect scope is none: no push, release, remote CI, provider
  proof, issue close, or live apply is authorized by this goal.

## User Acceptance

The user can inspect one goal record and answer:

1. Did broad and focused paths analyze the same changed pool and mapped test
   corpus at the same base/head identity?
2. Did they emit the same coverage facts, freshness marker, consumer verdict,
   and controlled failure behavior?
3. Did a candidate achieve at least three comparable observations of material
   relief beyond the fixed 5s median threshold?
4. If not, is the broad replacement explicitly rejected with an exact reopen
   trigger rather than presented as an optimization?

## Agent Verification Plan

### Low-Cost Checks

- Read the completed bottleneck goal, its bound retro and claims review, D51,
  and the north star before selecting the experiment.
- Inspect `mutation_coverage_producer.py`,
  `prepush_focused_changed_line_coverage.py`,
  `check_changed_line_mutation_coverage.py`, and `run_standing_pytest.py`.
- Reproduce exact focused and broad command/corpus identities before changing
  anything; record base/head, changed pool, mapped targets, xdist mode,
  `PYTEST_ADDOPTS`, cache/load availability, and host profile.
- Use temporary fixtures and compare exported coverage/marker/consumer payloads,
  not only elapsed time.

### High-Confidence Checks

- Establish an equivalence fixture where both paths receive the same changed
  files and mapped targets; compare changed-line coverage, blocking lists,
  freshness, success, and failure outputs field by field.
- Choose the median and 5s materiality threshold before candidate timing; run
  at least three interleaved baseline/candidate observations.
- Run controlled success, producer-failure, stale-marker, and uncovered-line
  fixtures through the consumer. Preserve non-zero status, failure names,
  recovery receipt, and no-fresh-marker behavior.
- Run focused correctness separately from timing and use delegated critique
  before implementation. If verdict logic changes, run the second repaired-
  surface review required by the operating contract.
- Finish with the strongest applicable local quality gate, bound retro, claims
  review, and complete goal validator.

### External Or Live Proof

N/A — no remote, provider, release, or live behavior claim is in scope.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Establish exact semantic equivalence between focused and broad coverage paths | The broad path was about 8s faster but used a different command shape; semantic identity must come before optimization | Command/corpus identity, field-by-field coverage/marker/consumer comparison, failure fixtures, and candidate decision | pending |
| B | Select one focused producer intervention only if A proves equivalence | A speed result that changes the proof question is not relief | Bounded packet, preservation invariant, falsifier, fixed median/5s threshold, and fresh-eye critique | pending |
| C | Implement and measure the smallest equivalent candidate | The goal earns a code change only after the proof question is unchanged | Focused tests, three interleaved baseline/candidate runs, controlled failures, and rollback/no-change result | pending |
| D | Lock proof and disposition the result | Timing is provisional until proof and claims survive separate observation | Final quality gate, retro, claims review, complete validator, and explicit relief/no-safe result | pending |

## Operator Decision Queue

none — this draft assumes a local, reversible experiment with no external
approval. Activation should confirm only whether this equivalence question is
the next priority; no publication or remote action is implied.

## Coordination Cues

Routing: quality — select the equivalence experiment and preserve the proof-cost
boundary; critique and impl join only after the semantic candidate is fixed.
Gather: n/a — no external source is being introduced.
Release: n/a — no release surface is in scope.
Issue closeout: n/a — no tracked issue is being resolved.

## Discuss Before Activation

Discuss before activation: resolved — this draft stays local and reversible;
activation authorizes measurement and critique only, with no push, release,
remote CI, or gate weakening. Any proof-surface change still requires the
separate fresh-eye and repaired-surface reviews.

## Slice Log

No slices executed; this is an inactive draft shaped from the completed
closeout experiment.

## Context Sources

1. [Design North Star](../../docs/design-north-star.md) — P1 favors judgment
   for this reversible experiment; P4/P5 require distinct evidence and observer
   if the producer/consumer verdict surface changes.
2. [Completed bottleneck goal](2026-08-04-reduce-current-closeout-bottleneck.md)
   — current host baseline, falsified worker-cap candidate, broad-coverage
   comparison, and exact reopen threshold.
3. [Bound retro](../retro/2026-08-04-reduce-current-closeout-bottleneck-retro.md)
   and [claims review](../critique/2026-08-04-reduce-current-closeout-bottleneck-claims-review.md)
   — recorded waste, no-safe disposition, and claims-review lessons.
4. [D51](../../docs/deferred-decisions.md#d51-release-branchci-barrier-and-quality-gate-runtime)
   — owner and reopen context for quality-gate runtime work.

## Interview Decisions

- Candidate seam: compare broad plain coverage with the focused producer because
  the broad run measured about 8s faster, but reject it unless proof inputs and
  outputs are semantically identical.
- Candidate controls: reject global worker caps, suite pruning, cache reuse,
  CI relocation, and coverage weakening because they change the proof question.
- Success test: median of at least three matched runs and fixed 5s relief
  threshold; if equivalence or failure preservation is incomplete, stop with
  no-safe-change rather than broaden the sample ritual.
- Proof channel: timing, controlled failure fixtures, focused correctness, and
  final quality remain separate channels.

## Plan Critique Findings

Initial shaping judgment: the broad path is a candidate, not a chosen remedy.
Before activation, run a bounded critique over the producer/consumer boundary
and the exact equivalence predicate. The review must challenge whether the
different command shape changes the proof, whether xdist/subprocess coverage
combines identically, and whether failure recovery remains visible. No
implementation is authorized by this draft alone.

## Off-Goal Findings

No off-goal findings at draft time. Global runner policy, CI relocation, release
ordering, cache design, and the historical telemetry stream remain separate.

## Final Verification

Retro: not yet applicable — this goal is an inactive draft with no executed slice.
Host log probe: not yet applicable — no activation or goal-scoped runtime window exists.
Disposition review: not yet applicable — no closeout claims exist until activation.

## User Verification Instructions

Review the four-slice boundary and confirm that broad-vs-focused semantic
equivalence is the next priority. Activate with:

    /goal @charness-artifacts/goals/2026-08-04-prove-equivalent-coverage-producer.md

Activation does not authorize publication or gate weakening. Completion may be a
safe implementation or an evidence-backed no-safe-change result.

## Auto-Retro

Retro dispositions: none — no slices have executed and no improvement has yet
been surfaced by this inactive draft.
Structural follow-up: none — no transferable waste has been observed in this
inactive draft; the prior goal's D51 follow-up remains the known owner anchor.
