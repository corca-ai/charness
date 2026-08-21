# Changed-Line Review Consumer Gaps Debug Review
Date: 2026-08-21

## Problem

The committed candidate passed standing pytest, but the exact-base changed-line
producer returned `status: blocked` with eight mapped files and uncovered
changed lines. The new fresh-eye consumer/refusal paths were therefore not
proved by the broad suite.

## Correct Behavior

Given a committed candidate and its exact base, the changed-line producer must
either measure every changed source line or name the precise counterexample
needed before merge. A green standing suite is not a substitute for that
producer-level proof.

## Observed Facts

- Base: `38775dfeb8d1e5574663d7ef461d19a63e252841`.
- Head at reproduction: `029de117f425d7c80a4a7df8419887e74f50e280`.
- Standing pytest passed, but the consumer returned `blocked` for 8 files.
- Missing classes include dynamic loader refusal, strict issue payload shape,
  close/readback failures, Markdown indented/fence parsing, typed delegation
  refusal, and resolution-observer import/field/error branches.

## Reproduction

Run `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .
--base-sha 38775dfeb8d1e5574663d7ef461d19a63e252841`. It reports
`blocking_targets` for `scripts/critique_reviewer_evidence.py`,
`skills/public/issue/scripts/{issue_backend,issue_close,issue_critique_observer,
issue_critique_observer_support,issue_markdown_lib,issue_resolution_critique,
issue_resolution_observer}.py`.

## Candidate Causes

- The broad suite exercises successful worker delivery more often than the
  newly extracted dynamic-import and malformed-input refusal branches.
- Refactoring moved ownership into support modules without moving or adding
  producer-level counterexamples for every fallback path.
- Closeout integration tests verify the aggregate result but do not reach every
  strict identity/readback exception arm.

## Hypothesis

The gap is a missing counterexample partition, not a false changed-line map.
Disconfirmer: run the gate's listed target lines through direct in-process
tests; if the same lines remain absent, the test loader or mapping is wrong;
if they become covered, the missing partition hypothesis is confirmed.

## Verification

- Result: confirmed — the gate names exact executable lines and the existing
  focused tests do not invoke several refusal/import branches.
- Repair plan: add direct counterexamples at the owning consumer/support tests,
  then rerun the exact command after committing the test repair.

## Root Cause

The repair changed verdict-producing code and split shared helpers, but its
coverage contract was validated only after commit. The broad suite proved
behavioral integration while leaving rare refusal branches unmeasured.

## Invariant Proof

- Invariant: every verdict/refusal branch introduced by the worker approval
  chain has an executable counterexample in the exact-base changed-line proof.
- Producer Proof: the changed-line producer emits each missing `path:line`
  target and refuses to render a clean verdict until covered.
- Final-Consumer Proof: standing pytest proved the aggregate consumer, and the
  committed exact-base rerun at `362221694004c1abbea8ad9ab2e808b0af9229d1`
  returned `status: clean`, with 52/52 changed pool files mapped and no
  blocking targets.
- Interface-Shape Sibling Scan: issue observer, resolution observer, Markdown
  parser, close backend, and worker evidence loader share the same fail-closed
  boundary pattern.
- Non-Claims: no fresh-eye approval, release, host behavior, or publication.

## Detection Gap

- Changed-line gate | broad pytest did not fire the missing branches | repaired
  with one direct counterexample per listed target family and verified the
  committed exact-base gate as clean.
- Source/plugin parity | mirror checks passed but do not measure runtime branches
  | run the same focused tests against source-owned modules and keep parity
  validation in the closeout.
- Human review | round-2 reviewers found semantic risks, not line coverage |
  retain the deterministic gate as the owner of this proof.

## Sibling Search

- Mental model: successful aggregate evidence is mistaken for branch-complete
  proof.
- same layer: `tests/quality_gates/test_issue_critique_observer.py` | decision:
  same bug, fix now | proof: gate target map and existing fixture boundaries.
- abstraction up: `scripts/critique_reviewer_evidence.py` and the shared worker
  carrier | decision: same class, diagnostic-only for this slice | proof: static
  target list; worker carrier is already covered by its focused suite.
- specialization down: `issue_markdown_lib.py` and observer support parsing |
  decision: same bug, fix now | proof: exact missing lines.
- cross-file: `tests/quality_gates/test_issue_skill.py` | decision: valid
  follow-up outside the slice | proof: current close integration fixtures do
  not own every new strict payload exception; follow-up: deferred
  `docs/handoff.md` Current State.

## Seam Risk

- Interrupt ID: changed-line-review-consumer-gaps-2026-08-21
- Risk Class: repeated-symptom
- Seam: changed source -> focused mapper -> test partition -> merge proof
- Disproving Observation: a committed rerun returns `status: clean` with no
  blocking targets for the same base/head scope.
- What Local Reasoning Cannot Prove: provider-host behavior or fresh-eye quality.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md

## Prevention

Make exact-base changed-line proof a required post-commit step for every verdict
surface. When it emits targets, bind repairs to its `blocking_targets` instead
of adding blanket coverage or lowering the gate; record the gap in this artifact
until a committed rerun proves the producer-to-consumer chain.
