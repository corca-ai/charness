# Quality Review
Date: 2026-04-12

## Scope

Repo-wide quality posture after tightening four previously missing gates:
public-skill adapter classification, evaluator-required cautilus scenario
contracts, optional online supply-chain audits, and scoped control-plane
coverage. `./scripts/run-quality.sh` now passes clean with all four in the
standing bar.

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
- `scripts/validate-public-skill-validation.py` fails when the current repo
  drifts on evaluator tiers or on adapter-required versus adapter-free public
  skill assignments.
- `scripts/validate-cautilus-scenarios.py` and
  `scripts/eval_cautilus_scenarios.py` keep the evaluator-required skill
  registry tied to maintained `run-evals` scenario IDs.
- `scripts/check-secrets.sh` prefers `gitleaks` and falls back to repo-local
  `secretlint`.
- `scripts/check-supply-chain.py` enforces manifest/lockfile alignment for
  npm/pnpm/yarn/bun plus `uv.lock` when Python deps exist, and
  `scripts/check-supply-chain-online.py` adds optional npm/pnpm/uv advisory
  probes with explicit binary and triage-owner reporting.
- `scripts/validate-packaging.py` fails on checked-in plugin export drift.
- `scripts/validate-quality-artifact.py` now requires explicit runtime hot
  spots, coverage-gate status, and evaluator depth in this artifact.
- `scripts/check-coverage.py` enforces a scoped control-plane coverage floor by
  tracing representative `charness`, `doctor`, `sync_support`, `update_tools`,
  and `install_tools` entrypoints against an ephemeral repo copy.
- `scripts/check-links-external.sh` scopes `lychee` to extracted external URLs,
  with online validation behind `CHARNESS_LINK_CHECK_ONLINE=1`.

## Runtime Signals

- runtime hot spots: current latest timings are `pytest` 36.4s,
  `check-coverage` 8.8s, `check-secrets` 2.6s, `check-markdown` 1.9s, and
  `run-evals` 1.5s.
- coverage gate: `python3 scripts/check-coverage.py --repo-root . --json`
  currently reports `62.9%` (`741/1178`) across the scoped control-plane target
  set with a required floor of `60.0%`; lowest modules are
  `support_sync_lib.py` `30.6%`, `install_provenance_lib.py` `55.9%`,
  `install_tools.py` `57.7%`, and `upstream_release_lib.py` `57.0%`.
- evaluator depth: `evals/cautilus/scenarios.json` now maps all
  `evaluator-required` public skills to maintained `run-evals` scenario IDs,
  and the cautilus adapter runs that registry in held-out and full-gate modes.
- runtime retention: per-command timings live in
  `skill-outputs/quality/runtime-signals.json`, older samples rotate into
  monthly `history/runtime-signals-YYYY-MM.jsonl`, and passing runs keep stdout
  bounded.

## Healthy

- one repo-owned entrypoint covers validators, docs, lint, tests, evals,
  duplicate detection, and supply-chain checks.
- maintainer-local enforcement is honest: checked-in pre-push hook, repo-owned
  installer, and standing validator all exist.
- adapter-required public skills now fail closed when checked-in example or
  bootstrap resolver artifacts are missing, and adapter-free skills cannot ship
  hidden adapter scaffolding.
- evaluator-required public skills now have a maintained scenario registry
  instead of prose-only cautilus depth claims.
- the online advisory wrapper names the binary surface, network dependency, and
  triage owner instead of pretending live supply-chain visibility is free.
- packaging drift is caught both before push and in standing validation.
- internal markdown-link discipline and external URL health have separate
  owners instead of one noisy mixed gate.
- test suites are split by seam under
  `tests/{quality_gates,charness_cli,control_plane}`, which keeps the
  `500`-line test-file cap enforceable.
- the quality artifact now has a deterministic closeout contract for speed,
  coverage status, and evaluator depth.

## Weak

- external-link validation still depends on network reachability and upstream
  host health when online mode is enabled.
- live advisory coverage is opt-in and only as strong as the locally installed
  npm/pnpm/uv binaries plus registry reachability.
- the secret gate fallback is tested, but the `gitleaks` binary path was not
  exercised live in this clone because the binary is not installed.
- the coverage gate is honest but intentionally scoped; several control-plane
  modules still sit below `60%` even though the aggregate floor passes.

## Missing

- no read-only proof yet shows that `charness update` stays clean against the
  current worktree or an ephemeral source bundle.
- no checked-in maintainer or CI profile currently exercises the optional
  online audit path with required binaries installed.

## Deferred

- `profile extends`
- preset structure depth beyond the current markdown-first contract
- any stronger host packaging artifact strategy beyond the checked-in root
  manifests

## Commands Run

- `./scripts/run-quality.sh`
- `git config --get core.hooksPath`
- `find .git/hooks -maxdepth 1 -type f | sort`
- `python3 scripts/check-coverage.py --repo-root . --json`
- `python3 scripts/validate-quality-artifact.py --repo-root .`
- `python3 scripts/validate-packaging.py --repo-root .`

## Recommended Next Gates

- `AUTO_CANDIDATE`: add a read-only proof that `charness update` stays clean
  against the current worktree or an ephemeral source bundle so local drift
  cannot hide behind `git clone` semantics.
- `AUTO_CANDIDATE`: add one or two traced flows that exercise
  `support_sync_lib.py`, `install_tools.py`, and release-provenance branches
  before raising the `60%` control-plane floor.
- `AUTO_CANDIDATE`: add an opt-in CI or maintainer profile that installs the
  required binaries and runs `check-supply-chain-online` with an explicit
  flaky-host policy.
- `AUTO_CANDIDATE`: exercise the `gitleaks`-installed branch in at least one
  standing environment instead of proving only the fallback path.
- `AUTO_CANDIDATE`: if evaluator depth needs model-backed variance rather than
  repo-local `run-evals`, connect the cautilus scenario runner to a maintained
  external execution surface and artifact contract.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
