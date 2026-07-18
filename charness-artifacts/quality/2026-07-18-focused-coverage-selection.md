# Quality Review
Date: 2026-07-18
Title: Nearest focused coverage selection

## Scope

Target boundary: focused mutation-coverage command selection for changed Python
files referenced through split paths or same-directory local loader chains.

Ambient repo findings: D18 remains ignored. No version bump, push, release, or
Cautilus evaluation belongs to this deterministic selector slice.

## Structural Packet

- capability_needed: agents need a predictable cheap coverage producer without
  manually reconstructing dynamic local imports.
- current_centers: textual selector, focused producer, changed-line consumer,
  and broad pytest.
- next_center: nearest local-loader dependency selection.
- transformation: conservative selector enhancement; no dependency registry or
  new gate.
- proof_boundary: fixtures, live repo recommendation, instrumented producer,
  authoritative changed-line consumer, and separate broad proof.
- enforcement_posture: reuse existing closeout and pre-push gates.

## Current Gates

- Focused selector tests, ruff, source/plugin synchronization, packaging,
  read-only quality, locked broad pytest, and changed-line coverage own the
  slice.
- Selection order is direct reference, nearest loader ancestor with tests, then
  explicit broad fallback. The selector never replaces the final consumer.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` rendered by
  `render_runtime_summary.py`; <!-- reproduction-source -->
- runtime hot spots: the focused suite passed 18/18 in 1.23s; the recommended
  four-file subset passed 66 tests in 25.79s without coverage, versus about 51s
  for the earlier manually widened normal subset.
- coverage gate: the prior manual instrumented producer cost about 152.2s; this
  slice's first locked consumer rejected five uncovered state branches, which
  are now covered by focused tests. No speedup is claimed before the final lock.
- evaluator depth: deterministic-gates-only because paths, loader literals,
  selected tests, measured lines, and consumer verdicts are directly observable.

## Healthy

- Split `ROOT / "..."` references now map without requiring a duplicated full
  path literal.
- Same-directory loader ancestry is breadth-first, cycle-bounded, and stops at
  the nearest level that has standing tests.
- One- and two-argument `_load_sibling`, `load_local_skill_module`, and literal
  `with_name("x.py")` forms have regression fixtures.
- Candidate discovery excludes helper modules that pytest will not collect as
  `test_*.py` targets.
- The live unreleased range maps every eligible changed file to four test files
  and retains the broad proof path.
- The first authoritative consumer caught five uncovered lines after broad
  pytest passed, demonstrating that the final consumer still has independent
  teeth rather than inheriting the selector's green.

## Weak

- Static recognition intentionally misses arbitrary computed module names and
  cross-directory import factories. These fail conservatively to partial or
  missing, not to a false changed-line pass.
- The payload does not yet explain the exact ancestor chain used for each map.

## Missing

- No persisted observation corpus measures which loader shapes recur or how
  often provenance would shorten operator diagnosis.

## Deferred

- Do not add AST inference, a maintained dependency registry, arbitrary pytest
  naming rules, or provenance fields without an observed selection miss or
  diagnosis-cost signal.

## Advisory

- artifact: `docs/conventions/implementation-discipline.md`; the root Charness
  CLI is YAML-first, but this repo-internal helper's documented automation
  contract and default executable-command channel are JSON-specific.
  Migrating it requires a separate compatibility contract, not a drive-by flag
  removal.
- command: `check-python-lengths`; existing warn-band files and nested CLI counts
  remain ambient rather than being attributed to this selector slice.

## Delegated Review

- Delegated Review: executed — diagnostic correctness and test-economics angles
  plus a separate counterweight ran read-only.
- Review found a whitespace regression and a real two-argument loader miss; both
  were fixed, retested, and accepted in a follow-up review.
- A final follow-up accepted four tests added for the five exact changed-line
  gaps; no production code was weakened to satisfy coverage.
- Parent boundary fingerprints reported no reviewer worktree/index/HEAD drift.
- Slow-gate lenses: fixture-economics favors the derived four-file subset;
  parallel-critical-path finds no safe split inside the final consumer;
  duplicated-proof keeps focused coverage separate from cached broad pytest.

## Commands Run

- Focused selector plus rollback pytest: 28 passed; focused ruff and
  `git diff --check` passed.
- Live suggester: `recommended`, six eligible files mapped, zero unmapped.
- Full post-sync read-only quality passed; source/plugin sync and reviewer
  boundary checks also passed.

## Recommended Next Quality Moves

- active keep direct-to-nearest-to-broad selection as the standard sequence for
  advisory test producers; the final consumer remains the teeth.
- passive add mapping provenance only after a concrete operator diagnosis cost because maintaining unused provenance is speculative interface weight.
- passive profile loader scanning only if selector runtime becomes a measured bottleneck because current selection completes in about 3s.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
