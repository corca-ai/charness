# Quality Review
Date: 2026-08-12
Title: Issue 593 HOTL target binding

## Scope

Target boundary: HOTL disposition parsing at verify and manual close carriers.
No live GitHub mutation or tracker readback is claimed.

## Surface Contract Review

- semantic coverage: observed — target identity at helper and both carrier consumers.
- surface: HOTL disposition parsing for verification and manual close carriers.
- owner: rung-1 HOTL floor owns grammar; callers own invoked issue numbers.
- projections: helper verdict, direct manual carrier, and bundled close carrier.
- state scope: one invoked issue and a multi-issue bundle; unrelated quoted numbers
  remain inert.
- transitions: unrelated target inert; matching target typed/refused; shorthand
  accepted only for a single invoked issue.
- proof boundary: deterministic focused tests and two fresh-eye rounds; no
  GitHub mutation or tracker readback occurred.
- unexamined axes: live tracker close state and provider-backed comment delivery.

## Current Gates

- The rung-1 HOTL floor binds a disposition to the invoked issue number.
- Direct and bundled manual carriers pass their invoked numbers into that floor.

## Runtime Signals

- runtime source: focused pytest receipt; timing capture is missing because this
  bounded parser path has no configured timing capture. <!-- reproduction-source -->
- runtime hot spots: none observed; this slice does not run a broad quality gate.
- coverage gate: focused rung-1 and close-comment regressions passed (35 tests).
- evaluator depth: deterministic-gates-only; Cautilus is not approved and would
  not establish tracker behavior.

## Healthy

- A copied unrelated HOTL issue number no longer blocks a close.
- A matching malformed HOTL entry is still refused at the carrier boundary.

## Weak

- Tracker mutation and live comment delivery are external to these focused tests.

## Missing

- No provider-backed close/readback proof is claimed.

## Deferred

- Post-publication closeout and tracker readback belong to each issue's separate
  irreversible-boundary carrier.

## Advisory

- structural review result: evidence: carrier-level tests prove number
  propagation and target exclusion; helper-only parsing would not cover that
  consumer boundary.
- prose review result: artifact: the HOTL floor remains a presence/form floor,
  not a claim that every selected issue has a HOTL entry.

## Delegated Review

- status: executed — round 1 required carrier-level proof; the repair added
  manual and bundle paths. Round 2 approved with a clean reviewer-boundary
  fingerprint. The later critique added direct manual-carrier and combined-target
  coverage; those repairs are accepted-unreviewed under the two-round cap.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  not applicable; this is a bounded deterministic parser seam.

## Commands Run

- `pytest tests/quality_gates/test_issue_closeout_rung1_floors.py tests/quality_gates/test_issue_close_comment_floor.py -q` — 35 passed.

## Recommended Next Quality Moves

- active carrier-owned target binding — preserve it whenever a shared closeout
  parser gains a per-issue grammar; test at least one bundled and one
  direct-mutation path.

## History

- [Portable proof-path learning review](./history/2026-07-19-portable-proof-path-learning-review.md)
