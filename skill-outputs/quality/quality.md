# Quality Review
Date: 2026-04-12

## Scope

Repo-wide quality posture after a clean `./scripts/run-quality.sh` pass and a
same-session tightening of the `quality` closeout contract. `Runtime Signals`
is now required to state hot spots, coverage-gate status, and evaluator depth
instead of leaving that as prose-only advice.

## Current Gates

- `./scripts/run-quality.sh` is the canonical local bar.
- `.githooks/pre-push` runs `scripts/sync_root_plugin_manifests.py` and then
  `./scripts/run-quality.sh`; `scripts/install-git-hooks.sh` wires
  `core.hooksPath`.
- `scripts/validate-maintainer-setup.py` fails closed when this clone is not
  actually using the checked-in `.githooks`.
- `scripts/run-quality.sh` runs parallel phases, records per-command timing,
  supports `CHARNESS_QUALITY_LABELS`, and only replays passing logs under
  `CHARNESS_QUALITY_VERBOSE=1`.
- `scripts/check-secrets.sh` prefers `gitleaks` and falls back to repo-local
  `secretlint`.
- `scripts/check-supply-chain.py` enforces manifest/lockfile alignment for
  npm/pnpm/yarn/bun plus `uv.lock` when Python deps exist.
- `scripts/validate-packaging.py` fails on checked-in plugin export drift.
- `scripts/validate-quality-artifact.py` now requires explicit runtime hot
  spots, coverage-gate status, and evaluator depth in this artifact.
- `scripts/check-links-external.sh` scopes `lychee` to extracted external URLs,
  with online validation behind `CHARNESS_LINK_CHECK_ONLINE=1`.

## Runtime Signals

- runtime hot spots: current latest timings are `pytest` 25.0s,
  `check-secrets` 2.5s, `check-markdown` 1.9s; `run-evals` is 1.3s and
  everything else is below that.
- coverage gate: none; the local bar proves pass/fail across validators,
  tests, and evals but does not measure line or branch coverage.
- evaluator depth: `run-evals` covers adapter bootstrap, fixture portability,
  support-sync contracts, and representative skill contracts, but not
  maintained evaluator-backed `cautilus` scenarios for `evaluator-required`
  skills.
- runtime retention: per-command timings live in
  `skill-outputs/quality/runtime-signals.json`, older samples rotate into
  monthly `history/runtime-signals-YYYY-MM.jsonl`, and passing runs keep stdout
  bounded.

## Healthy

- one repo-owned entrypoint covers validators, docs, lint, tests, evals,
  duplicate detection, and supply-chain checks.
- maintainer-local enforcement is honest: checked-in pre-push hook, repo-owned
  installer, and standing validator all exist.
- packaging drift is caught both before push and in standing validation.
- internal markdown-link discipline and external URL health have separate
  owners instead of one noisy mixed gate.
- test suites are split by seam under
  `tests/{quality_gates,charness_cli,control_plane}`, which keeps the
  `500`-line test-file cap enforceable.
- the quality artifact now has a deterministic closeout contract for speed,
  coverage absence, and evaluator depth.

## Weak

- some public skills still have durable artifacts or onboarding seams without
  checked-in adapter contracts.
- external-link validation still depends on network reachability and upstream
  host health when online mode is enabled.
- the supply-chain gate proves manifest/lockfile discipline, not live advisory
  visibility or triage behavior.
- the secret gate fallback is tested, but the `gitleaks` binary path was not
  exercised live in this clone because the binary is not installed.

## Missing

- no automated current-repo gate yet decides which public skills must ship
  adapters versus which can stay adapter-free honestly.
- no maintained evaluator-backed `cautilus` scenario path yet exists for
  `evaluator-required` public skills.
- no optional online advisory wrapper yet names the binary, flaky-host
  behavior, and triage owner for npm/pnpm/uv surfaces.
- no coverage gate yet if the repo decides it wants quantitative test-depth
  enforcement rather than pass/fail only.

## Deferred

- `profile extends`
- preset structure depth beyond the current markdown-first contract
- any stronger host packaging artifact strategy beyond the checked-in root
  manifests

## Commands Run

- `./scripts/run-quality.sh`
- `git config --get core.hooksPath`
- `find .git/hooks -maxdepth 1 -type f | sort`
- `python3 scripts/validate-quality-artifact.py --repo-root .`
- `pytest -q tests/test_quality_artifact.py`

## Recommended Next Gates

- `AUTO_CANDIDATE`: classify adapter-required public skills and fail closed
  when a durable-artifact or onboarding-heavy skill lacks a checked-in adapter
  contract.
- `AUTO_CANDIDATE`: add a read-only proof that `charness update` stays clean
  against the current worktree or an ephemeral source bundle so local drift
  cannot hide behind `git clone` semantics.
- `AUTO_CANDIDATE`: add an optional networked advisory wrapper for npm/pnpm/uv
  only if the repo is willing to own binary setup, flaky-host behavior, and
  triage.
- `AUTO_CANDIDATE`: if quantitative test depth becomes necessary, add a scoped
  coverage gate around `tests/charness_cli` and `tests/control_plane` instead
  of a blanket repo-wide percentage floor.
- `AUTO_CANDIDATE`: connect the `cautilus` integration manifest to honest
  maintained scenarios without pretending the current repo-local bar already
  has that depth.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
