# Issue 614 Unbounded Local Artifact Retention Debug
Date: 2026-08-13

## Problem

Repo-owned local test and mutation workspaces can retain expensive outputs without
a bounded lifecycle: failed standing-pytest basetemps accumulate automatically,
while `reports/mutation` does not distinguish managed current outputs from ad-hoc
diagnostics.

## Correct Behavior

Given repeated standing-test failures, when another run begins or ends, then the
runner keeps only the newest three inspectable failed basetemps and never deletes
the current or a concurrently active run. Given mutation reports, the maintained
fixed-path outputs stay protected while an operator can inventory and explicitly
prune old unmanaged diagnostics without a normal quality run deleting evidence.

## Observed Facts

- Issue #614 records the seed-cache incident and the maintainer's decision to keep
  failed pytest roots for inspection while bounding their tail.
- `run_standing_pytest.py` names explicit roots `charness-run-<time_ns>` so nested
  pytest cleanup deliberately cannot see them, and removes one only after exit 0.
- The live cache contains 26 such roots under the current repo key; that key is
  5.6 GB of the 6.0 GB `pytest-tmp` tree. The newest retained roots are still
  hundreds of MB, so count rather than empty parent directories drives cost.
- The earlier 2026-05-12 temp-amplification incident explicitly retained three
  successful pytest sessions; three is therefore an existing inspection tradeoff,
  not a new guess.
- `reports/mutation` currently has 32 top-level files. Its 2.2 GB total is dominated
  by `issue-354-coverage.json` at 2,017,725,609 bytes, dated 2026-06-11.
- Maintained mutation producers resolve fixed paths such as `test-coverage.json`,
  `cosmic-ray.sqlite`, `cosmic-ray-dump.jsonl`, `sample.json`, `sample.md`,
  `summary.md`, and the configured run log; they overwrite or clear those paths.

## Reproduction

- Live smallest observation: `find` under the current printed temp root finds 26
  `charness-run-*` directories; `du` measures that repo key at 5.6 GB. The only
  post-run deletion branch is guarded by `result.returncode == 0`, so another
  failure adds a root and removes none.
- Mutation disconfirmer: top-level size/mtime inventory plus repository reader and
  writer search finds a single 2.02 GB ad-hoc file, not a canonical per-run history
  family. Fixed canonical names can be large, but their path cardinality is bounded.

## Candidate Causes

- Pytest's own retention is expected to prune the roots; disconfirmed because the
  `charness-run-` prefix intentionally avoids pytest's `pytest-` cleanup race.
- The 181 repo-key parents are the primary disk cost; disconfirmed because the
  current key alone owns 5.6 GB and most other keys are empty or tiny.
- Failed-run retention has no repo-owned cap; confirmed by the sole success-only
  `shutil.rmtree` branch and 26 live retained roots.
- Canonical mutation runs append unbounded history; disconfirmed by fixed output
  paths. The remaining defect is the missing managed/unmanaged lifecycle contract.

## Hypothesis

- Confirmed diagnosis: a runner-owned newest-three prune, protected by per-run
  sibling locks and scoped only to default-generated `charness-run-*` roots, will
  bound inspectable failures without touching explicit `--basetemp` paths.
- Confirmed policy boundary: classifying canonical mutation outputs as managed
  replace-in-place state and making unmanaged pruning dry-run-first and explicit
  will provide cleanup without turning an ordinary proof run into an evidence
  deletion boundary.
- disconfirmer: a focused concurrency test may delete a locked sibling, a custom
  basetemp test may inspect its parent, or the mutation inventory may classify a
  configured canonical path as unmanaged.

## Verification

- Focused runner, retention-manager, mutation-producer, closeout, quality-runner,
  and changed-line suites passed (156 tests); the repaired-only suite passed 40.
- A live dry-run classified nine unmanaged files totaling 2,051,034,430 bytes,
  emitted a candidate-set digest, removed nothing, and refused `--execute` without
  that digest. No live deletion was authorized or performed.
- Tests execute the final standing-runner failure/success branches, active and
  explicit-keep preservation, invalid override fallback, report-root and candidate
  replacement refusals, managed-set changes, immediate pre-unlink revalidation,
  and the dry-run/confirmation/execute CLI sequence.

## Root Cause

The standing runner deliberately escaped pytest's unsafe nested cleanup but supplied
only a success cleanup branch, leaving its own failure retention ownerless. Mutation
outputs had fixed producers but no explicit boundary between replaceable current state,
ad-hoc local diagnostics, and durable evidence, so safe cleanup was undecidable.

## Invariant Proof

- Invariant: when the standing runner retains a failed basetemp for inspection, a
  later runner may remove it only after proving it is outside the newest-three set
  and not active; when mutation cleanup names a candidate, the operator must see a
  dry-run inventory before deletion.
- Producer Proof: simulated successful and failed standing runs write distinct
  lifecycle markers; the report inventory derives fixed managed paths and renders
  an identity-bound candidate set.
- Final-Consumer Proof: the runner retains exactly three marked failures while
  leaving active/custom/explicit-kept/legacy roots alone; CLI dry-run removes
  nothing, unconfirmed execute refuses, and confirmed execute removes only the
  unchanged synthetic candidate.
- Interface-Shape Sibling Scan: seed-cache LRU, pytest nested-cleanup protection,
  fixed mutation report producers, and ignored local artifact roots were inspected.
- Non-Claims: no automatic deletion of existing mutation reports or user-supplied
  basetemps; no claim that `pytest-tmp` itself caused the seed-cache disk-full event.

## Detection Gap

- Standing-runner tests | covered success deletion and nested-cleanup safety but no
  repeated-failure retention | exercise default-path failure wiring and locked peers.
- Mutation docs/tools | named report files but not lifecycle class | inventory the
  configured managed set and require explicit execution for unmanaged pruning.

## Sibling Search

- Mental model: once data is gitignored or outside the repo, its lifecycle needs no
  owner because the producing tool will eventually clean it.
- same layer: test seed cache | decision: already fixed with newest-three LRU and
  active-lock skip | proof: focused regression suite.
- abstraction up: `.charness/reviewer-boundary` and `.charness/usage-episodes` |
  decision: monitor, not this slice | proof: 12 MB and 8.7 MB snapshot only;
  follow-up: issue-614-small-hidden-roots-if-growth-reproduces.
- cross-file: mutation outputs | decision: fix policy and operator cleanup now |
  proof: producer/reader inventory plus live size/mtime inventory.

## Seam Risk

- Interrupt ID: issue-614-local-retention
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: future host disk pressure or operator usefulness
  of any specific unmanaged diagnostic.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep retention adjacent to the producer that owns each workspace. Automatic cleanup
may touch only runner-named roots with liveness proof; ambiguous ignored evidence gets
a managed-path inventory and an explicit dry-run/execute boundary instead. Existing
unmarked basetemps remain preserved because pre-policy roots cannot be classified as
failed versus explicitly kept; reclaiming them is an operator decision, not an inferred
automatic migration.
