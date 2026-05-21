# Mutation Testability Pool + JS Slice Critique

Date: 2026-05-21

## Scope

Closeout critique for expanding deterministic mutation sampling beyond
`scripts/*.py`, adding a bounded JS mutation slice for `scripts/agent-runtime`,
and removing ambient `agent-browser` orphan state from default deterministic
quality gates.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewers

- Pre-implementation reviewer `019e4875-4fe7-7f90-82e3-404c9b121e7d`
  identified forced-hygiene selection, extensionless `charness` mutation proof,
  subprocess-coverage risk, pool manifest coverage, and Stryker command-runner
  cost risks.
- Post-implementation reviewer `019e4884-8b29-7000-b0a0-01a3ea50aa41`
  identified two blockers: JS `NoCoverage` mutants were not blocking, and
  explicit `agent-browser` hygiene failure no longer ran cleanup.
- Closeout reviewer `019e4893-ac4b-7873-9afd-6647d41266c7` identified one
  blocker: stale or missing StrykerJS JSON reports could make the issue body
  or summary path misleading after a wrapper timeout or reporter failure.

## Act Before Ship

- JS `NoCoverage` and timeout mutants must be blocking signals, not excluded
  from a reachable denominator that can produce false PASS. Fixed in
  `scripts/check_js_mutation_score.py` and covered by
  `test_js_mutation_summary_blocks_no_coverage_mutants`.
- Explicit `agent-browser` hygiene must retain cleanup-on-failure. Default
  quality no longer runs or kills another session's daemon tree, but an
  operator-selected hygiene gate now executes cleanup after failure again.
- The CLI/surface probe that runs `scripts/doctor.py` must ignore ambient
  `agent-browser` orphan state, matching the deterministic coverage fixture
  behavior.
- JS mutation execution must delete stale JSON before launching StrykerJS, and
  the JS summary checker must fail when a full-mode report is missing. Fixed in
  `scripts/run_js_mutation.py` and `scripts/check_js_mutation_score.py`, with
  regression tests for both stale-report cleanup and missing-report failure.

## Bundle Anyway

- Python mutation pool now includes root CLI/bootstrap, `scripts/*.py`, public
  skill helper scripts, and support skill helper scripts while excluding tests,
  plugin exports, reports, and generated artifacts.
- The sample manifest records pool counts so future readers can see whether a
  selected file came from core, public skill helper, or support skill helper
  code.
- Cosmic Ray accepts the extensionless `charness` target; a regression test now
  proves that path before CI.
- StrykerJS is added only for `scripts/agent-runtime/*.mjs`. It uses command
  runner mode and is documented as coarse, budgeted proof rather than
  coverage-derived affected-test selection.
- The mutation workflow installs Node dependencies via `actions/setup-node@v6`
  and `npm ci` before running the JS slice.

## Valid But Defer

- Python subprocess coverage remains a known selector limitation for CLI-only
  execution paths. Current selection correctly treats unobserved files as scope
  gaps instead of silently mutating them; deeper subprocess coverage can be a
  later structural improvement.
- The first focused Stryker full run on `contract-versions.mjs` produced a real
  60% score at an 80% threshold. That is acceptable as discovery evidence; the
  new summary fails it instead of hiding it.

## Decision

Ship after sync and deterministic verification. Do not clean live
`agent-browser` daemon trees by default; keep real runtime hygiene explicit.
