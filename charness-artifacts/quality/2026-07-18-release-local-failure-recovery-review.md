# Quality Review
Date: 2026-07-18
Title: Retryable local release failures

## Scope

Target boundary: release-helper mutations from a clean starting commit through local release commit/tag creation and structured failure reporting.

Ambient repo findings: D18 remains ignored. No version bump, tag, push, release, or Cautilus evaluation belongs to this deterministic recovery slice.

## Current Gates

- Existing focused release tests, source/plugin sync, packaging validation, ruff, changed-line mutation proof, read-only quality, and locked slice closeout own the change.
- No new blocking floor was added; recovery is executable behavior in the existing release helper.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`, <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`.
- runtime hot spots: read-only quality passed 81/81 in 60.2s; pytest used 40.0s.
- coverage gate: locked broad proof and focused coverage production passed; eligible worktree lines remain an explicit `NOT CHECKED` until the exact `3c2516b9..HEAD` consumer runs after commit.
- evaluator depth: deterministic-gates-only because Git status, HEAD, restored bytes, tag target, and failure payloads are directly observable.
- No speedup is claimed; this slice targets retry cost and correctness rather than steady-state runtime.

## Healthy

- Pre-commit release preparation snapshots the clean HEAD and restores tracked paths from it when preparation, quality, artifact staging, or commit fails.
- Newly created non-ignored paths are moved to a Git-data quarantine outside the worktree, preserving recovery material without blocking retry.
- Partial restore or quarantine failures report completed work, errors, and remaining status instead of claiming a clean rollback.
- Once a release commit exists, rollback refuses to rewrite history; resume can revalidate and create a missing local tag at the exact saved commit only while remote/public publication is absent.
- Root and packaged plugin scripts remain exact mirrors.

## Weak

- Ignored files are outside the rollback inventory. This is intentional for the current helper, but a future release producer that writes ignored state must declare and clean its own ledger.
- A failure after HEAD moves but before the artifact amend fully settles can still require a more explicit post-commit dirty-state recovery transition; this slice proves the observed clean missing-tag case, not every possible Git failure.

## Missing

- No fault test yet establishes the exact dirty worktree left by a failed post-commit artifact amend; the current resume proof covers clean missing-tag and ambiguous-remote states.

## Deferred

- Do not add a generic transaction framework until a second workflow demonstrates the same owned mutation set.
- Model post-commit dirty-state repair when a reproducible failure or focused fault seam establishes its exact state.

## Advisory

- artifact: critique prepare packet; structural review result: capability_needed=failed release returns clean retry-ready or defined resume state; current_centers=clean-start gate, failure payload, resume; next_center=local failure transition owner; transformation=small rollback helper plus narrowed resume transition; proof_boundary=Git integration fault tests; enforcement_posture=existing-gate reuse.
- command: release focused pytest; sequencing result: mutation-before-quality remains required because release quality must inspect bumped/generated surfaces; moving quality earlier would weaken proof, so rollback—not reordering—owns recovery.
- artifact: `publication-boundary.md`; prose review result: it now distinguishes pre-commit restoration from post-commit resume and keeps publication provisional.
- command: baseline read-only quality; target-boundary result: release-local recovery is the changed boundary; baseline test/runtime and existing length/clone notices remain ambient.

## Delegated Review

- Delegated Review: executed — Git correctness and release state-machine angles plus a separate counterweight ran read-only.
- Reviewers found rename restoration, too-narrow exception ownership, false partial-recovery evidence, missing-tag stranding, and plan-before-resume evidence drift; all blocking findings were repaired.
- Final correctness review returned `SHIP-READY`; parent fingerprint verification found no worktree/index/HEAD drift.

## Commands Run

- Baseline `./scripts/run-quality.sh --read-only`: 81 passed, 0 failed.
- Focused rollback/resume tests, focused ruff, source/plugin byte comparison, Markdown checks, and critique boundary fingerprints.
- Final focused release tests passed 57/57; packaging and locked broad read-only proof passed. Focused coverage production is rerun after the follow-up commit so the exact changed-line consumer sees the final `base..HEAD` range.

## Recommended Next Quality Moves

- passive keep resume identity derivation aligned with plan identity because the preflight intentionally duplicates only the minimum version/tag/commit inputs and focused tests currently prove parity.
- passive fault-inject the post-commit artifact-amend boundary before claiming all post-commit local failures are resumable because this slice has no reproducible dirty post-commit failure.
- active preserve the design rule: a clean-start workflow that mutates locally must make every owned failure either restore the start state or emit a typed resumable state.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
