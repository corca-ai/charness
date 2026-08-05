# Issue #506 — local open disposition carrier

Date: 2026-08-05
Status: local behavior established; remote issue remains open and out of scope
Issue: https://github.com/corca-ai/charness/issues/506

## Observed problem

The shared reviewer-boundary helper has a canonical default snapshot path. An
unqualified verify can therefore read an older snapshot belonging to another
review window and report against the wrong baseline. The explicit `--before`
path used by the structural review selected the intended snapshot and returned
clean. The live issue remains OPEN; this carrier records the local disposition
without changing that state.

## Producer, consumer, and owner

- Producer: `skills/shared/scripts/reviewer_boundary_fingerprint.py` creates
  the snapshot and verifies its fingerprint, window identity, and parent/reviewer
  attribution.
- Consumer: the review parent reads the verify verdict before accepting a
  delegated fresh-eye review as a boundary proof.
- Owner: the reviewer-boundary helper and its invocation contract; the parent
  owns the decision to accept or quarantine the review.

## Semantic invariant and falsifier

The requested review window must be explicit in the evidence being verified.
A snapshot from another window, a stale default snapshot, or parent-attributed
worktree drift must not be rendered as a clean proof. A valid explicit window
must preserve the existing clean/parent-attributed distinction and no-write
boundary semantics.

Falsifier: a focused helper test accepts a stale/default snapshot as the
requested window, loses the window identity in its refusal, or turns
parent-attributed drift into a clean verdict.

## Local proof

- Focused behavior proof: `pytest -q
  tests/quality_gates/test_reviewer_boundary_fingerprint.py` passed 24 tests in
  4.98 seconds. The suite covers explicit-window binding, stale/default
  refusal, parent attribution, legacy snapshot compatibility, and no-write
  semantics.
- Source/plugin identity: `cmp -s
  skills/shared/scripts/reviewer_boundary_fingerprint.py
  plugins/charness/shared/scripts/reviewer_boundary_fingerprint.py` passed;
  `py_compile`, focused `ruff check`, and `git diff --check` also passed.
- Delegated disposition evidence: the prior structural final disposition review
  explicitly routes issue #506 to the reviewer-tool contract, records its
  `recurs: #461` lineage, and states that #506 is an open record rather than a
  closed-issue or live-behavior claim:
  `charness-artifacts/critique/2026-08-04-reduce-closeout-runtime-structural-waste-disposition-review.md`.
- Distinct behavior verdict: the local helper contract is established for the
  tested window/refusal axes. This is a behavior verdict about the repository
  helper, not a remote issue verdict; the final cross-track claims reviewer is
  the independent reader of this carrier.

## Durable blocker and next action

The remote issue is still OPEN, and no issue-resolution critique, remote CI
readback, or adapter closeout readback has been run for #506. Leave the issue
open. Before any later close call, run a #506-specific delegated resolution
critique, validate the issue carrier, render a distinct behavior verdict, and
read the remote state back through the issue adapter. A new recurrence or a
host invocation claim would reopen the local proof question.

## Non-claims

This carrier does not claim remote issue closure, remote CI, provider/host
invocation proof, release publication, or that every reviewer caller supplies
an explicit `--goal-path`-style window argument. It does not replace the
distinct-observer requirement with a same-agent reread and does not merge
#506's reviewer-window semantics into the #502 receipt contract.

## Fresh-observer boundary

An earlier independent claims reread completed with no blockers in window
`cross-track-final-claims-final-reread-20260805`; its boundary verify was
clean. The goal then committed an acceptance update and rebound its packet, so
the post-acceptance reread remains pending. The remote issue remains OPEN and
still requires its own later resolution critique and adapter readback.
