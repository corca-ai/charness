# Cumulative Closeout Staged-Scope Coupling Debug
Date: 2026-07-19

## Problem

`run_slice_closeout.py --base <campaign>` sent every historical campaign path
through the staged commit structural sweep. A later cumulative lock therefore
rechecked Slice 2's snapshot-bound verdict against the Slice 5 worktree and
blocked because normal later changes made the old verdict stale.

## Correct Behavior

Campaign paths own cumulative sync/verify/broad-proof scope. Staged structural
gates own only the current live worktree/index paths.

## Observed Facts

- The cumulative payload correctly included all commits since `9a70c60d`.
- `block_on_structural_sweep` consumed that same payload list unchanged.
- Historical critique packet integrity passed under repository-wide validation,
  but current applicability correctly failed after later slices.
- Bare `--base` resolves through the auto path without an explicit campaign SHA.

## Reproduction

Run `python3 scripts/run_slice_closeout.py --repo-root . --base 9a70c60d
--verification-lock`; before the repair, the structural sweep stops on Slice 2's
now-stale declared inputs before reaching cumulative proof.

## Candidate Causes

- Historical critique validation was too strict in every context.
- Slice 2 verdict binding made ordinary later changes invalid.
- Cumulative proof paths were reused as if they were current staged paths.

## Hypothesis

The closeout caller conflates proof scope and commit-boundary scope. Disconfirmer:
a live-only structural path override still sends historical critique paths to the
staged gate or drops them from the cumulative proof payload.

## Verification

- confirmed — focused tests retain historical paths in the payload, route only
  live staged/unstaged paths to the sweep for explicit and auto bases, and keep
  no-base behavior unchanged; 84 tests pass.

## Root Cause

The staged structural sweep reused `payload["changed_paths"]`, whose meaning
expands from “live diff” to “campaign range plus live diff” under `--base`.
Neither owner represented the distinction explicitly at their call seam.

## Invariant Proof

- Invariant: cumulative evidence scope and current commit-gate scope may overlap
  but are not interchangeable.
- Producer Proof: `run_slice_closeout` derives live structural paths separately
  whenever any `--base` mode is active.
- Final-Consumer Proof: structural sweep accepts the explicit live list while
  payload and broad-proof collectors retain the campaign range.
- Interface-Shape Sibling Scan: plan-only receives the same live structural
  list; other structural-sweep callers keep the existing default.
- Non-Claims: historical critique verdicts are not made current; only packet
  integrity remains durable after their reviewed inputs evolve.

## Detection Gap

- cumulative closeout | unit tests covered base collection and structural sweep
  separately | added caller tests for explicit/auto base scope separation

## Sibling Search

- Mental model: one `changed_paths` name hid two temporal scopes.
- plan axis: plan-only command rendering | decision: fixed in the same seam |
  proof: explicit `structural_paths` is forwarded to planned commands.
- cross-file: `staged_commit_gate_plan.py` now accepts an optional path override
  without changing its pre-commit callers.

## Seam Risk

- Interrupt ID: cumulative-closeout-staged-scope-coupling
- Risk Class: none
- Seam: campaign path collection -> staged structural sweep
- Disproving Observation: a historical-only artifact reaches the staged sweep
  during a clean post-commit `--base` closeout
- What Local Reasoning Cannot Prove: every future caller will preserve the two
  scopes without naming them
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Pass temporal scope explicitly at the boundary: cumulative payload paths remain
proof inputs, while staged structural commands consume only live diff paths.
