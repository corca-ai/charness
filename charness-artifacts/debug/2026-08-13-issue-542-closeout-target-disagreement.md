# Issue 542 Closeout Target Disagreement Debug
Date: 2026-08-13

## Problem

A protected `close-with-comment` can carry one manual target declaration while
the CLI supplies a different issue target. The crosswalk reported the generic
`not_singleton` aggregate, hiding the conflicting authority boundary.

## Correct Behavior

Given exactly one manual declaration and one CLI target that differ,
`close-with-comment` refuses before any backend call with
`target_disagreement` and names both targets. Multi-target commit carriers and
true supersets retain their aggregate `not_singleton` refusal.

## Observed Facts

- `issue_close._authorize_direct_close()` passes the parsed declaration as
  `invoked_targets` and its `--repo/--number` target as `carrier_targets`.
- `authorize_closeout()` previously merged both sets before checking
  singleton-ness, so the source-specific disagreement was indistinguishable.
- The ingress test confirms authorization runs before the backend close path.

## Reproduction

- `authorize_closeout([514], [518], "close-with-comment", ...)` previously
  returns `not_singleton`, despite each authority source being singleton.

## Candidate Causes

- The generic crosswalk treated every carrier source as two halves of one text
  carrier.
- The caller/validator interface did not encode that manual declaration is an
  assertion about a separately supplied CLI target.
- Tests asserted aggregate refusal but did not distinguish the source contract.

## Hypothesis

- Check source-scoped singleton equality only for `close-with-comment` before
  generic aggregation; disconfirmer: a commit-message disagreement changes from
  `not_singleton`, or the mismatch reaches a backend call.

## Verification

- Result: confirmed — focused crosswalk and closeout-ingress suites cover the
  distinct refusal, preserved aggregate behavior, and zero-call refusal path.

## Root Cause

The validator had one generic target-set model for two different semantics:
commit-carrier references may aggregate, while a manual declaration must equal
the independently supplied CLI target.

## Invariant Proof

- Invariant: when `issue_close` supplies a manual declaration and CLI target,
  the final close ingress must refuse their unequal singleton identities before
  any backend close operation.
- Producer Proof: crosswalk unit test emits `target_disagreement` for 514 vs
  518 only under `close-with-comment`.
- Final-Consumer Proof: closeout authorization ingress test receives the
  refusal before the backend path; the CLI error contains `target_disagreement`.
- Interface-Shape Sibling Scan: commit and staged carriers keep aggregate
  semantics; their disagreement test remains `not_singleton`.
- Non-Claims: no hosted GitHub close was attempted and no issue state changed.

## Detection Gap

- Crosswalk tests did not model the one-declaration/one-CLI authority split;
  add source-specific and ingress regression coverage.

## Sibling Search

- Mental model: target-set source labels carry authorization semantics, not just
  diagnostics.
- carrier source: evidence_boundary_crosswalk.py | decision: source-scoped
  branch | proof: focused unit tests.
- close ingress: issue_close.py | decision: no behavior change | proof:
  pre-backend ingress test.
- cross-file: commit-hook carrier tests | decision: preserve aggregate branch |
  proof: existing aggregate regression.

## Seam Risk

- Interrupt ID: issue-542-closeout-target-disagreement
- Risk Class: none
- Seam: CLI target and manual declaration through crosswalk authorization to
  backend close ingress.
- Disproving Observation: those values are always the same by construction.
- What Local Reasoning Cannot Prove: backend behavior after a valid close.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/critique/2026-08-13-issue-542-closeout-target-disagreement.md

## Prevention

Keep source-specific authorization semantics explicit and make the ingress test
prove a refusal happens before the irreversible backend boundary.
