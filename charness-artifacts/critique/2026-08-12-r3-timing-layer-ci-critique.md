# R3 Timing-Layer CI Critique

Date: 2026-08-12

## Execution

Two bounded, read-only fresh-eye rounds reviewed the Quality Core step and its
focused regression proof. Both reviewer-boundary fingerprints verified clean.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- Requested tier: n/a — host inherited the session model.
- Requested spawn fields: unnamed bounded read-only reviewer scope, exact
  workflow/test paths, and blocker/major/minor reporting through the host agent
  interface.
- Host exposure state: metadata-hidden
- Application state: the host returned no reviewer-tier application metadata.
- Delivery state: findings-received

## Boundary Ownership

- Producer: `check_timing_layer_completeness.py` owns the timing-table verdict.
- Consumer: Quality Core executes that exact repo-owned command for push/tag/PR
  changes that can bypass an installed local hook.
- Owning surface: Quality Core local-gate subset mirror.
- Verdict: owned-correctly

## Target

Code critique: CI scheduling of an existing timing-layer verdict and its
local/CI scope guard.

## Change

Add the exact existing timing-layer completeness command to Quality Core. Keep
the commit-time dispatcher and docs-only pre-push selection unchanged.

## Capability at Stake

An unhooked contributor, web-UI edit, or `--no-verify` path reaches the
existing timing-layer verdict in CI without charging the fast docs-only push
lane a duplicate, unscoped check.

## Findings and Counterweight Triage

- R1-F1 | act-before-ship | The initial test used raw substring assertions, so
  a comment could satisfy the CI assertion and a deleted docs-only label could
  satisfy the hook assertion. Repaired by matching the actual adjacent YAML
  `name`/`run` step and pinning the complete 14-label docs-only list.
- R2 | no findings | The repaired guard requires the exact existing command,
  retains every docs-only label, and excludes the timing-layer label.
- Over-worry | Do not add `check-timing-layer-completeness` to
  `DOCS_ONLY_LABELS`; commit-time ownership already covers its two changed
  inputs, and the ruling expressly preserves the fast pre-push lane.
- Valid but defer | A hosted CI run is not claimed: no push was authorized.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — proof surfaces must assert the
actual consumer step rather than a nearby textual spelling.

## Deliberately Not Doing

- No new validator or duplicate implementation.
- No pre-push label, hook installation, push, hosted CI readback, or release.

## Pre-Merge Action

Focused timing/CI/static checks passed. The round-1 repair was independently
read in round 2; no round-2 repair was needed.
