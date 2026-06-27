# Broad Pytest Proof Base Scope Debug
Date: 2026-06-27

## Problem

`run_slice_closeout.py --base auto --verification-lock --refresh-broad-pytest-proof`
reported a broad pytest proof whose top-level `changed_paths` covered the full
slice, but whose cached `recorded_broad_pytest_proofs.changed_paths` contained
only the staged follow-up files.

## Correct Behavior

Given a closeout payload scoped with `--base`, when broad pytest proof is
recorded or reused, then the proof fingerprint must include the payload's
committed-range paths as well as any live worktree paths created during closeout
execution.

## Observed Facts

The closeout payload listed the full slice path set, including committed docs,
root scripts, plugin exports, and tests. The recorded broad pytest proof listed
only three staged follow-up paths. `run_slice_closeout.py` passed
`collect_changed_paths` directly into `execute_command_plan`, so broad proof
recording recomputed the live working-tree diff instead of reusing the already
resolved payload scope.

## Reproduction

Run a closeout after one slice commit exists and additional fixes are staged:
`run_slice_closeout.py --base auto --verification-lock
--refresh-broad-pytest-proof`. Inspect the JSON payload. The top-level
`changed_paths` includes the committed range; the broad proof record may contain
only currently dirty paths.

## Candidate Causes

- Payload matching lost paths before broad proof recording.
- Broad proof cache writer truncated `changed_paths` before persisting.
- The executor received the working-tree collector instead of a collector scoped
  to the closeout payload.

## Hypothesis

If the executor records broad proof by calling the default working-tree
collector, then committed `--base` paths disappear from the proof fingerprint
whenever the working tree contains only staged follow-up files.

## Verification

The call site in `run_slice_closeout.py` passed `collect_changed_paths` to
`execute_command_plan`. The helper `_resolve_changed_paths` had already
computed the correct base range for the payload, but that list was not carried
into the broad proof collector. A regression test now asserts that the broad
proof scope collector keeps initial base-range paths while adding live worktree
paths.

## Root Cause

The closeout had two different concepts of changed paths: payload scope used
`--base`, while broad proof cache scope recomputed the default working-tree
diff. The proof cache therefore fingerprinted a narrower evidence boundary than
the closeout claimed.

## Invariant Proof

- Invariant: broad pytest proof cache scope equals the closeout validation scope
  plus live sync-generated worktree changes.
- Producer Proof: `_closeout_changed_paths_collector` unions payload paths with
  `collect_changed_paths(repo_root)`.
- Final-Consumer Proof: `test_broad_pytest_proof_scope_keeps_base_range_and_live_worktree`
  exercises committed-range plus dirty-file scope.
- Interface-Shape Sibling Scan: mutation coverage fingerprints already carry
  producer metadata separately; this repair is limited to broad pytest cache
  path scope.
- Non-Claims: this does not prove every cached proof was historically scoped
  correctly.

## Detection Gap

- closeout proof cache tests | no test modeled committed `--base` paths plus
  later live worktree paths | add the base-range/live-worktree union regression.

## Sibling Search

- Mental model: "changed paths" was treated as a single source, but payload
  scope and live worktree scope had diverged.
- cross-file: scripts/slice_closeout_command_executor.py | decision: keep the
  executor generic and fix the caller-provided collector | proof: call-site
  review plus targeted regression.

## Seam Risk

- Interrupt ID: broad-pytest-proof-base-scope-2026-06-27
- Risk Class: none
- Seam: none
- Disproving Observation: local closeout JSON showed the mismatch directly.
- What Local Reasoning Cannot Prove: none
- Generalization Pressure: none

## Interrupt Decision

- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep cache proof fingerprints tied to the already resolved validation payload,
not to a late default collector that silently changes semantics under `--base`.
