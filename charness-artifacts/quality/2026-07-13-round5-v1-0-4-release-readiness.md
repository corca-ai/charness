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
- Custom-home Claude proof: public doctor/init/reset two-home tests passed and
  every Claude plugin subprocess now crosses the same selected-home seam.
- Security baseline: secret scan and supply-chain checks passed.
- Frozen-bundle standing broad pytest passed under the verification lock in
  94.92s; the release gate then passed in 72.297s.
- v1.0.4 public content and installed source/cache/host state were confirmed by
  a bounded observer through unauthenticated REST and local doctor readback.

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
- The reproduced custom-home leak now has observation plus both mutation
  directions covered; unrelated process-home `.claude` creation is a sentinel.
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

- None for v1.0.4 acceptance. The locked bundle, semver/release critique,
  substantive public readback, installed doctor/cache proof, and distinct
  observer are bound to checked-in closeout evidence.

## Deferred

- Revisit release-only managed-install fixture economics only with same-command
  before/after evidence and at least one retained real install/update smoke.
- Do not broaden catalog root validation to list/resolve, permission matrices,
  symlink matrices, or Git-checkout requirements without operator evidence.
- Real Claude custom-home execution remains an explicit nonclaim; evaluate a
  safe root-CLI host-proof trigger separately rather than expanding this patch.

## Advisory

- structural review result: command: `inventory_structural_waste.py`, `inventory_cli_ergonomics.py`, and `inventory_brittle_source_guards.py` found no broad-scanner, duplicate-discovery, repeated-read, CLI-ergonomics, or brittle-guard candidate.
- prose review result: command: `inventory_skill_ergonomics.py --summary` required prose judgment; trigger boundaries, progressive disclosure, helper ownership, dogfood pressure, and target-vs-ambient split were inspected, and the 16 host-reference findings are intentional adapter/host boundaries rather than current defects.
- test-economics inventory: command: focused standing/release pytest timing measured managed-install 3 tests/0.61s, release-only 14 tests/78.78s, and standing nested-CLI cluster 44 tests/3.77s; no speedup claim is admitted.

## Delegated Review

- Delegated Review: executed — bounded speed and structure scouts independently measured test economics and structural/CLI surfaces; code critique then used two distinct angles and a separate counterweight, all read-only with zero fingerprint drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): re-delegated for fixture economics and nested-process boundaries; parallelism and proof deletion were rejected because the measured cases exercise distinct stateful delivery boundaries.
- Post-release review: the first bounded quality pass correctly returned HOLD
  because durable artifacts lagged the already-passing release proof. Its public
  and installed evidence requests are checked in; the final bounded re-review
  passed with zero fingerprint drift before the goal flipped complete.

## Commands Run

- `./scripts/run-quality.sh --read-only`
- `./scripts/check-secrets.sh`; `python3 scripts/check_supply_chain.py --repo-root .`
- `python3 scripts/check_test_production_ratio.py --repo-root .` (advisory 1.03).
- structural, CLI-ergonomics, brittle-guard, skill-ergonomics, and test-economics inventories recorded in the active goal.
- `pytest -q tests/test_capability_catalog.py tests/charness_cli/test_codex_cache_refresh.py --durations=10`
- focused custom-home public doctor/init/reset pytest (3 passed in 6.57s).
- focused ruff, plugin parity, debug/critique validators, and reviewer fingerprints.
- `run_slice_closeout.py --base v1.0.3 --verification-lock
  --produce-mutation-coverage` (standing broad pytest passed in 94.92s).
- repo release helper dry-run and execute; release quality passed in 72.297s,
  fresh-checkout probes passed, public HTTPS returned 200, and install refresh
  completed in 8.757s.
- bounded observer read remote refs, unauthenticated GitHub REST content, and
  installed doctor/cache state; evidence is durable in
  `charness-artifacts/probe/2026-07-13-v1.0.4-independent-release-observer.json`.

## Recommended Next Quality Moves

- active preserve agreement among quality, goal, retro, and handoff whenever
  post-release evidence changes —
  capability_needed=durable closeout truth; next_center=post-release memory;
  transformation=verified release to reconstructable next-session state;
  proof_boundary=checked-in observer plus disposition review;
  enforcement_posture=existing goal/artifact gates. North-star: prevent a
  correct release from leaving a wrong durable answer. Floor-addition restraint:
  use the existing closeout contract; add no broad gate.
- passive revisit release-only managed-install economics only after a same-command retained-boundary experiment because distinct real install/update states currently justify the cost — capability_needed=test economics; next_center=release-only fixture setup; transformation=repeated setup to proven cheaper shared setup; proof_boundary=before/after command plus retained process smoke; enforcement_posture=no-gate because no safe delta is yet demonstrated.

## History

- [pytest suite test-value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
