# Quality Review
Date: 2026-05-20

## Scope

Landed two previous `Recommended Next Gates`: content-addressed seed cache
(`tests/seed_cache.py`) moves `charness-repo-seed`, `charness-git-repo-seed`,
and `managed-home-seed` out of `tmp_path_factory` and into
`~/.cache/charness/test-seeds/<source-hash>/` keyed on
`git rev-parse HEAD` plus tracked diff plus untracked-not-ignored digest;
xdist workers share one materialization via `filelock`. Agent-browser orphan
race fixed by replacing `agent-browser --help` with `agent-browser --version`
in `run_help_check` (the `--help` flag warmed a background daemon as a side
effect, leaving a PPID=1 orphan that broke the next run's `--doctor-check`).
`tests/conftest.py` adds a `pytest_sessionfinish` hook that runs
`agent_browser_runtime_guard.py --cleanup-orphans --execute` on the xdist
controller as a defensive backstop. `./scripts/run-quality.sh` now finishes
64/0 twice in succession with no manual cleanup between runs.

## Current Gates

- `./scripts/run-quality.sh`: 64 passed / 0 failed across two consecutive
  runs without manual orphan cleanup; pytest 22-32s on a warm seed cache,
  `check-seed-fixture-budget` 0.1-3.1s (was 20-40s median).
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
- `release_only` marker matches `pyproject.toml`'s intent; `--release` flag is the discoverable opt-in; release adapter contract documents the convention.
- `## References` link inventory enforced; seed-fixture footprint bounded.
- Seed fan-out collapsed from 18 workers × 3 seeds = 54 materializations to
  one materialization per `(HEAD, dirty-digest)` shared across workers via
  `filelock`; `~/.cache/charness/test-seeds/<hash>/` persists across sessions
  for zero-copy same-HEAD reruns.
- Agent-browser `--doctor-check` no longer leaks PPID=1 orphans because the
  helpcheck switched from `--help` (daemon-warming side effect) to
  `--version`; `pytest_sessionfinish` is the controller-side defensive
  backstop.

## Weak

- Audit of non-release_only seed consumers (`test_validate_packaging_committed_*`,
  `test_charness_init_exports_managed_surface`, `test_doctor_*`,
  `test_charness_doctor_reports_managed_surface`,
  `test_installed_cli_remembers_managed_checkout`, `test_doctor_can_write_host_state_snapshot`,
  `test_tool_doctor_cli_returns_nonzero_for_blocking_disposition`) concluded
  these test foundational `charness init/doctor/reset` and packaging-committed
  surfaces — `subprocess.run` mocks would erase the integration safety net.
  No migrations applied.
- The seed cache grows unbounded across HEAD changes (one directory per
  `(HEAD, dirty-digest)`); no eviction policy yet. Pragmatic answer: clean
  `~/.cache/charness/test-seeds/` manually or via a future LRU helper.
- prose review result: trigger-boundary and progressive-disclosure judgment
  still requires subagent/human critique, not `heuristic_finding_count=0`.

## Missing

- No maintained Cautilus scenario-registry edit (carried).
- No CI lane; quality/security proof stays local-runner enforced.

## Deferred

- Downstream-repo dogfood on the stronger generated skill-ergonomics default
  before changing the rule set again (carried).
- LRU eviction for `~/.cache/charness/test-seeds/<hash>/` (keep N most-recent
  hashes by mtime) once accumulated cache size becomes operationally
  noticeable; out of scope for the cache landing because the cache is easy
  to clean manually and same-HEAD reuse already pays back the seed cost.

## Advisory

- Fresh-eye review evidence: bounded general-purpose subagent reviewed `inventory_standing_test_economics.py` on prior pass.
- `validate_usage_episodes.py` evidence: `no_adapter`/`disabled` remain exit-zero with structured warning payloads.
- `check_seed_fixture_budget.py` evidence: `advisory_only_no_pytest_temp_yet` when no pytest tmp root exists.

## Delegated Review

- status: executed; reviewer: bounded general-purpose subagent on this turn
  reviewed the seed-cache helper, refactored fixtures, `pytest_sessionfinish`
  hook, and the `run_help_check` `--help`→`--version` swap. Verdict: no
  blockers; deferred follow-ups recorded in `Weak`/`Deferred`. Critique
  artifact: `2026-05-20-seed-cache-orphan-teardown-critique.md`.
- slow-gate lenses reviewed: fixture-economics (seed fan-out collapsed),
  parallel-critical-path (xdist workers now share one materialization),
  duplicated-proof (release-time per-test commits already removed; no new
  duplicated coverage introduced this turn).
- this turn's mutation: `tests/seed_cache.py`, fixture refactor,
  `pytest_sessionfinish` cleanup hook, `run_help_check` daemon-leak fix.

## Commands Run

- `./scripts/run-quality.sh` (twice consecutively)
- `python3 scripts/run_slice_closeout.py --repo-root .`
- `python3 scripts/check_changed_surfaces.py --repo-root .`

## Recommended Next Gates

- passive `AUTO_CANDIDATE` because downstream skill-ergonomics dogfood has not yet been collected: queue downstream issues before changing the default rule set again.
- passive `AUTO_CANDIDATE` because `~/.cache/charness/test-seeds/<hash>/` grows unboundedly across HEAD changes: add an LRU eviction helper (keep N most-recent hashes by mtime) when accumulated cache size becomes operationally noticeable.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
