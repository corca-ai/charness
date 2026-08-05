# Issue #506 — local open disposition carrier

Date: 2026-08-05
Status: local implementation complete; remote issue remains open pending closeout
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
  tests/quality_gates/test_reviewer_boundary_fingerprint.py` passed 26 tests in
  5.63 seconds, and the paired parity suite passed 45 tests. The suites cover
  explicit-window binding, unqualified default refusal, explicit-path legacy
  compatibility, parent attribution, malformed snapshot refusals, and no-write
  semantics.
- Source/plugin identity: `cmp -s
  skills/shared/scripts/reviewer_boundary_fingerprint.py
  plugins/charness/shared/scripts/reviewer_boundary_fingerprint.py` passed;
  `py_compile`, focused `ruff check`, and `git diff --check` also passed.
- Implementation: the default canonical path now refuses without `--window-id`,
  while explicit `--before` remains an identity-bearing compatibility path; the
  operating contract names the complete invocation.
- Delegated resolution critique: the issue-specific critique records three
  angles, a separate counterweight, four clean reviewer-boundary windows, and
  the decision not to add canonical-path alias detection:
  `charness-artifacts/critique/2026-08-05-issue-506-resolution-critique.md`.
- Distinct behavior verdict: the focused helper/parity test channel establishes
  the local contract for the tested window/refusal axes. This is a behavior
  verdict about the repository helper, not a remote issue-state verdict.

## Durable blocker and next action

The remote issue is still OPEN, and no direct-commit carrier, remote CI
readback, or adapter closeout readback has been run for #506. Before close,
validate the exact carrier, render the distinct focused-test behavior verdict,
and read the remote state back through the issue adapter. A new recurrence or a
host invocation claim would reopen the local proof question.

## Non-claims

This carrier does not claim remote issue closure, remote CI, provider/host
invocation proof, release publication, or that every reviewer caller supplies
an explicit `--goal-path`-style window argument. It does not replace the
distinct-observer requirement with a same-agent reread and does not merge
#506's reviewer-window semantics into the #502 receipt contract.

## Fresh-observer boundary

The #506 resolution critique's Jackson, Weinberg, Gawande, and counterweight
windows each returned a clean boundary verify before parent writes. This
accepts the local implementation proof only. The remote issue remains OPEN
until the direct-commit carrier and adapter CLOSED readback complete.
