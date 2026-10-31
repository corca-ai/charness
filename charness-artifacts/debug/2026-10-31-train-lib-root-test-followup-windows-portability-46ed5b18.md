# Debug: train library test root selection
Date: 2026-10-31

## Problem

`test_load_train_lib_inserts_missing_repo_root` once found the installed checkout at `sys.path[0]` instead of the test checkout during the release pytest run.

## Correct Behavior

Given a selected checkout absent from `sys.path`, when `_load_train_lib` runs, then the selected checkout is inserted; the insertion test should not depend on unrelated resolver state.

## Observed Facts

The test passed an empty namespace to `_resolve_worktree_lib_root`.
With `EMBEDDED_REPO_ROOT = None`, the resolver falls through to the managed checkout; on this host that is `/home/hwidong/.agents/src/charness`.
The resolver also accepts an embedded root first; the original failed run did not capture its value.
The hook runtime environment sets cache and temp paths, but does not select the checkout.

## Reproduction

With the train module preloaded, clear the embedded root and remove both checkout paths from `sys.path`; `_load_train_lib(argparse.Namespace())` inserts the installed checkout.

## Candidate Causes

- An unset shared embedded root causes managed-install fallback; an embedded installed root could produce the same observed path.
- Module import side effects can reinsert the source checkout and mask the wrong resolver result.

## Hypothesis

- Pinning the resolver return to the test checkout makes the insertion assertion independent of bootstrap state and import order | disconfirmer: run with the embedded root unset and train module preloaded.

## Verification

- Confirmed: the unpinned resolver selected the installed checkout with the embedded root unset; the pinned test passes with the same state and module preloaded.
- The entire test file passes with eight xdist workers, reverse collection order, and the hook runtime environment.

## Root Cause

The insertion test relied on a mutable, process-wide bootstrap root while passing no explicit worktree root.
The exact bootstrap value in the original failure was not recorded, so its particular upstream setter is unproven.

## Invariant Proof

- Invariant: the insertion test checks the path chosen by its resolver, independently of resolver policy.
- Producer Proof: the test replaces `_resolve_worktree_lib_root` with a fixed checkout result.
- Final-Consumer Proof: the test checks the path inserted by `_load_train_lib`.
- Interface-Shape Sibling Scan: `test_task_run_lib_root.py` separately tests source and managed checkout policy.
- Non-Claims: this does not identify the original run's bootstrap setter.

## Detection Gap

- Earlier full lanes passed because bootstrap context and module import order varied; the controlled resolver result removes that dependency.
- Scoped critique: pinning must not replace product resolver coverage; `test_task_run_lib_root.py` independently covers its policy.

## Sibling Search

- Mental model: importing the CLI implies the current checkout remains the selected root for every later test.
- Same file: the insertion test is the only assertion of this train-loader path.
- Cross-file: `tests/charness_cli/test_task_run_lib_root.py` explicitly controls bootstrap state and tests resolver policy.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: the exact bootstrap value during the original failure.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Tests of loader insertion should supply their selected root; resolver policy tests should own checkout selection.
