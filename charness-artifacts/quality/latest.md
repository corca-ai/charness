# Quality Review
Date: 2026-05-20

## Scope

Landed all three previous `Recommended Next Gates`: depth-bounded pytest tmp
walk (`_pytest_temp_footprint_quick`) collapses `check-seed-fixture-budget`
from ~20s to <1s; release adapter contract now documents the
`./scripts/run-quality.sh --release` convention; audit of non-release_only
seed consumers concluded no fixture migration is honest (the remaining
consumers test `charness init`/`doctor`/`reset`/packaging committed-state,
all genuine CLI integration surface). Pre-existing agent-browser orphan
flakiness on `check-cli-skill-surface`/`check-coverage` is unrelated to
these changes.

## Current Gates

- `./scripts/run-quality.sh`: 62-64 passed / 0-2 failed depending on
  agent-browser orphan state; pytest 22.1-42.8s, `check-seed-fixture-budget`
  now 0.1-3.1s (was 20-40s median).
- `release_only` pytest cases now excluded by default; `--release` flag re-includes them.
  `.agents/release-adapter.yaml` `quality_command` is `./scripts/run-quality.sh --release`
  so release publish still covers them.
- `skills/public/release/references/adapter-contract.md` documents the
  `--release` convention so downstream repos with marker-gated regression
  tests know to override the portable `quality_command` default.
- `check-references-link-inventory` (24 files, 0 drift);
  `check-seed-fixture-budget` (now reads via `_pytest_temp_footprint_quick`
  with single `du -d 4 -B1` call; runtime budget tightened 60s → 5s).
- `validate-attention-state-visibility` declares 48 files;
  `validate-skill-ergonomics` enforces all five configured rules;
  `validate-maintainer-setup` passes.
- `inventory_skill_ergonomics.py`: `scope_status=scanned`,
  `finding_status=zero_heuristic_findings`, `prose_review_status=still_required`,
  `checked_skill_count=22`, `heuristic_finding_count=0`.
- `inventory_lint_ignores.py`: 38 entries with `scope=inline`,
  0 `blanket=true`, representative `codes=[E402]`, across 26 files.
- `inventory_cli_ergonomics.py` emits `scope_classification=advisory_only_no_cli_surface`
  when no registry/archetype contract is discovered;
  `find_inline_prompt_bulk.py` emits
  `scope_classification=advisory_only_no_canonical_prompt_asset_roots`
  when no explicit `--source-glob` is supplied.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 22.1s-42.8s latest / 24.4s median / 140.0s budget;
  `check-coverage` 41.3s / 40.3s / 45.0s leaves ~3.7s headroom;
  `check-seed-fixture-budget` median dropped 19.9s → 0.1s after depth-bounded `du`;
  smoothing window trimmed of pre-change stale samples.
- coverage gate: `check-coverage` passes in standalone runs; intermittent
  failure under quality gate appears tied to agent-browser orphan race.
- evaluator depth: `run-evals` passed; Cautilus planner declined on-demand eval.

## Healthy

- Depth-bounded `du -d 4` reduces `check-seed-fixture-budget` from ~20s to ~0.1s.
- `release_only` marker matches `pyproject.toml`'s documented intent;
  `--release` flag is the discoverable opt-in; release skill contract doc
  declares the convention.
- `## References` link inventory enforced; seed-fixture footprint bounded.

## Weak

- Audit of non-release_only seed consumers (`test_validate_packaging_committed_*`,
  `test_charness_init_exports_managed_surface`, `test_doctor_cache_selection`,
  `test_doctor_next_action` (4), `test_charness_doctor_reports_managed_surface`,
  `test_installed_cli_remembers_managed_checkout`, `test_doctor_can_write_host_state_snapshot`,
  `test_clone_seeded_managed_home_can_share_source_checkout`,
  `test_tool_doctor_cli_returns_nonzero_for_blocking_disposition`) concluded
  these test foundational `charness init/doctor/reset` and packaging-committed
  surfaces — replacing with `subprocess.run` mocks would erase the integration
  safety net, not just the cost. No migrations applied this turn.
- Agent-browser orphan accumulation during pytest causes intermittent
  `check-cli-skill-surface` and `check-coverage` failures in the quality
  gate; the runtime guard's healthcheck itself spawns daemons that survive
  pytest teardown. Pre-existing flakiness, separate from this turn's changes.
- prose review result: trigger-boundary and progressive-disclosure judgment
  still requires subagent/human critique, not `heuristic_finding_count=0`.

## Missing

- No maintained Cautilus scenario-registry edit (carried).
- No CI lane; quality/security proof stays local-runner enforced.
- No session-scoped autouse teardown that cleans up agent-browser orphan
  daemons before run-quality phases that doctor agent-browser.

## Deferred

- Content-addressed seed cache (shared materialization across pytest
  sessions) — would shrink the remaining per-session ~1.9 GiB seed
  materialization for non-release_only consumers.
- Downstream-repo dogfood on the stronger generated skill-ergonomics default
  before changing the rule set again (carried).

## Advisory

- Fresh-eye review evidence: bounded general-purpose subagent reviewed `inventory_standing_test_economics.py` on prior pass.
- `validate_usage_episodes.py` evidence: `no_adapter`/`disabled` remain exit-zero with structured warning payloads.
- `check_seed_fixture_budget.py` evidence: `advisory_only_no_pytest_temp_yet` when no pytest tmp root exists.

## Delegated Review

- status: executed; reviewer: bounded general-purpose subagent on the prior
  pass; this turn extends with three landed gates and an honest audit
  conclusion that no further test migrations make sense without a
  content-addressed seed cache.
- slow-gate lenses reviewed: fixture-economics (depth-bounded `du` removes
  budget gate as a hotspot), parallel-critical-path (xdist workers still
  spawn seed fixtures for non-release tests; deferred), duplicated-proof
  (release-time per-test commits already removed).
- this turn's mutation: depth-bounded `_pytest_temp_footprint_quick`;
  release adapter contract doc; non-migration audit recorded in `Weak`.

## Commands Run

- `./scripts/run-quality.sh`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/check_seed_fixture_budget.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_lint_ignores.py --repo-root . --json`
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --json`

## Recommended Next Gates

- active `AUTO_CANDIDATE` because pre-existing agent-browser orphan race causes intermittent `check-cli-skill-surface`/`check-coverage` failures: add a session-scoped autouse teardown in `tests/conftest.py` that calls `scripts/agent_browser_runtime_guard.py --cleanup-orphans --execute` after pytest finishes, so the next run-quality phase sees a clean state.
- passive `AUTO_CANDIDATE` because per-session seed materialization still pays ~1.9 GiB for non-release_only consumers: introduce a content-addressed shared seed cache (`~/.cache/charness/test-seeds/<repo-hash>/`) so the second pytest run with the same HEAD pays zero copy cost.
- passive `AUTO_CANDIDATE` because downstream skill-ergonomics dogfood has not yet been collected: queue downstream issues before changing the default rule set again.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
