# Debug Review: Immutable Reviewed-Input Seed
Date: 2026-08-31

## Problem

The 16-worker standing suite failed while copying the shared reviewed-input Git
seed: `shutil.Error` reported that `.git/index.lock` existed during directory
enumeration but was gone when copied. The run ended with 8,661 passes and one
failure.

## Correct Behavior

Given a source-bound cached seed, when parallel tests need repository state or a
derived identity, then the builder publishes one immutable bundle and consumers
either read bundled bytes or copy the repository before running Git. No consumer
runs Git against the shared repository.

## Observed Facts

- `build_reviewed_input_identity()` ran `git status` directly in the shared seed
  from four xdist consumers. Git documents that status refreshes the index and
  may take an optional lock even though the requested result is read-only.
- Luna reproduced `open(.git/index.lock, O_CREAT|O_EXCL)` followed by `unlink`
  under `strace`; this exactly explains the disappearing path in `copytree`.
- The seed cache serialized construction, but not later reads, because its ready
  marker promises immutable output.
- Pattern ladder: observed failure = disappearing lock during copy; local
  pattern = derived identity recomputed against shared `.git`; interface sibling
  = four process-local caches sharing one filesystem seed; pattern of patterns =
  logical read-only intent was mistaken for filesystem immutability.

## Reproduction

- `/tmp/charness-standing-v14-20260831.jsonl` with the canonical standing runner:
  8,661 passed, one `test_issue_worker_carrier` failure at shared
  `.git/index.lock`.
- Independent `strace` of the exact status path observed index lock create and
  unlink on a clean seed.

## Candidate Causes

- Git status optionally refreshed the shared seed index while another worker copied it.
- Seed pruning or rebuilding removed files despite a ready marker.
- A test explicitly mutated the shared repository rather than a private copy.

## Hypothesis

- If repeated identity capture is the writer, bundling the canonical identity
  during locked seed construction and removing all direct shared-seed capture
  will eliminate the race and its Git calls. Disconfirmer: any remaining
  `build_reviewed_input_identity(repo_seed())` consumer or fresh-cache parallel
  failure.

## Verification

- Confirmed: source scan found four direct consumers; all now read the bundled
  JSON identity. No direct consumer remains.
- Confirmed: fresh empty cache, 16 workers, four consumer suites: 80 passed.
- Confirmed: broader reviewed-input set, 16 workers: 115 passed; the original
  87-test set passed three additional consecutive 16-worker runs.
- Two Luna reviews found one blocker: old ready caches lacked the new sidecar.
  The seed name is versioned `-v2`, so the output-schema change cannot reuse them.
- Final standing proof: 8,662 passed in 67.32 seconds; the census recorded 5,679
  Git launches, down from v13's 6,139, with no seed-copy race.

## Root Cause

The fixture contract called the repository seed immutable while allowing
consumers to execute Git against it. Git's result was observationally read-only,
but status performs an optional index write. Per-process `@cache` reduced repeat
work inside one worker and hid the cross-process ownership error; it did not make
the shared filesystem immutable.

## Invariant Proof

- Invariant: the seed builder is the only process allowed to run Git in the
  shared bundle; post-ready consumers only read sidecar bytes or copy the repo.
- Producer Proof: `_build_seed` creates the commit and canonical identity before
  the ready marker is published.
- Final-Consumer Proof: packet, worker-carrier, semantic-review, and identity
  consumers passed together from a fresh cache under 16 workers.
- Interface-Shape Sibling Scan: all `repo_seed()` identity captures were searched;
  four were converted and ordinary clone-local captures remain intentional.
- Non-Claims: this does not change production identity semantics or mutation tests.

## Detection Gap

- Immutable seed fixture | the existing test proved clone mutations did not alter
  the seed, but never exercised concurrent logical reads | run the four consumers
  together from a fresh cache under xdist and forbid shared-seed derived reads by API.
- Cache output schema | a ready marker did not encode sidecar shape | version the
  seed name whenever the bundle's required outputs change.

## Sibling Search

- Mental model: a read-only Git question cannot mutate repository files.
- same layer: four reviewed-input consumers | decision: same bug, fix now | proof:
  source scan plus parallel runtime failure.
- abstraction up: other seed helpers copy before Git | decision: intentional
  boundary | proof: `copy_worktree_seed` and repo-copy helpers return private copies.
- specialization down: clone-local identity capture | decision: intentional
  boundary | proof: each target lives under pytest tmp.
- cross-file: `tests/seed_cache.py` ready-marker contract | decision: same bug,
  fixed by versioned bundle name | proof: stale-cache counter-review.

## Seam Risk

- Interrupt ID: reviewed-input-seed-immutability-2026-08-31
- Risk Class: none
- Seam: xdist workers consuming one filesystem cache bundle
- Disproving Observation: fresh-cache parallel consumer run is green.
- What Local Reasoning Cannot Prove: behavior on filesystems not exercised here.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Result: two Luna fresh-eye reviews completed; one cache-schema blocker
  was fixed, while stale-dict and import-cycle concerns were over-worry.
- Next Step: impl
- Handoff Artifact: none

## Prevention

Cached repository seeds are immutable publication bundles, not shared working
trees. Derive reusable metadata once while the builder owns the lock, version the
bundle name when required outputs change, and make every test-local mutation or
Git observation operate on a private copy.
