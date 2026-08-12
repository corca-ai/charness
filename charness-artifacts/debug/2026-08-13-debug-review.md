# Issue 586 Wired-Proof Debug
Date: 2026-08-13

## Problem

Issue #586 proposes a structural guard after historical checks passed direct-call
tests while their real operator paths did not reach them; its current evidence
also says the two cheap candidate guards have zero live findings.

## Correct Behavior

Given an added proof-surface check, when an operator invokes its production
entry point, then a representative wired-path test should observe the check or
the issue should retain an explicit non-closure disposition rather than claim a
general guard is justified from historic examples alone.

## Observed Facts

- The issue's current comment measured zero classification-vocabulary
  divergences and nine production functions referenced only from tests; its most
  suspicious result was a superseded helper with an equivalent wired guard.
- No current candidate shown in the issue is a reproduced inert check.
- Claim type: liveness/absence. Candidate claim: the proposed cheap guard catches
  a current instance. Cheapest falsifier: rerun or inspect the named measured
  candidates through their operator routes. Result: not yet confirmed.

## Reproduction

- n/a — issue #586 currently records historical incidents, not a current failing
  operator-path reproduction; inspect its named candidates before proposing code.

## Candidate Causes

- A current production entry point may omit a context argument or bypass a new
  check despite a direct-call test.
- The historical pattern may have been repaired, leaving only a useful review
  heuristic rather than an automatable invariant.
- A token-reference scan may misclassify dynamic or superseded helpers as inert.

## Hypothesis

- Falsifiable claim: a named current candidate fails to exercise an equivalent
  check through its real operator entry point | disconfirmer: trace the named
  candidate's production caller and execute its closest existing wired test.

## Verification

- disconfirmed for the named candidate — `issue_close.py` and
  `issue_verify_closeout.py` both invoke `readbacks_for_closeout()` on their
  production paths, and `tests/quality_gates/test_issue_consolidation_readback.py`
  passed 28 tests, including the wired-loop fetch-failure branch.

## Root Cause

The named `verify_consolidation()` helper is superseded rather than inert: its
two actual closeout consumers call the equivalent `readbacks_for_closeout()`
implementation. The remaining issue evidence names no current failing path, so
a generic detector would be a speculative feature rather than a bug repair.

## Invariant Proof

- Invariant: operator-path proof must observe the check that its direct-call test
  claims to exercise.
- Producer Proof: a check or classification emits a decision.
- Final-Consumer Proof: the operator-facing command, hook, or close carrier
  reaches that decision on its production path.
- Interface-Shape Sibling Scan: both direct-close and verifier consumers share
  the same readback interface and call the wired implementation.
- Non-Claims: no current inert check, consumer-repository path, or general
  automatic detector accuracy is proven.

## Detection Gap

- Direct-call unit tests | cover implementation but not production reachability |
  add a wired-path assertion only where a live check/entry-point pair is named.

## Sibling Search

- Mental model: coverage of a helper is equivalent to reachability from its
  operator entry point.
- same layer: closeout classification copies | decision: diagnostic-only pending
  a live divergence | proof: issue's measured zero-divergence comment.
- abstraction up: generic reachability advisory | decision: defer pending a
  measured false-negative/false-positive evaluation | proof: no current finding.
- cross-file: `issue_consolidation_readback.verify_consolidation` | decision:
  inspect its wired equivalent before treating it as inert | proof: issue comment.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: proof helper to operator entry point.
- Disproving Observation: each named candidate has an equivalent wired guard.
- What Local Reasoning Cannot Prove: paths invoked only by external hosts.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: spec
- Handoff Artifact: this record.

## Prevention

Use a wired-path regression test for any newly named production check. Do not
add a broad detector without a current instance and an evaluated error model;
record #586 as deferred until that trigger is available.
