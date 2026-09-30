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
- Changed surfaces: scripts/adapters/surfaces_lib.py,
  scripts/evidence/probe_record_parse.py,
  scripts/evidence/probe_stimulus_replay.py,
  scripts/gates_support/removed_name_consumers.py,
  scripts/setup/setup_adapter_inspect_lib.py,
  scripts/setup/setup_inspect_quality_lib.py,
  scripts/setup/validate_maintainer_setup.py,
  scripts/task_run/task_run_execution.py, scripts/task_run/task_run_git.py,
  tests/charness_cli/test_task_run_git_refusals.py,
  tests/charness_cli/test_task_run_scope_gaps.py,
  tests/coverage_debt/test_batch12.py,
  tests/quality_gates/test_maintainer_hooks.py,
  tests/quality_gates/test_setup_inspect_adapters.py,
  tests/repo_bootstrap_marker.py (deleted)
- Minimum sufficient proof: one adversarial critic pass (`VERDICT: ship`,
  zero blockers, 13 numbered findings) with the two novel claims
  parent-verified against the tree; `ruff check` clean on all touched
  files; length gate validated; fresh-interpreter imports of all nine
  modules with and without `PYTHONPATH`; by-path loads from a foreign
  cwd; 59/59 focused tests; standing suite 11076 passed on the final
  tree; `check_standalone_imports` ok on the nine files; negative
  control below executed.
- Deliberately omitted checks: downstream copiers outside this repo (none
  exist in repo, docs, skills, or tests; the sanctioned in-repo copier
  structurally cannot emit the guard-without-bootstrap shape); live
  provider lanes (import-time deletion, no lane behavior change).
- Verifier contract: native read-only subagent on the shared tree
  (reviewer verdict in this session's subagent log, fossil-critic
  01a0f0a5); standing pytest; run-quality full read-only release lane;
  ruff check; fresh-interpreter probes; this artifact validated by
  validate_critique_artifacts.py.
- Failure classification: none
- Negative control: command: replayed the deleted refuser probe against the new tree (meta_path blocker for `scripts.core.subprocess_guard` + evicted guard + root stripped from sys.path, by-path load of `scripts/task_run/task_run_git.py`); expected refusal: plain `ModuleNotFoundError` propagates (no fallback swallows it); observed result: `ModuleNotFoundError: No module named 'scripts.core.subprocess_guard'`, refuser fired=True; receipt: this-session run record, tree left unmodified (inline probe, no repo writes).
- Subject identity: sha256:f6859b435d324de4d308523f085be4fa6da37feb94c770818f5cb2407ecdd5ce
- Verifier identity: sha256:09d2c417c352fec7bf4019c6972198ae9a28667dc8edf59aa43dbed86406ee67
- Input identity: sha256:953b1d207c76bfa5c8128f7a19672b36a985251f49c33345191dacf84eb56afd
- Failure identity: stable:clean
- Evidence identity: sha256:85c12d8b8879b3aa6ea97e31a647763db7c99d5e0fc9d02ed7536f2c526acb81
- Retry disposition: first-attempt
- Retry key: sha256:2531a89cc48e24fdc933c36ba00c5f1d678f5402420de8e4d6659adab425111f

Identity preimages (reproducible): subject is sha256 of
`git diff 4cfd3cc75..7565242f3` bytes; verifier is sha256 of the critic
verdict text (fossil-critic 01a0f0a5 final answer); input is sha256 of the
string "release 8.14.5 patch over 4cfd3cc75..7565242f3 closing no issues";
evidence is sha256 of "standing:11076 passed;" plus the first 512 bytes of
tests/coverage_debt/test_batch12.py; retry key is
`build_retry_key` over the four identities above (NUL-joined sha256).

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
