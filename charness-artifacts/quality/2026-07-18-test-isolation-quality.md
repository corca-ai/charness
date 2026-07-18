# Quality Review
Date: 2026-07-18
Title: Test Isolation Correct-By-Construction Review

## Scope

Target boundary: standing-test isolation, early detection of shared-checkout
mutation, and xdist seed-cache behavior; release/publish behavior is excluded.

Ambient repo findings: the prior broad-suite race exposed one remaining test
that wrote a transient critique artifact into the real checkout.

## Current Gates

The existing `check_test_repo_copy_invariants.py` already runs before broad
pytest and owns copy-policy drift plus copy-heavy standing-test exclusions. This
slice reuses that gate rather than adding another closeout floor.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: read-only quality 55.9s latest / 55.7s median; pytest 35.4s / 35.9s, both within configured profile budgets.
- coverage gate: focused proof, locked full closeout (4,735 tests), and changed-line mutation proof passed.
- evaluator depth: deterministic-gates-only; the test filesystem and process-lock seams have direct executable proof, so Cautilus is not required.

## Healthy

- Test setup already has `tmp_path`, centralized copy helpers, release-only
  copy-heavy markers, and a file-locked content-addressed seed cache.
- The existing isolation gate is cheap, deterministic, and already sequenced
  before broad pytest in the repo-python surface.

## Weak

- The gate guarded copy cost but not direct writes through the real checkout
  root, allowing transient files to perturb unrelated xdist workers.
- The seed cache's cross-process build-once and stale/partial recovery behavior
  existed in code without direct behavioral tests.

## Missing

- No missing gate remains for the reproduced direct-path class after this
  slice; arbitrary subprocess/library side effects intentionally remain outside
  the finite AST ratchet.

## Deferred

- Failed-builder seed-cache recovery waits for a concrete failure or recurrence;
  current code omits the ready marker and rebuilds partial state on the next call.

## Advisory

- structural review result: artifact: `../critique/2026-07-18-test-isolation-critique.md` records that capability needed is predictable first-pass test
  isolation; existing centers are `tmp_path`, repo-copy policy, and seed-cache
  locking; the next center is the existing isolation gate, strengthened through
  existing-gate reuse with a direct focused proof boundary.
- prose review result: artifact: `../../skills/public/quality/references/testability-and-selection.md` now states one principle
  and one concrete shape—source checkout read-only, minimal temporary repo for
  writes—without claiming a static sandbox.
- command: the extended checker found exactly one current true positive and no
  ambient false positives; after isolation it passes repo-wide.

## Delegated Review

- Delegated Review: executed — two read-only scouts shaped the work list, then
  two high-leverage code-critique angles and a separate counterweight reviewed
  the finite detector contract; fingerprint verification reported no drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  re-delegated to the structural scout; it rejected a copy-heavy standing fixture
  and favored focused seed-cache behavior tests.

## Commands Run

- quality/impl planners, runtime summary, Cautilus preflight, skill authoring preflight.
- repo-wide isolation checker plus 73 focused invariant, preflight, and seed-cache tests.
- ruff on all changed Python surfaces.

## Recommended Next Quality Moves

- active existing-gate reuse — capability_needed=first-pass standing-test isolation; next_center=repo-copy/test-isolation checker; transformation=finite real-root pathlib taint ratchet plus minimal temporary-repo helper pattern; proof_boundary=focused positive/negative AST fixtures and xdist process test; enforcement_posture=existing-gate-reuse.
- passive failed-builder recovery test — capability_needed=seed-cache exception recovery evidence; next_center=seed-cache focused tests; transformation=add only after a failure or recurrence; proof_boundary=builder exception then successful retry; enforcement_posture=no-gate because current recovery structure is direct and no escape has been observed.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
