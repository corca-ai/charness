# Debug Review: review closeout preflight
Date: 2026-09-06

## Problem

Goal 805 paid for a delivered review that issue closeout refused for its scope,
then repaired a non-durable citation after another delivered review. The user
authorized a bounded reduction of this review-to-closeout rework, not a new Goal.

## Correct Behavior

Given the supported issue-owned review launch, derive resolution purpose and
qualified targets, and refuse malformed inputs or ineligible selected citations
before reviewer launch. Generic reviews remain available for other purposes.
After correction, the unchanged final consumer must still enforce delivery,
identity, membership and per-target proof. Measure worker calls and interventions;
do not infer general delegation savings.

## Observed Facts

The retained Goal 805 implementation critique records the scope refusal and its
correction. Current `run_review.py` accepts free-form `--scope`; current
`issue_critique_observer.py` requires prefix `issue-resolution`. The prior issue
documentation routed directly to the generic runner, with no issue-owned launch.
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

Five Whys: review must be repeated → final purpose/citation conditions are met
only after delivery → the generic launch does not compose issue readiness →
issue docs expose the generic producer directly → transport and consumer tests
never exercise that intended journey with a wrong-purpose or ignored citation.

The initial prefix-deletion hypothesis was rejected after causal critique and a
reproduced counterexample: exact targets plus passing diagnostic observations
without a repair become wrongly usable when the purpose check is removed.
The [causal disposition](../critique/2026-09-06-review-closeout-cause.md) preserves
that refusal. Repair belongs in a small issue-owned launch, not looser approval.

## Invariant Proof

- Invariant: the issue launch supplies known purpose and targets, and rejects
  malformed inputs or ineligible selected citations before paid review; final
  issue consumers still validate the actual delivered result.
- Producer Proof: the composed fake-backend regression observes two baseline
  calls including correction versus one call through the new issue command.
- Final-Consumer Proof: both public commands refuse wrong purpose and accept
  the corrected baseline and candidate; bad selected citations start zero workers.
- Interface-Shape Sibling Scan: scope, exact targets, evidence durability.
- Non-Claims: no live/model efficiency, semantic approval, host update or provider
  write. Changed-line proof is clean for all eight changed execution files at
  `1563e116b`; broad integration verification is recorded separately.

## Detection Gap

`test_semantic_review_command.py` proves delivery; bundled consumer tests seed
matching prefixes, so their composition never varies this independent axis.
The composed regression now varies purpose independently of exact targets, and
checks evidence before packet freezing. Selected-file tests prohibit discovery
and compare the existing directory/glob and exemption decisions. The new command
is scoped under the existing issue CLI; it does not add another runner or gate.

## Sibling Search

- Mental model: successful generic review delivery implies intended-consumer use.
- cross-file: review runner and issue critique observer; durability gate.
- same layer: legacy singleton scope | decision: intentional plain-text or
  non-rendering boundary | proof: static scan; it lacks per-target observations.
- abstraction up: report/receipt/ledger scope joins | decision: same class,
  diagnostic-only for this slice | proof: executable fixture; preserve joins.
- specialization down: structured target validation | decision: same bug, fix
  now | proof: executable fixture plus source; retain all target refusals.
- mental-model: ignored citations in reviewed Markdown | decision: same bug,
  fix now | proof: real fake-backend launch refuses before packet/worker creation,
  and proceeds after durable evidence repair while unrelated dirty docs remain.

## Seam Risk

- Interrupt ID: review-closeout-preflight
- Risk Class: none
- Seam: local review launch and issue proof consumption
- Disproving Observation: historical consumer refusal after delivered review
- What Local Reasoning Cannot Prove: total long-delegation benefit
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/critique/2026-09-06-review-closeout-code.md

## Prevention

`test_issue_bundled_closeout.py` covers the real launch-to-consumption journey;
`test_quality_universe_selection.py` and selected durability parity tests prevent
whole-corpus discovery and exemption drift. The independent
[code critique](../critique/2026-09-06-review-closeout-code.md) found no blockers.
Keep historical receipts immutable and exact-byte approval binding intact.

The [descriptive comparison](../probe/2026-09-06-review-closeout/comparison.json)
retains actual local fixture outputs and elapsed observations, without a timing
threshold or live-savings inference. Operator clarification removed non-Git
compatibility; alternate provider paths are unchanged. The latest independent
bounded call-graph check and 77 focused tests cover that deletion.

An implementation lane separately failed scope validation and automatic retention
removed its uncommitted checkout. The parent recovered all 11 files byte-for-byte
from the captured final diff before correction; [recovery evidence](../probe/2026-09-06-review-closeout/recovery.json)
records that ineligible run and its cost. Retention behavior is an explicit
follow-up, not a repaired capability or evidence of overall delegation savings.
