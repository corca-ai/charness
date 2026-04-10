# Quality Review
Date: 2026-04-10

## Scope

Current repo-wide quality posture after tightening local enforcement,
splitting quality history from the current snapshot, adding the first
Google Workspace `gws-cli` gather seam, and tightening executable-spec
guidance around cost, overlap, and adapter depth.

## Current Gates

- `./scripts/run-quality.sh` remains the canonical local gate.
- `.githooks/pre-push` enforces that gate in clones that installed
  `./scripts/install-git-hooks.sh`.
- `scripts/record_quality_runtime.py` now records per-gate elapsed time into a
  compact current summary plus rotated monthly archives.
- `scripts/validate-quality-artifact.py` now keeps this file short and shaped
  as a current snapshot instead of an ever-growing session log.
- `scripts/validate-maintainer-setup.py` now fails closed when this clone has
  not actually activated the checked-in pre-push hook.

## Runtime Signals

- standing quality gates now write per-command elapsed time to
  `skill-outputs/quality/runtime-signals.json`
- older timing samples rotate into monthly `history/runtime-signals-YYYY-MM.jsonl`
  archives instead of accumulating in the current snapshot
- `quality` should now treat lint/test/runtime drift and bounded diagnostic
  retention as operability quality, not as an afterthought

## Healthy

- quality, packaging, profile, adapter, integration, and representative-skill
  validators all run through one repo-owned entrypoint.
- the repo now distinguishes `charness`-owned gather runtime from true
  external binaries, and Google is modeled as `gws-cli` rather than a copied
  helper path.
- public `gather` now has a repo-owned helper for Google Workspace operator
  guidance instead of relying on ad hoc memory.
- maintainer-local hook drift is no longer invisible: the canonical quality
  runner now checks whether this clone actually points `core.hooksPath` at the
  checked-in `.githooks` directory.
- the control plane now tracks `cautilus` as a real external evaluator
  boundary instead of a deferred placeholder.
- `spec` and `quality` now explicitly tell executable-spec repos to keep specs
  at acceptance level, delete overlap, and move duplicated shell-heavy detail
  into cheaper lower layers.

## Weak

- some public skills still have durable artifacts or onboarding seams without a
  checked-in adapter contract.

## Missing

- no maintained evaluator-backed `cautilus` scenario path yet for the
  `evaluator-required` public skills beyond the current integration manifest
  and root adapter seam.
- no automated current-repo gate yet that decides which public skills must ship
  adapters versus which can stay adapter-free honestly.

## Deferred

- `profile extends`
- preset structure depth beyond the current markdown-first contract
- any stronger host packaging artifact strategy beyond the checked-in root
  manifests

## Commands Run

- `./scripts/run-quality.sh`
- `cat skill-outputs/quality/runtime-signals.json`
- `python3 scripts/doctor.py --repo-root . --tool-id gws-cli --json`
- `python3 scripts/validate-maintainer-setup.py --repo-root .`

## Recommended Next Gates

- `AUTO_CANDIDATE`: classify which public skills require a checked-in adapter
  contract and fail closed when a durable-artifact or onboarding-heavy skill
  lacks one.
- `AUTO_CANDIDATE`: add a deterministic smoke path for shipped support-sync
  contracts so `agent-browser`-style upstream support references cannot drift
  silently.
- `AUTO_CANDIDATE`: connect the new `cautilus` integration manifest to honest
  maintained scenarios for `evaluator-required` skills without pretending the
  current repo-local bar already has that depth.
- `AUTO_CANDIDATE`: when a repo relies on logs or machine-readable diagnostics
  for debugging or operations, add deterministic checks for bounded retention
  and rotation instead of letting those artifacts grow invisibly.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
