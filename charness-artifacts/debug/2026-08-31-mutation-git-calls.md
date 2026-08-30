# Debug Review
Date: 2026-08-31

## Problem

The standing suite repeatedly invokes mutation changed-pool Git reads, and a
process-global filesystem-token cache was proposed as a large reduction.

## Correct Behavior

Repeated reads inside one operation may share an explicit immutable snapshot.
Separate operations must not reuse Git results unless the cache key completely
represents Git semantics and the reuse works across the process boundaries that
created the measured cost.

## Observed Facts

- The attributed census recorded 252 calls from
  `changed_pool_files_vs_base`: 126 untracked reads and 126 base diffs.
- Those calls occur across separate Python processes in the standing suite.
- The proposed module-global cache existed inside each Python process, so it
  could not collapse the suite to one read per base as predicted.
- Its token did not bind every Git semantic input, including linked-worktree
  common metadata and Git environment overrides.

## Reproduction

- Inspect `/tmp/charness-final-spawn-probe/final-standing-v7-20260831.jsonl`
  grouped by `mutation_changed_files_lib.py:changed_pool_files_vs_base`.

## Candidate Causes

- Unrelated CLI behavior tests reconstruct the same repository-backed mutation
  snapshot.
- Product-global caching was mistaken for operation-scoped snapshot ownership.
- The estimate counted distinct bases but ignored distinct Python processes.

## Hypothesis

If a filesystem-token module cache owns the results, the standing suite will
drop from 252 Git calls to roughly ten without weakening freshness.

disconfirmer: compare the proposed cache lifetime with the Python process IDs
that own the 252 attributed calls, then enumerate Git semantic inputs absent
from the token before accepting any speed estimate.

## Verification

- Result: refuted before merge. The cache boundary is per process, while the
  repeated calls cross processes; its invalidation token is also incomplete.
- The cache implementation and cache-specific tests were removed.
- Existing safe batching of changed-line diffs over immutable object IDs remains.

## Root Cause

The proposed optimization placed reuse below the operation boundary. It tried
to infer semantic freshness from selected filesystem metadata and optimized a
test-process layout rather than the consumer operation.

## Invariant Proof

- Invariant: no cross-operation Git result reuse from a partial filesystem token.
- Producer Proof: `changed_pool_files_vs_base` performs fresh Git reads.
- Final-Consumer Proof: focused mutation tests after cache removal.
- Interface-Shape Sibling Scan: reviewed-input identity had the same proposed
  global-cache shape and was rejected for the same reason.
- Non-Claims: the 252-call residual is not claimed fixed by this record.

## Detection Gap

- process attribution | caller counts did not initially name the owning pytest
  test | the external census now records `PYTEST_CURRENT_TEST`.
- cache review | positive invalidation tests covered only selected state changes
  | require a complete semantic-key argument or keep reuse operation-scoped.

## Sibling Search

- Mental model: an unchanged-looking filesystem is equivalent to unchanged Git semantics.
- same layer: reviewed-input global cache | decision: same risk, remove | proof: linked-worktree and environment counterexamples.
- abstraction up: CLI test matrices | decision: investigate next | proof: attributed test ownership.
- specialization down: immutable object-ID diff cache | decision: retain | proof: full object IDs are immutable content identities.
- cross-file: `scripts/reviewed_input_identity.py` | decision: same global-cache
  error, remove | proof: linked-worktree and environment counterexamples.

## Seam Risk

- Interrupt ID: mutation-global-cache-2026-08-31
- Risk Class: none
- Seam: filesystem token -> Git semantic result
- Disproving Observation: separate processes and unbound Git semantic inputs
- What Local Reasoning Cannot Prove: complete Git cache-key coverage
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Prefer operation-scoped snapshots and batched Git protocols. Treat global caches
of mutable repository state as correctness changes, not test-speed tweaks.
