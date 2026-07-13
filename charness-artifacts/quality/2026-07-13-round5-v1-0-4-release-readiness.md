# Quality Review
Date: 2026-07-13
Title: Round 5 v1.0.4 Release Readiness

## Scope

Target boundary: repo-wide patch-release readiness, with focused judgment on
current operator defects, test economics, generated surfaces, security, and
deterministic gate health.

Ambient repo findings: the release-only managed-install suite remains expensive;
no current structural, CLI-ergonomics, brittle-guard, secret, or supply-chain
failure was found.

## Current Gates

- Read-only broad quality baseline: 81/81 phases passed.
- Focused catalog proof: 21 tests passed; ruff and source/plugin parity passed.
- Security baseline: secret scan and supply-chain checks passed.
- Final verification-lock and release proof remain pending until the bundle is frozen.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; read-only profile measured in this run. <!-- reproduction-source -->
- runtime hot spots: full release latest/median 71.8s/74.4s; read-only 56.7s/60.9s; pytest 36.9s/51.6s, all within configured budgets.
- coverage gate: `./scripts/run-quality.sh --read-only` passed 81/81 in 59.6s.
- evaluator depth: deterministic-gates-only because Cautilus is ask-before-run and was outside this authorization.

## Healthy

- Generated plugin ownership and synchronization are explicit; the catalog
  backend mirror is byte-identical after the change.
- The reproduced invalid-root writer defect now has backend, direct CLI,
  in-process public handler, and actual public-process regression proof.
- Current secret, supply-chain, structural-waste, CLI-ergonomics, and brittle
  source-guard inventories produced no actionable failure.

## Weak

- Release-only managed-install proof costs 78.78s for 14 tests; the cases cross
  distinct install/update boundaries, so cost alone does not justify flattening them.
- Skill-ergonomics inventory reported 16 host-reference heuristics, but prose
  inspection classified them as intentional host-boundary references rather
  than trigger, path, or progressive-disclosure defects.
- Test-to-production Python line ratio is 1.03 against the advisory 1.00
  reference. The new 0.37s process regression earns its boundary; the ratio is
  test-value pressure, not evidence that this regression should be deleted.

## Missing

- Final locked-bundle proof, semver/release critique, public release readback,
  installed-version doctor/cache proof, and distinct-observer confirmation.

## Deferred

- Revisit release-only managed-install fixture economics only with same-command
  before/after evidence and at least one retained real install/update smoke.
- Do not broaden catalog root validation to list/resolve, permission matrices,
  symlink matrices, or Git-checkout requirements without operator evidence.

## Advisory

- structural review result: command: `inventory_structural_waste.py`, `inventory_cli_ergonomics.py`, and `inventory_brittle_source_guards.py` found no broad-scanner, duplicate-discovery, repeated-read, CLI-ergonomics, or brittle-guard candidate.
- prose review result: command: `inventory_skill_ergonomics.py --summary` required prose judgment; trigger boundaries, progressive disclosure, helper ownership, dogfood pressure, and target-vs-ambient split were inspected, and the 16 host-reference findings are intentional adapter/host boundaries rather than current defects.
- test-economics inventory: command: focused standing/release pytest timing measured managed-install 3 tests/0.61s, release-only 14 tests/78.78s, and standing nested-CLI cluster 44 tests/3.77s; no speedup claim is admitted.

## Delegated Review

- Delegated Review: executed — bounded speed and structure scouts independently measured test economics and structural/CLI surfaces; code critique then used two distinct angles and a separate counterweight, all read-only with zero fingerprint drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): re-delegated for fixture economics and nested-process boundaries; parallelism and proof deletion were rejected because the measured cases exercise distinct stateful delivery boundaries.

## Commands Run

- `./scripts/run-quality.sh --read-only`
- `./scripts/check-secrets.sh`; `python3 scripts/check_supply_chain.py --repo-root .`
- `python3 scripts/check_test_production_ratio.py --repo-root .` (advisory 1.03).
- structural, CLI-ergonomics, brittle-guard, skill-ergonomics, and test-economics inventories recorded in the active goal.
- `pytest -q tests/test_capability_catalog.py tests/charness_cli/test_codex_cache_refresh.py --durations=10`
- focused ruff, plugin parity, debug/critique validators, and reviewer fingerprints.

## Recommended Next Quality Moves

- active freeze and publish the catalog invalid-root repair only after final lock — capability_needed=release confidence; next_center=operator no-write safety; transformation=focused verified slice to patch bundle; proof_boundary=verification-lock plus distinct public observer; enforcement_posture=existing gates. North-star: prevent a wrong result escaping at publication. Floor-addition restraint: reuse focused regression and release gates; add no broad gate.
- passive revisit release-only managed-install economics only after a same-command retained-boundary experiment because distinct real install/update states currently justify the cost — capability_needed=test economics; next_center=release-only fixture setup; transformation=repeated setup to proven cheaper shared setup; proof_boundary=before/after command plus retained process smoke; enforcement_posture=no-gate because no safe delta is yet demonstrated.

## History

- [pytest suite test-value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
