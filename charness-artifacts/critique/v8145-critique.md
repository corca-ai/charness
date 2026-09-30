# Release Critique — charness v8.14.5 (patch)

Date: 2026-09-30

## Decision Under Review

Ship charness v8.14.5 (tag v8.14.5) as a patch release carrying the removal
of nine bootstrap-shadowed `subprocess_guard` re-root fallbacks (plain
imports after `_load_repo_runtime_bootstrap()`), the deletion of the five
refuser tests that pinned the fossil, and the deletion of the now-unused
marker-defeat helper. No behavior change in any shipped layout.

Kind: charness release critique
Prepared for: v8.14.5 patch release
Scope: 15 files over 4cfd3cc75..7565242f3 (9 scripts, 5 test files, 1
helper deletion; +30/-387); the reviewer read the pushed commit and the
working tree, and the parent verified the diff with focused suites, fresh
interpreters, and the full standing suite.
Reviewers: 1 native read-only fresh-eye subagent (adversarial fossil
critic), parent-owned counterweight (this artifact)

## Release Scope

v8.14.5 is a patch release: dead-code removal only. It closes no issues. No
new commands, flags, skills, or install surfaces; no migration; no receipt
changes. The nine deleted `except` arms could only run where the bootstrap
marker is absent but the guard marker is present, a layout that exists
nowhere shipped (repo, plugin mirror, skills, fixtures all carry both
markers or neither in the failing direction).

## Surface-Lock Inventory

Generated artifacts: the `plugins/` mirror is generated and gitignored; no
packaging or CLI surface is touched by this release, so no regen applies.

Consumer-visible behavior: none. Successful imports resolve identically
(bootstrap inserts the root, plain packaged import binds the same module
object). Failure modes change only where they were already crashes: a
lone-file copy now raises plain `ImportError` instead of `StopIteration`
from the arm's defaultless `next()`, which is the strictly better
diagnostic.

## Operator Action Required

None. No behavior reversals: every import that succeeded before succeeds
now, binding the same objects.

## Upgrade Path

Standard patch upgrade from any 8.x install via `charness update`; no
migration, no config change. Rollback to 8.14.4 is safe (pure deletion,
no state or contract change).

## Verification Scope Decision

- Claim under test: v8.14.5 patch removes only unreachable fallback arms
  and their pinning tests, breaks no import path in any shipped layout,
  and leaves no stale reference (imports, tests, docs).
- Evidence accepted: critic subagent disk survey + gate scan (read-only,
  fresh context); parent spot-checks of the critic's two novel claims;
  `ruff check` clean on all touched files; length gate validated;
  fresh-interpreter imports of all nine modules with and without
  `PYTHONPATH`; by-path loads from a foreign cwd; 59/59 focused tests;
  11076/11076 standing suite; `check_standalone_imports` ok on the nine
  files (run by the critic against the real gate).
- Not re-proven: downstream copiers outside this repo (none exist in repo,
  docs, skills, or tests; the sanctioned in-repo copier structurally
  cannot emit the guard-without-bootstrap shape).

## Failure Angles

- A shipped partial layout (guard without bootstrap marker) would make a
  removed arm load-bearing: surveyed repo, plugin mirror, skills scripts,
  mutants mirror, closure-seeded fixtures, lone-copy fixtures, and
  literal-file fixtures — the shape exists nowhere (§1-§6).
- A gate or test enforcing the fallback pattern would go red on removal:
  no enforcement exists; `check_standalone_imports` (the by-path import
  gate) passes on all nine files (§8, §12).
- Leftover references (`_repo_root`, refuser tests, helper imports) would
  fail lint or collection: zero residue repo-wide; the one remaining
  `_repo_root = next(` is a distinct `None`-default pattern, not a tenth
  instance (§9-§11).
- A future downstream copier could package guard-without-bootstrap: no
  such copier exists; the arm could not have fired in two of the nine
  files anyway (preceding plain imports die first) (§7, §13).

## Counterweight Triage

- Act Before Ship: none. The critic returned `VERDICT: ship` with zero
  blockers; both novel claims (§3 closure mechanism, §9 distinct sibling)
  parent-verified against the tree.
- Bundle Anyway: none — the change is already minimal (+30/-387, format
  noise reverted out of the diff).
- Over-Worry: skills/ scripts keep identical arms (they never call the
  bootstrap, so the arm is their only inserter — correctly out of scope,
  §6); `lesson_ledger_writer_lib.py` keeps its `None`-default arm
  (distinct pattern with re-raise — correctly out of scope, §9).
- Valid but Defer: the `except ModuleNotFoundError` re-root siblings for
  non-guard modules (~20 files) are the same disease with per-module
  proofs still owed; each needs its own shadowing check (one,
  `run_standing_pytest.py`, is documented-live with no preceding
  bootstrap and must be kept).

## Fresh-Eye Satisfaction

parent-delegated: one independent native-subagent adversarial pass with a
ship/block verdict returned no blocking finding; every numbered finding
(§1-§13) either corroborates the fossil argument with file evidence or
scopes a correctly-excluded sibling with a named reason. The parent
spot-verified the two findings that go beyond the commit message rather
than re-running the whole survey; the slice stops here by the bounded
follow-up rule.

## Reviewer Tier Evidence

- Requested tier: native read-only subagent on the shared tree (no file-backed worker tier requested; host exposes no reviewer-tier control)
- Requested spawn fields: role, objective, task_name via subagent_spawn; read-only brief, no isolation (shared checkout, no writes)
- Host exposure state: host-defaulted
- Application state: findings received in parent context; reviewer read-only with no writes; model/effort mapping not host-visible
- Delivery state: findings-received
- Execution mode: typed-subagent

## Boundary Ownership

- Producer: `_load_repo_runtime_bootstrap()` (owns repo-root insertion), the nine edited scripts (own their packaged imports)
- Consumer: direct script invocations, by-path loaders (tests, gates), fresh-interpreter first imports
- Owning surface: module import blocks of the nine scripts
- Verdict: owned-correctly
