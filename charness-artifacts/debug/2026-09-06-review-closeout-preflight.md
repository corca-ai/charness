# Debug Review: review closeout preflight
Date: 2026-09-06

## Problem

Goal 805 paid for a delivered review that issue closeout refused for its scope,
then repaired a non-durable citation after another delivered review. The user
authorized a bounded reduction of this review-to-closeout rework, not a new Goal.

## Correct Behavior

Given an intended issue-closeout review, when its purpose, targets or evidence
already violate deterministic consumer conditions, fail before reviewer launch.
After correction, the unchanged final consumer must still enforce delivery,
identity, membership and per-target proof. Measure worker calls and interventions;
do not infer general delegation savings.

## Observed Facts

The retained Goal 805 implementation critique records the scope refusal and its
correction. Current `run_review.py` accepts free-form `--scope`; current
`issue_critique_observer.py:336` requires prefix `issue-resolution`. Their intended
relationship and existing preflight alternatives are under investigation.
Prior cardinality and ephemeral-carrier records caution against weakening exact
membership or mistaking author-disk existence for durable evidence.

## Reproduction

Executed the real semantic runner with a deterministic fake backend, then both
public closeout commands with the resulting unchanged report/receipt/ledger.
One worker call produced transport approval; both consumers refused only the
scope prefix. The observed projection is
`charness-artifacts/probe/2026-09-06-review-closeout/baseline.json`.
Historical reports stay immutable.

## Candidate Causes

- Candidate: review launch validates transport readiness without the selected
  closeout consumer's deterministic eligibility conditions.
- Alternative: an existing issue-owned route already supplies those conditions,
  and only the direct generic caller omitted it.

## Hypothesis

With identical issue targets and readable evidence, an arbitrary scope can reach
worker launch but cannot pass issue consumption. disconfirmer: find an existing
launch refusal or a supported consumer that accepts this purpose unchanged.

## Verification

Confirmed by the replay. Independent bounded source investigation found no
issue-owned launcher; bundled-closeout docs route to the generic runner. Existing
dry-run validates transport, not intended-consumer eligibility. Scope prefix is
caller-written text, not independent semantic authority. Structured targets have
separate exact packet/result membership, per-target pass and evidence checks.

## Root Cause

Five Whys: a delivered review cannot close → consumer requires a free-text
prefix → generic producer accepts other text → issue docs route directly to
that producer → old descriptive-scope check remains beside newer structured
target/observation checks without a composed launch-to-consumption test.
Candidate repair: retire the redundant prefix only for validated structured
carriers; keep legacy prefix and every delivery, identity and target check.
Whether this loses meaningful purpose detection is the causal review question.

## Invariant Proof

- Invariant: known issue-closeout ineligibility is surfaced before paid review;
  final issue consumers still validate the actual delivered result.
- Producer Proof: baseline replay launched one simulated worker, exit 0.
- Final-Consumer Proof: both public commands exit 2 with the same sole refusal.
- Interface-Shape Sibling Scan: scope, exact targets, evidence durability.
- Non-Claims: no new code, benefit, host update or provider write established.

## Detection Gap

`test_semantic_review_command.py` proves delivery; bundled consumer tests seed
matching prefixes, so their composition never varies this independent axis.
Add one real fake-backend-to-final-consumer scenario. No new command is proposed.

## Sibling Search

- Mental model: successful generic review delivery implies intended-consumer use.
- cross-file: review runner and issue critique observer; durability gate.
- same layer: legacy singleton scope | decision: intentional plain-text or
  non-rendering boundary | proof: static scan; it lacks per-target observations.
- abstraction up: report/receipt/ledger scope joins | decision: same class,
  diagnostic-only for this slice | proof: executable fixture; preserve joins.
- specialization down: structured target validation | decision: same bug, fix
  now | proof: executable fixture plus source; retain all target refusals.
- mental-model: ignored citations in reviewed Markdown | decision: same class,
  diagnostic-only for this slice | proof: prior Goal 805 push refusal; separately
  examine moving the existing citation check before input freezing.

## Seam Risk

- Interrupt ID: review-closeout-preflight
- Risk Class: none
- Seam: local review launch and issue proof consumption
- Disproving Observation: historical consumer refusal after delivered review
- What Local Reasoning Cannot Prove: total long-delegation benefit
- Generalization Pressure: none

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Pending causal disposition. Do not alter historical receipts, infer semantic
equivalence from formatting, remove identity checks, or launch a new release.
