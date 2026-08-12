# Issue 602 Create Verification Grammar Debug
Date: 2026-08-13

## Problem

When create's automatic readback is skipped or cannot complete, the issue tool
returned a raw backend view command rather than a tool-grammar verification
action. Its help also named known placeholder titles.

## Correct Behavior

Create retains its normal automatic readback. Later verification uses
`verify-create` with repo/number and optionally the original body file; without
that file it reports identity readback but never body fidelity. Operator help
does not prime known placeholder title strings.

## Observed Facts

- `create_issue` already read back a normal create, so it was false that create
  had no verification at all.
- Deferred paths exposed `view_argv`, a raw backend invocation, while no
  create-specific verification subcommand existed.
- Placeholder blocking covered only known exact titles and did not establish an
  agent-choice or provider-roundtrip claim.

## Reproduction

- A skipped readback returns an unverified payload; before this repair its only
  create-specific guidance was a raw backend view command.

## Candidate Causes

- Deferred verification was not modeled as a first-class lifecycle operation.
- Backend transport arguments were exposed as the next operator action.
- Help text optimized an escape-hatch explanation over priming resistance.

## Hypothesis

- A `verify-create` operation that reuses the selected backend view contract,
  paired with neutral placeholder help, restores a grammar-contained path;
  disconfirmer: deferred verification still requires a raw backend command or
  reports body fidelity without the original body file.

## Verification

- Result: confirmed by create, verify-create (with and without body file),
  issue-tool runner, issue-skill, and closeout-discipline regression suites
  (101 tests). R1 fresh-eye repair required custom view templates to bind repo,
  number, and fields; response number/repository identity; string body for
  byte verification; no public raw argv; and a help regression. R2 further
  required positive real issue numbers and explicit returned-repository
  evidence. Those R2 repairs are accepted-unreviewed under the two-round cap.

## Root Cause

The create lifecycle exposed a backend implementation detail instead of a
typed, tool-owned deferred verification operation.

## Invariant Proof

- Invariant: an unverified create with a known issue number offers a
  tool-grammar readback; only a supplied original body file can produce a
  byte-fidelity verdict. A verified readback has a positive exact issue number
  and explicit matching repository evidence.
- Producer Proof: create emits structured `verification` metadata and
  verify-create owns selected-backend readback.
- Final-Consumer Proof: CLI tests invoke verify-create rather than a backend
  command and observe `body_verified: null` without a body file.
- Interface-Shape Sibling Scan: close's raw view argv is a distinct post-close
  boundary and remains diagnostic-only for this slice.
- Non-Claims: no provider roundtrip or agent-choice behavior was tested.

## Detection Gap

- Tests covered normal readback and exact placeholder refusal but not the
  deferred verification command, its body-fidelity distinction, or help priming.

## Sibling Search

- Mental model: backend transport output is not an operator workflow command.
- create lifecycle: issue_create.py and issue_create_verify.py | decision: own typed verifier module | proof: fake-backend CLI tests.
- issue help/docs: SKILL.md and issue-backend.md | decision: neutral wording | proof: help/docs assertions.
- cross-file: issue_close.py | decision: diagnostic-only | proof: static scan; different irreversible boundary.

## Seam Risk

- Interrupt ID: issue-602-create-verification-grammar
- Risk Class: none
- Seam: create payload to deferred operator readback through selected backend.
- Disproving Observation: every unverified create has an equivalent safe
  in-grammar command already surfaced.
- What Local Reasoning Cannot Prove: external backend/provider and agent-choice behavior.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/critique/2026-08-13-issue-602-create-verification-grammar-resolution.md

## Prevention

Keep deferred lifecycle operations as typed CLI commands, bind both requested
and returned target identity before reporting readback success, and distinguish
a successful readback from byte-for-byte verification explicitly.

The pre-commit Python-length gate required moving the already-tested verifier
into the cohesive `issue_create_verify.py` module; the public create helper
keeps the same typed operation and focused regressions prove the wiring.
