# Closeout Bundle Evidence Identity and Release Retro

Date: 2026-08-06
Goal: charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md

## Context

This retro covers the first implementation slice of the active closeout-bundle
goal: the opt-in local orchestrator, its source/plugin mirror, packet identity
binding, focused refusal tests, and the two commits that recorded the slice.
The strongest evidence is the committed diff, focused tests, pre-lock closeout,
pre-commit gate, and changed-surface critique validation. The real execute
attempt's refusal on pre-existing hand-authored critique path violations is
strong evidence of fail-closed behavior, not evidence that the bundle completed.

## Window

The window ran from the activated goal and existing-owner inspection through
commits `7af2ec02` and `1fff1417` on 2026-08-06. It includes contract shaping,
implementation, two bounded review rounds, a standalone multi-angle critique,
packet rebinding after ledger edits, deterministic verification, and the
pre-lock closeout.

## Evidence Summary

- The execution contract and source/plugin CLI/library copies are checked in at
  `charness-artifacts/spec/2026-08-06-closeout-bundle-execution-contract.md`,
  `scripts/closeout_bundle.py`, and `plugins/charness/scripts/closeout_bundle.py`.
- `pytest -q tests/quality_gates/test_closeout_bundle.py tests/quality_gates/test_final_bundle_preflight.py tests/test_reviewed_input_identity_failures.py` passed 38 tests; ruff, Python lengths, copy invariants, boundary/duplicate ratchets, documentation preflight, goal shape, and the pre-lock closeout passed.
- The source/plugin packet identity was regenerated after the goal ledger commit
  was recorded; the standalone critique binds the current packet and identity.
- Packet Consumed: `charness-artifacts/retro/closeout-bundle-evidence-identity-and-release-retro-packet.md`.
- No metrics adapter commands are configured; this retro makes no token,
  tool-count, or host-efficiency claim.

## Waste

- packet-identity-churn (recurrence-class: release-proof-identity-churn): the
  goal ledger was corrected after the first commit, requiring packet regeneration
  and a second small bookkeeping commit. The repair was correct, but the packet
  should have been treated as dependent on every reviewed goal edit from the
  start.
- historical-authoring-scope-refusal: the real execute reached sync and pointer
  freshness, then refused on existing hand-authored critique path references.
  The refusal is useful safety evidence; the avoidable cost was discovering the
  full historical scope only after execution began rather than presenting an
  aggregated authoring diagnostic in the dry-run plan.
- The fresh-eye rounds, identity checks, mirror checks, and refusal tests were
  necessary proof at a cross-surface verdict boundary, not waste. No claim is
  made that the full review gate's ambient baseline failures were caused by this
  slice.

## Critical Decisions

- Keep bundle execution opt-in and direct-argv-only. Shell syntax and interpreter
  code modes refuse before any sync runner call, preserving the owner gate's
  boundary.
- Rebuild the final preflight after every mutating sync and verify the packet's
  durable identity on disk before the verification lock. This prevents a stale
  pre-sync scope or a runner-returned identity from becoming the closeout claim.
- Record the execute refusal and omit a receipt instead of repairing unrelated
  historical authoring drift opportunistically. The next slice can decide whether
  an aggregate diagnostic is worth a scoped contract change.

## Trends vs Last Retro

The prior same-day retro is bound to the umbrella closeout goal, not this goal;
its lessons still apply. This slice repeated packet identity churn, confirming
the existing `release-proof-identity-churn` recurrence class. It improved the
workflow by binding packet JSON, durable packet identity, and the standalone
critique record together before commit, but the closeout bundle still needs a
goal-specific claims/disposition reader before final publication.

## North Star Alignment

The North Star held where the bundle used judgment for reversible local work,
kept enforcement at the existing owner gates, and treated local green as
provisional. Distinct review windows, packet identity, and the execute refusal
kept a wrong closeout claim from escaping. The mis-application was allowing the
first ledger state to say the commit was pending after the implementation had
already been committed; that bookkeeping drift created a second identity cycle.
The failure signature was a durable evidence record lagging the reviewed tree.

## Expert Counterfactuals

- Engelbart's system-improving lens would have designed the packet producer,
  goal ledger update, and rebinding step as one H+LAM+T loop, with the commit
  reference treated as a declared input to the closeout record from the outset.
- Gawande's checklist lens would have placed “execute refusal path is a named
  non-claim” and “packet identity regenerated after goal bookkeeping” beside the
  pre-commit gate, reducing the second ledger-only commit without weakening it.

## Sibling Search

- same layer: `scripts/closeout_bundle_lib.py` packet/receipt sequencing | decision: same waste, fix now | proof: focused identity-drift and receipt tests plus the committed identity recheck.
- abstraction up: `scripts/final_bundle_preflight_lib.py` authoring scope | decision: valid follow-up outside the slice | proof: it reports planned paths but not an aggregate authoring-path diagnostic; follow-up: deferred closeout-bundle-authoring-diagnostics.
- specialization down: `scripts/check_doc_authoring_preflight.py` | decision: intentional boundary | proof: the real execute surfaced its refusal and the owner gate remained unchanged.
- mental-model siblings: critique packet and release proof bindings | decision: same waste, fix now | proof: packet JSON, durable packet, and standalone critique identity are now checked together.

## Next Improvements

- workflow: freeze the reviewed goal/spec/implementation set before ledger edits,
  and regenerate the packet immediately whenever a reviewed path changes
  (recurrence-class: release-proof-identity-churn).
- capability: consider a dry-run authoring diagnostic that aggregates all
  offending hand-authored paths without executing any sync or behavior command
  (recurrence-class: closeout-diagnostic-visibility).
- memory: carry the distinction between `ready`, `completed`, and a refused
  execute into the final claims review; a bundle receipt is never implied by a
  dry-run or a partial execute.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md
