# Quality Review
Date: 2026-04-11

## Scope

Current repo-wide quality posture after a `quality` dogfood session caught
checked-in plugin export drift in the canonical local bar and promoted that
drift check into `validate-packaging`.

## Current Gates

- `./scripts/run-quality.sh` remains the canonical local gate.
- `.githooks/pre-push` enforces that gate in clones that installed
  `./scripts/install-git-hooks.sh`.
- `./scripts/run-quality.sh` runs independent phases in parallel, records
  per-command timing, and keeps verbose success logs as an explicit
  `CHARNESS_QUALITY_VERBOSE=1` opt-in.
- `scripts/check-secrets.sh` prefers `gitleaks` and falls back to repo-local
  `secretlint` when `gitleaks` is unavailable.
- `scripts/check-supply-chain.py` now enforces repo-local manifest and
  lockfile alignment for npm/pnpm/yarn/bun surfaces plus `uv.lock`
  presence when Python dependencies are declared.
- `scripts/validate-packaging.py` now fails closed when the checked-in plugin
  tree drifts from the generated install surface, not only when manifest JSON
  or top-level marketplace artifacts drift.
- `scripts/record_quality_runtime.py` keeps a compact current timing summary
  plus rotated monthly archives.
- `scripts/validate-quality-artifact.py` keeps this file short and current.
- `scripts/validate-maintainer-setup.py` now fails closed when this clone has
  not actually activated the checked-in pre-push hook.
- `scripts/check-links-external.sh` scopes `lychee` to extracted external
  `http(s)` URLs, with online validation as an explicit `CHARNESS_LINK_CHECK_ONLINE=1` opt-in.

## Runtime Signals

- standing quality gates now write per-command elapsed time to
  `skill-outputs/quality/runtime-signals.json`
- the current runtime summary includes `check-supply-chain`, and older timing
  samples rotate into monthly `history/runtime-signals-YYYY-MM.jsonl` archives
- success output stays bounded while preserving failing-command diagnostics and
  per-command timing, so operability drift is visible without noisy happy-path logs
- this session proved the local bar can catch install-surface drift before
  pre-push, because `run-quality` surfaced a managed-checkout update failure
  caused by an unsynced checked-in plugin export

## Healthy

- quality, packaging, profile, adapter, integration, and representative-skill
  validators all run through one repo-owned entrypoint.
- maintainer-local hook drift is no longer invisible: the canonical quality
  runner now checks whether this clone actually points `core.hooksPath` at the
  checked-in `.githooks` directory.
- the quality runner overlaps low-coupling validators and heavy test/eval
  seams by phase instead of paying unnecessary serial pre-push cost.
- routine pre-push output is now agent-readable at a glance because passing
  runs no longer replay linter/test stdout unless verbose mode was requested.
- the control plane now tracks `cautilus` as a real external evaluator
  boundary instead of a deferred placeholder.
- `spec` and `quality` now explicitly tell executable-spec repos to keep specs
  at acceptance level, delete overlap, and move duplicated shell-heavy detail
  into cheaper lower layers.
- the external-link gate checks real external URLs from maintained docs and
  metadata without blocking routine pre-push runs on default unauthenticated network backoff.
- internal markdown-link discipline now has a repo-owned deterministic owner
  again instead of being implicitly delegated to a network-oriented link
  checker that never enforced it.
- checked-in plugin export drift is no longer only a pre-push concern: the
  canonical packaging validator now compares the generated plugin tree against
  the committed tree and fails on content drift.
- `quality` now ships package-manager-specific security references for npm,
  pnpm, and uv instead of leaving supply-chain follow-up as handoff-only prose.

## Weak

- this dogfood exposed a reporting gap in `quality` itself: speed, coverage
  absence, and evaluator-depth status were available but not surfaced first.
- some public skills still have durable artifacts or onboarding seams without a
  checked-in adapter contract.
- external-link validation still depends on network reachability and upstream
  host health when `CHARNESS_LINK_CHECK_ONLINE=1` is enabled locally.
- the new supply-chain gate proves manifest/lockfile discipline, but it does
  not yet prove live advisory visibility or triage behavior.
- the current secret gate was validated through repo-owned tests and fallback
  logic, but `gitleaks` itself was not exercised live in this clone because
  the binary is not installed locally.

## Missing

- no automated current-repo gate yet that decides which public skills must ship
  adapters versus which can stay adapter-free honestly.
- no maintained evaluator-backed `cautilus` scenario path yet for the
  `evaluator-required` public skills beyond the current integration manifest
  and root adapter seam.
- no optional online advisory/audit seam yet for npm/pnpm/uv that names the
  binary, network dependency, and triage owner explicitly.

## Deferred

- `profile extends`
- preset structure depth beyond the current markdown-first contract
- any stronger host packaging artifact strategy beyond the checked-in root
  manifests

## Commands Run

- `./scripts/run-quality.sh`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate-packaging.py --repo-root .`
- `pytest -q tests/test_quality_gates.py -k 'validate_packaging_passes_on_current_repo or validate_packaging_rejects_checked_in_plugin_tree_drift or sync_root_plugin_manifests_writes_install_surface'`
- `pytest -q tests/test_quality_gates.py -k 'run_quality or record_quality_runtime'`
- `./scripts/check-secrets.sh`
- `python3 scripts/check-supply-chain.py --repo-root .`
- `pytest -q tests/test_quality_gates.py`

## Recommended Next Gates

- `AUTO_CANDIDATE`: tighten the `quality` closeout contract so the first report
  always states runtime hot spots, coverage-gate presence, and evaluator depth.
- `AUTO_CANDIDATE`: classify which public skills require a checked-in adapter
  contract and fail closed when a durable-artifact or onboarding-heavy skill
  lacks one.
- `AUTO_CANDIDATE`: add a read-only test path that proves managed-checkout
  `charness update` stays clean against the current worktree or an ephemeral
  source bundle, so local uncommitted install-surface drift cannot hide behind
  `git clone` semantics during CLI tests.
- `AUTO_CANDIDATE`: add an optional networked advisory wrapper for npm/pnpm/uv
  only if the repo is prepared to own binary setup, flaky-host behavior, and triage.
- `AUTO_CANDIDATE`: if a downstream repo does not already carry Node tooling,
  prefer `gitleaks` over `secretlint` for the first secret gate to avoid
  turning secret scanning into a package-manager adoption decision.
- `AUTO_CANDIDATE`: add a deterministic smoke path for shipped support-sync
  contracts so `agent-browser`-style upstream support references cannot drift
  silently.
- `AUTO_CANDIDATE`: connect the new `cautilus` integration manifest to honest
  maintained scenarios for `evaluator-required` skills without pretending the
  current repo-local bar already has that depth.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
