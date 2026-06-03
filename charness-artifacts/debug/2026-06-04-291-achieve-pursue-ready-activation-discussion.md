# Debug Review: #291 Achieve Pursue-Ready Activation Discussion
Date: 2026-06-04
Issue: #291

## Problem

`achieve` can report `pursue_ready: true` and exit 0 while also warning that
consequential activation discussion is only surfaced, not resolved.

## Correct Behavior

Given a goal with consequential activation decisions, when the discussion summary
is missing or not explicitly resolved, then `check_goal_artifact.py
--pursue-ready` must report that the goal is not activation-ready and return a
nonzero exit status. A shaped-but-unresolved artifact may report `shape_ready:
true`, but `pursue_ready` and `activation_ready` must be false.

## Observed Facts

- Issue #291 records the mismatch: `pursue_ready: true` appeared together with
  an activation-discussion warning.
- `goal_artifact_discussion.py` used `discussion_ready` to mean a non-empty
  summary exists.
- `goal_artifact_lib.py` used `not placeholders and discussion_ready` as
  `pursue_ready`.
- CLI wrappers summarize `pursue_ready` as `PURSUE_READY: yes`, so exit 0 and
  the concise line can hide the warning from operators.
- Existing tests pinned the bad state: unresolved discussion expected
  `pursue_ready is True` and `PURSUE_READY: yes`.
- Fresh-eye causal review confirmed the consumer-boundary failure: a
  deterministic artifact floor was treated as final operator readiness.

## Reproduction

Before the fix, a draft goal containing a consequential `Non-Goals` entry plus a
non-empty but unresolved `Discuss before activation:` line returned
`pursue_ready: true` and exit 0 from `--pursue-ready`.

## Candidate Causes

- A naming bug: `discussion_ready` meant "summary present" instead of
  "discussion resolved."
- A consumer-boundary bug: CLI exit status and `PURSUE_READY: yes` exposed the
  misleading boolean more strongly than the warning.
- A test-contract bug: tests encoded "warning-only but true" as expected
  behavior after the earlier #279 closeout.

## Hypothesis

If discussion readiness distinguishes summary presence from explicit resolution,
and `pursue_ready` aliases activation readiness rather than shape readiness,
then unresolved consequential discussion will fail closed while resolved goals
still pass.

## Verification

Planned focused proof:

- Targeted `test_goal_artifact_lib.py` cases for hidden, surfaced-unresolved,
  explicit resolved, stale Slice Log, N/A, issue-number-leading, and fenced
  summaries.
- CLI helper tests proving unresolved discussion returns nonzero and
  `PURSUE_READY: no`.
- Prose pinning in `test_achieve_before_activation.py`.
- Local artifact check on this active goal should pass because its discussion is
  marked `RESOLVED in-thread`.

## Root Cause

The checker collapsed three states into one readiness boolean: shaped enough for
Before-phase continuation, discussion summary present, and activation-ready. The
warning tried to carry the unresolved operator obligation, but the machine
contract and wrapper summaries exposed the state as ready.

## Invariant Proof

- Invariant: a goal is activation-ready only when it is shaped and all required
  consequential activation discussion is explicitly resolved.
- Producer Proof: `goal_artifact_discussion.py` should emit distinct
  `discussion_summary_present` and `discussion_resolved` states.
- Final-Consumer Proof: `goal_artifact_lib.py`, `check_goal_artifact.py`, and
  the `charness goal check` wrapper should return nonzero / `PURSUE_READY: no`
  for unresolved consequential discussion.
- Interface-Shape Sibling Scan: scan success booleans, exit codes, concise
  wrapper summaries, and generated/plugin mirrors for stale warning-only
  semantics.
- Non-Claims: this debug slice does not fix #292 or #284.

## Detection Gap

- activation-readiness checker | tests asserted `pursue_ready is True` with an
  unresolved discussion warning | update tests to require activation failure.
- CLI wrapper | concise output said `PURSUE_READY: yes` for unresolved discussion
  | update helper tests to require `PURSUE_READY: no`.
- prose contract | lifecycle text allowed helper output to say true while
  warning remained | update prose to separate `shape_ready` and
  `activation_ready`.

## Sibling Search

- Mental model: deterministic floors that prove a record exists were treated as
  proof that the human/operator decision was resolved.
- success-field axis: `pursue_ready`, `ok`, `verified`, and `resolved` names can
  overstate recorded state; decision: #291 fixes the active pursue-ready surface
  and final critique should scan nearby warning-plus-success fields.
- wrapper axis: JSON warning fields may be dropped in concise output; decision:
  pin CLI summary behavior for unresolved discussion.
- generated/export axis: plugin mirrors may preserve stale semantics; decision:
  sync plugin exports before validation.
- historical artifact axis: older complete goals may have unmarked summaries;
  decision: resolved goals can use an explicit `RESOLVED` marker, while old
  unresolved examples should fail `--pursue-ready` if rechecked.

## Seam Risk

- Interrupt ID: issue-291-achieve-pursue-ready-activation-discussion
- Risk Class: operator-visible-recovery
- Seam: goal artifact checker output to operator activation behavior.
- Disproving Observation: `pursue_ready: true` plus a warning was enough for a
  caller to offer activation before discussion was complete.
- What Local Reasoning Cannot Prove: whether all host wrappers outside this repo
  consume the new fields correctly.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-04-291-292-284-activation-index-and-skill-preflight.md

## Prevention

Do not let a field named `ready` or a zero exit status mean "recorded enough for
discussion." Readiness fields must identify the consumer boundary they prove:
shape-ready for continuing Before-phase, activation-ready for `/goal`.
