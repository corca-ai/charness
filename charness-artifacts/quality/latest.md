# Quality Review
Date: 2026-05-20

## Scope

Restored `release_only` pytest marker to its documented intent: standing
quality runs now exclude release-time regression tests for `charness update`
behavior (added across April 2026 to guard the v0.3-v0.5 update bugs that
have been stable for ~30 days). Release publishes still run them via
`./scripts/run-quality.sh --release`. Net: ~70% drop in standing pytest cost
and ~80% drop in retained pytest tmp footprint, with no measurable loss in
standing safety net.

## Current Gates

- `./scripts/run-quality.sh`: 64 passed / 0 failed in 50.4s on
  `local-linux-x86_64-36cpu` (vs 158.4s prior). `pytest` itself dropped
  from 81.4s median to 22.1s.
- `release_only` pytest cases now excluded by default; `--release` flag
  (or `CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY=1`) re-includes them.
  `.agents/release-adapter.yaml` `quality_command` is now
  `./scripts/run-quality.sh --release` so release publish still covers them.
- `check-references-link-inventory` (24 files, 0 drift);
  `check-seed-fixture-budget` (total 1.88 GiB / 10.00 GiB cap on a fresh
  pytest tmp; previously 9.78 GiB across 3 retained sessions).
- `validate-usage-episodes` replays exit-zero `no_adapter`;
  `validate-attention-state-visibility` declares 48 files;
  `validate-skill-ergonomics` enforces all five configured rules;
  `validate-maintainer-setup` passes (`.githooks` wired).
- `inventory_skill_ergonomics.py`: `scope_status=scanned`,
  `finding_status=zero_heuristic_findings`, `prose_review_status=still_required`,
  `checked_skill_count=22`, `heuristic_finding_count=0`.
- `inventory_lint_ignores.py`: 38 entries with `scope=inline`, 0 `blanket=true`,
  representative `codes=[E402]`, across 26 files.
- `inventory_cli_ergonomics.py` emits `scope_classification=advisory_only_no_cli_surface`
  when no registry/archetype contract is discovered;
  `find_inline_prompt_bulk.py` emits
  `scope_classification=advisory_only_no_canonical_prompt_asset_roots`
  when no explicit `--source-glob` is supplied.
- `inventory_cli_side_effect_probes.py`: 0 findings; `inventory_dual_implementation.py`: 0 candidates.
- `check-coverage` passes at floor 85% (`coverage_fragile_margin_pp=1.0`);
  `run-evals` passes; Cautilus planner `next_action=none`,
  `must_ask_before_running=true`.
- `inventory-ci-local-gate-parity` reports no drift; no CI lane present.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 22.1s latest / 81.4s prior-median / 140.0s budget;
  `check-coverage` 41.3s / 40.3s / 45.0s leaves ~3.7s headroom;
  `check-seed-fixture-budget` 19.9s median / 60.0s budget (no longer dominated by 3-session tmp);
  `validate-inventory-consumption-declaration` 27.4s median / 35.0s budget.
- coverage gate: `check-coverage` passed in 41.3s.
- evaluator depth: `run-evals` passed; Cautilus planner declined on-demand
  eval as expected.

## Healthy

- The `release_only` marker now matches `pyproject.toml`'s documented intent;
  `--release` flag is the discoverable opt-in.
- Empty-policy classification trap is closed for `inventory_cli_ergonomics.py`
  and `find_inline_prompt_bulk.py` via explicit `scope_classification`.
- `## References` link inventory is enforced; seed-fixture footprint is
  bounded by a deterministic budget gate.

## Weak

- Non-release_only tests still consume `seeded_charness_git_repo`/`seeded_managed_home`
  (`test_validate_packaging_committed_*`, `test_charness_init_exports_managed_surface`,
  `test_doctor_cache_selection`, parts of `test_tool_lifecycle.py`); per-session
  materialization remains, only the retention multiplier and per-test commits dropped.
- `validate-inventory-consumption-declaration` latest 39.1s exceeded its
  35.0s budget on prior run (median 27.4s, no violation). Watch for drift.
- prose review result: trigger-boundary and progressive-disclosure judgment
  still requires subagent/human critique, not `heuristic_finding_count=0`.

## Missing

- No maintained Cautilus scenario-registry edit (carried).
- No CI lane; security/quality proof stays local-runner enforced.
- No content-addressed seed cache; only release_only routing was fixed this
  turn. Non-release_only seed consumers still pay per-session materialization.

## Deferred

- Downstream-repo dogfood on the stronger generated skill-ergonomics default
  before changing the rule set again (carried).
- Depth-bounded `_pytest_temp_footprint` so `check-seed-fixture-budget` can
  drop below its 60s runtime budget.

## Advisory

- Fresh-eye review evidence: bounded general-purpose subagent reviewed `inventory_standing_test_economics.py` on prior pass; this turn extends those findings by routing `release_only` per its documented marker intent.
- `validate_usage_episodes.py` evidence: `no_adapter`/`disabled` remain exit-zero with structured warning payloads.
- `check_seed_fixture_budget.py` evidence: `advisory_only_no_pytest_temp_yet` when no pytest tmp root exists.

## Delegated Review

- status: executed; reviewer: bounded general-purpose subagent on the prior
  pass; this turn's change traces directly to the user-named hypothesis that
  the April-vintage update-regression integration tests had been kept on the
  standing path beyond their useful lifetime.
- slow-gate lenses reviewed: fixture-economics (seed materialization now
  decoupled from retention multiplier), parallel-critical-path (xdist
  workers still spawn seed fixtures for non-release tests),
  duplicated-proof (release-time per-test commits removed from standing
  path).
- this turn's mutation: respect `release_only` marker in standing pytest;
  route release publish via `--release`.

## Commands Run

- `./scripts/run-quality.sh`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/check_seed_fixture_budget.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_lint_ignores.py --repo-root . --json`
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --json`

## Recommended Next Gates

- active `AUTO_CANDIDATE` because non-release_only seed consumers still pay per-session materialization: audit `test_validate_packaging_committed_*` and the non-release_only subset of `test_managed_install.py` for whether `seeded_charness_git_repo` is genuinely required, or whether mocking `subprocess.run` would let them drop the fixture entirely.
- passive `AUTO_CANDIDATE` because `check-seed-fixture-budget` still costs ~20s of `du`: replace `_pytest_temp_footprint` with a depth-bounded `du -d N` walk so the budget gate can tighten its 60s runtime budget below 5s.
- passive `AUTO_CANDIDATE` because release-time gate parity is not yet declared in the release artifact: name `./scripts/run-quality.sh --release` explicitly in the release artifact's verification checklist so future operator review does not silently lose update-flow coverage.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
