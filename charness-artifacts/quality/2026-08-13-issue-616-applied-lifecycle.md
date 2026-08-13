# Quality Review
Date: 2026-08-13
Title: Issue 616 applied lesson and contract lifecycle

## Scope

Target boundary: schema migration, replay, operator mutation commands, and
non-authorizing reports for lesson archive/resurrection and contract
graduation/retirement. No live contract membership transition is applied.

Ambient repo findings: PLR2004 is not enabled and a diagnostic-only scan reports
992 findings, mostly tests. That is a separate baseline/ratchet candidate, not a
reason to broaden this lifecycle slice.

## Surface Contract Review

- semantic coverage: observed — v3/v1 migration, lifecycle replay, active and
  archived selection, proposal evidence, reviewed application, retirement, and
  retained history have deterministic behavior tests.
- surface: lesson ledger v4, preview policy v2, contract register v2, and seven
  operator commands.
- owner: the ledgers own durable events and projections; quality supplies evidence
  for a proposal; a reviewed Markdown decision authorizes a state transition.
- projections: active lessons, archived lessons, active units, retired units,
  preview buckets, checker receipts, and retention rows.
- state scope: one repository-local append-only ledger/register; no installed,
  hosted, or GitHub state is touched.
- transitions: v3-to-v4 and v1-to-v2 migration, archive/resurrect,
  propose/apply-graduation, retirement, citation, and deterministic rebuild.
- proof boundary: focused tests, live read-only validators/previews, generated
  mirror equality, and bounded fresh-eye review; no human approval quality or
  usefulness threshold is inferred.
- unexamined axes: long-run selection usefulness, contract catch mapping,
  calibrated staleness, provider behavior, and concurrent writers across hosts.

## Current Gates

- Existing ledger/register validators enforce closed schemas, canonical paths,
  append-only committed prefixes, fixed budgets, deterministic projections, and
  live H2 equality when an application is attempted.
- Existing root-plugin synchronization owns shipped mirrors; no new broad gate is
  introduced.

## Runtime Signals

- runtime source: focused pytest and direct operator-command receipts; timing
  capture is missing because these bounded local paths have no timing budget.
  <!-- reproduction-source -->
- runtime hot spots: none observed; 82 focused tests completed in about four seconds.
- coverage gate: focused lifecycle suite passed (85 tests); broad repo quality
  remains a closeout step.
- evaluator depth: deterministic-gates-only; Cautilus is ask-before-run and was
  neither requested nor needed to prove replay invariants.

## Healthy

- Existing live state migrates without changing its lesson scores, active cohort,
  contract unit inventory, or unit budget.
- Archived selection has a real slot and no fabricated active fallback.
- Contract evidence proposes but never auto-applies a membership change.
- Duplicate review classifies the 19 newly grouped families as intentional
  standalone-CLI plumbing or parallel schema-owner replay, with a rationale per
  fingerprint; no fixable duplication is accepted into the gate baseline.

## Weak

- Catch events remain unavailable because no gate-to-unit mapping exists.
- The retention report cannot yet calibrate staleness.

## Missing

- No live archive, graduation, or retirement decision exists to exercise a real
  reviewed event; fixtures prove the transition mechanics only.

## Deferred

- Score thresholds, automatic graduation, contract catch attribution, calibrated
  staleness, and adversarial multi-host writer transactions remain explicitly out
  of scope.

## Advisory

- structural review result: artifact: the durable event stream is separate from its
  materialized projection and from live contract docs, so replay can refuse drift
  instead of silently rebuilding away history.
- prose review result: command: operator docs put dry run and reviewed decision references
  at mutation boundaries and state that evidence/reporting is non-authorizing.
- inventory evidence: `ruff check --select PLR2004 scripts skills tests` found a
  separate 992-item adoption problem; use a production-only no-increase ratchet if
  pursued rather than enabling it globally in this slice.

## Delegated Review

- status: executed — a bounded preimplementation quality reviewer confirmed the
  v4/v2 event-and-projection shape, active budget 50, real archive slot, frozen
  register seed, and non-authorizing report; its reviewer-boundary fingerprint
  verified clean. Final repaired-surface critique is still required at closeout.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  not applicable; focused deterministic tests reuse existing fixtures and complete
  in seconds.

## Commands Run

- `pytest` over the lesson, selection, continuity, and contract-register suites —
  85 passed.
- both checker commands, deterministic preview, and retention review — valid;
  live state is 16 active lessons and 26 active contract units.
- `sync_root_plugin_manifests.py` and Ruff over changed Python — clean.
- duplicate ratchet after reviewed overlay classification — clean at fixed
  `fixable_ceiling=0`.

## Recommended Next Quality Moves

- active lifecycle closeout — capability_needed=bounded repaired-surface review;
  next_center=#616 proof surface; transformation=review then focused/broad gates;
  proof_boundary=local direct-commit carrier; enforcement_posture=existing-gate-reuse.
- passive magic-number ratchet because adoption needs its own baseline owner — capability_needed=baseline ownership;
  next_center=production Python only; transformation=no-increase PLR2004 baseline;
  proof_boundary=diagnostic inventory because tests dominate current findings;
  enforcement_posture=no-gate because adoption needs an independent quality slice.

## History

- [Portable proof-path learning review](./history/2026-07-19-portable-proof-path-learning-review.md)
