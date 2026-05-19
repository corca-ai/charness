# Quality Review
Date: 2026-05-20

## Scope

Repo-wide posture refresh on a clean tree. Inventory dispatch across skills,
CLI, standing-gate verbosity, standing-test economics, lint ignores, prompt
bulk, runtime, and attention-state visibility. No mutations; focus is on
what the green gate hides — standing-test fixture footprint and two empty-
scope inventories that should not read as enforcement.

## Current Gates

- `./scripts/run-quality.sh`: 62 passed / 0 failed in 96.0s on
  `local-linux-x86_64-36cpu` (one more gate than the prior review).
- `validate-usage-episodes` replays exit-zero `no_adapter`;
  `validate-attention-state-visibility` declares 45 files;
  `validate-skill-ergonomics` enforces all five configured rules;
  `validate-maintainer-setup` passes (`.githooks` wired).
- `inventory_skill_ergonomics.py`: `scope_status=scanned`,
  `finding_status=zero_heuristic_findings`, `prose_review_status=still_required`,
  `checked_skill_count=22`, `heuristic_finding_count=0`.
- `inventory_standing_gate_verbosity.py`: verbose escape hatch present;
  pytest/specdown failure-detail markers actionable.
- `inventory_cli_side_effect_probes.py`: 0 findings; mutating `uninstall`,
  `tool install`, `tool update`, `tool sync-support` all probed.
- `inventory_dual_implementation.py`: 0 cross-language duplicate candidates.
- `inventory_lint_ignores.py`: 38 entries with `scope=inline`, 0 `blanket=true`,
  representative `codes=[E402]`, across 26 files.
- `check-coverage` passes at floor 85% (`coverage_fragile_margin_pp=1.0`);
  `run-evals` passes; Cautilus planner `next_action=none`,
  `must_ask_before_running=true`.
- `inventory-ci-local-gate-parity` reports no drift; no CI lane present, so
  quality/security proof is local-runner enforced.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 54.2s latest / 72.7s median / 140.0s budget;
  `check-coverage` 41.3s / 40.4s / 45.0s leaves ~4.6s headroom;
  `validate-inventory-consumption-declaration` 34.1s / 24.9s / 35.0s.
- coverage gate: `check-coverage` passed in 41.3s.
- evaluator depth: `run-evals` passed; Cautilus planner declined on-demand
  eval as expected.

## Healthy

- Attention-state visibility declared for 45 files; skipped/advisory states
  cannot regress silently behind exit zero.
- Skill ergonomics scope semantics are explicit; default rule list covers
  all five supported rules.
- Mutating CLI commands all carry side-effect probes; no parity drift.

## Weak

- Standing-test economics from `inventory_standing_test_economics.py`:
  `test_file_count=167`, `nested_cli_file_count=67` (the 10 in
  `nested_cli_files` was the truncated head, not the count), and
  `pytest_temp_footprint = 7,772,123,136` bytes (~7.24 GiB) across 3 retained
  sessions; three duplicated seed roots (`charness-repo-seed`,
  `charness-git-repo-seed`, `managed-home-seed`) contribute ~4.3 GiB. The
  inventory's `recommended_action` is to reduce duplicated repo/home fixture
  materialization before changing retention or disabling xdist.
- `inventory_cli_ergonomics.py` returns `status=unconfigured` (no
  command-registry.json / command-archetypes.json discovered);
  `find_inline_prompt_bulk.py` runs against `prompt_asset_roots=[]` with
  current hits inside `tests/` previews. Per the empty-policy lesson both
  need explicit advisory-only classification rather than reading as enforced.
- prose review result: trigger-boundary and progressive-disclosure judgment
  for public skills still requires subagent/human critique, not the
  ergonomics script's `heuristic_finding_count=0`.

## Missing

- No maintained Cautilus scenario-registry edit (carried).
- No CI lane; security/quality proof stays local-runner enforced.
- No deterministic gate yet for the seed-fixture footprint budget.

## Deferred

- Future low-noise `## References` link-inventory check (carried).
- Downstream-repo dogfood on the stronger generated skill-ergonomics default
  before changing the rule set again (carried).

## Advisory

- Bounded fresh-eye general-purpose subagent reviewed `inventory_standing_test_economics.py` and the empty-scope inventories; three actionable items landed in the artifact.
- `validate_usage_episodes.py` evidence: `no_adapter`/`disabled` remain exit-zero with structured warning payloads.

## Delegated Review

- status: executed; reviewer: bounded general-purpose subagent, read-only.
- slow-gate lenses reviewed: fixture-economics (seed-root duplication and
  ~7.24 GiB pytest tmp), parallel-critical-path (xdist worker startup with
  nested-CLI fanout), duplicated-proof (overlapping repo/home/managed-home
  seed materialization across sessions).
- actionable findings landed: corrected `nested_cli_file_count` reading
  10 → 67; named the seed-fixture dedup Recommended Next Gate with the
  7.24 GiB number; classified the two empty-scope inventories per the
  empty-policy lesson.

## Commands Run

- `python3 scripts/validate_maintainer_setup.py --repo-root .`
- `python3 scripts/doctor.py --json`
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `./scripts/run-quality.sh`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_lint_ignores.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root .`
- `python3 skills/public/quality/references/find_inline_prompt_bulk.py --repo-root . --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: introduce a session-scoped shared fixture for the
  three seed roots with a per-seed materialization budget, bounding the
  ~7.24 GiB retained pytest tmp before raising xdist workers or changing
  retention.
- passive `AUTO_CANDIDATE` because empty-scope is not yet declared advisory-only: classify `inventory_cli_ergonomics.py` and `find_inline_prompt_bulk.py` explicitly as advisory-only in their JSON envelopes when scope is empty/unconfigured.
- passive `AUTO_CANDIDATE` because no `## References` drift has surfaced yet: keep the low-noise link-inventory check on the queue.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
