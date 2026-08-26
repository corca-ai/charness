# Adapter Bootstrap Idempotence Debug Review
Date: 2026-08-27

## Problem

Only the `impl` adapter had been moved to a shared idempotent initializer.
The other 15 public entrypoints still mixed wrapper-specific writers and
plain path output with the lifecycle, so the shipped adapter surface did not
have one observable contract.

## Correct Behavior

All 16 entrypoints must resolve the same target boundary and produce one typed
`charness.adapter-bootstrap/v1` receipt. A fresh target initializes, a valid
existing target is unchanged, dry-run never mutates, and invalid or
unestablished state refuses before mutation unless explicit force is requested.

## Observed Facts

- The pre-fix source had idempotence localized to `impl`; `critique` and
  `issue` also carried bespoke write paths.
- The repaired wrappers share the common lifecycle in both source and plugin
  trees and no longer print a second returned path after the receipt.
- The 16-entrypoint contract matrix passed `32`; the related suite passed
  `76`; the standing classification passed `37`; the combined target passed
  `69`.

## Reproduction

Run `python3 -m pytest -q tests/quality_gates/test_adapter_bootstrap_contract.py`
from the named proof worktree. Each parametrized entrypoint is exercised in a
temporary repository for fresh initialization, repeat invocation, dry-run,
and invalid-version refusal. The invalid case is the cheapest check that an
unhonored declaration does not silently overwrite or fall back.

## Candidate Causes

- The first shared helper was adopted by one wrapper instead of the complete
  shipped public set.
- Bespoke writers made output shape and mutation ownership local to individual
  skills.
- Callers treated a returned path or readable YAML as success without a
  common version/refusal receipt.

## Hypothesis

The defect is a lifecycle-ownership split, not a per-skill YAML rendering
failure: routing every wrapper through one initializer will make repeat and
refusal behavior identical without changing resolver-specific data fields.
disconfirmer: execute the all-entrypoint invalid-version and repeat matrix and
look for any wrapper that mutates, emits an extra line, or reports a different
state.

## Verification

Confirmed locally. The clean proof target emits the common receipt, preserves
valid existing destinations, refuses invalid/unestablished state without
force, and passes source/plugin parity plus the focused and standing gates.
The exact-target aggregate eval is intentionally not a green claim because a
pre-existing representative-skill-contracts checker still expects two critique
phrases removed from the current skill source.

## Root Cause

The adapter bootstrap contract had no common lifecycle owner: one entrypoint
had idempotence while the remaining wrappers could choose their own output and
write behavior. The common library and all 16 thin wrappers close that split.

## Invariant Proof

- Invariant: every public initializer has one typed receipt and never silently
  mutates an invalid or unestablished destination.
- Producer Proof: the parametrized 16-entrypoint matrix invokes each wrapper
  against fresh, existing, dry-run, and invalid-version fixtures.
- Final-Consumer Proof: the consumer-classification standing gate reads the
  same source/plugin declarations and passed `37`.
- Interface-Shape Sibling Scan: canonical wrappers, plugin mirrors, and the
  common initializer were compared; the two trees are byte-identical where
  required.
- Non-Claims: no installed-host, hosted, scheduler, conditional-trigger, or
  consumer-repository behavior is inferred from local proof.

## Detection Gap

The existing implementation test covered the `impl` adapter but did not
enumerate every public initializer or assert one receipt shape. The new matrix
and classification gate close that gap; the stale aggregate checker remains a
separate source/checker mismatch and is recorded as a non-claim.

## Sibling Search

- same layer: all 16 `skills/public/*/scripts/init_adapter.py` placements |
  decision: same bug, fix now | proof: executable matrix.
- abstraction up: `scripts/adapter_init_lib.py` |
  decision: same bug, fix now | proof: focused boundary tests and all wrapper
  execution.
- specialization down: `skills/public/critique/scripts/init_adapter.py` and
  `skills/public/issue/scripts/init_adapter.py` |
  decision: same bug, fix now | proof: executable matrix.
- adjacent consumer: `skills/public/issue/scripts/issue_tracker_cli.py` |
  decision: same class, diagnostic-only for this slice | proof: classification
  gate only; it is a direct consumer, not an initializer, so behavior remains
  outside #692.
cross-file: `scripts/adapter_init_lib.py` and
`skills/public/issue/scripts/issue_tracker_cli.py`.
Over-reach check: each listed initializer was found in the complete
`rg --files` inventory and executed by the parametrized matrix; the adjacent
consumer is listed only because its direct adapter read is independently named
by the classification contract.

## Seam Risk

- Interrupt ID: adapter-bootstrap-unhonored-state-2026-08-27
- Risk Class: contract-freeze-risk
- Seam: initializer wrapper -> typed receipt -> adapter consumer
- Disproving Observation: any matrix entry mutates invalid/unestablished state,
  emits a second output line, or diverges between source and plugin export.
- What Local Reasoning Cannot Prove: installed-host adoption, hosted provider
  behavior, scheduler execution, and every consumer repository.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved locally
- Critique Required: no — explicit operator direction omitted forced fresh-eye
  review and this host exposes no Agent/subagent capability.
- Next Step: impl
- Handoff Artifact: none — explicit operator direction omitted handoff update.

## Prevention

Keep public wrappers thin and route lifecycle decisions through the common
initializer. Retain the 16-entrypoint matrix, the consumer-classification
gate, and explicit clean named-worktree proof while treating the stale
aggregate contract as a separate friction-removal item.
