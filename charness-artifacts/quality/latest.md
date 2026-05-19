# Quality Review
Date: 2026-05-20

## Scope

Repo-wide posture refresh with the active and both passive `Recommended Next
Gates` from the prior pass implemented in the same turn: a per-seed/total
pytest tmp budget gate (`check-seed-fixture-budget`), a `## References`
link-inventory gate (`check-references-link-inventory`), and explicit
advisory-only classification in `inventory_cli_ergonomics.py` and
`find_inline_prompt_bulk.py` when their scope is empty.

## Current Gates

- `./scripts/run-quality.sh`: 64 passed / 0 failed in 158.4s on
  `local-linux-x86_64-36cpu` (two new gates added this turn).
- New gates: `check-references-link-inventory` (24 files inspected, 0 drift);
  `check-seed-fixture-budget` (total 9.78 GiB observed / 10.00 GiB cap,
  per-seed cap 3.00 GiB, no breaches yet).
- `validate-usage-episodes` replays exit-zero `no_adapter`;
  `validate-attention-state-visibility` declares 48 files (45 → 48 after the
  three new advisory-only declarations);
  `validate-skill-ergonomics` enforces all five configured rules;
  `validate-maintainer-setup` passes (`.githooks` wired).
- `inventory_skill_ergonomics.py`: `scope_status=scanned`,
  `finding_status=zero_heuristic_findings`, `prose_review_status=still_required`,
  `checked_skill_count=22`, `heuristic_finding_count=0`.
- `inventory_cli_ergonomics.py` now emits `scope_classification=advisory_only_no_cli_surface`
  when no registry/archetype contract is discovered;
  `find_inline_prompt_bulk.py` emits `scope_classification=advisory_only_no_canonical_prompt_asset_roots`
  when no explicit `--source-glob` is supplied.
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
- runtime hot spots: `pytest` 111.5s latest / 81.4s median / 140.0s budget;
  `check-coverage` 41.3s / 40.3s / 45.0s leaves ~3.7s headroom;
  `check-seed-fixture-budget` 38.6s / 19.9s / 60.0s (new, dominated by
  pytest-tmp `du`);
  `validate-inventory-consumption-declaration` 39.1s / 27.4s / 35.0s
  (latest above budget; median still under).
- coverage gate: `check-coverage` passed in 41.3s.
- evaluator depth: `run-evals` passed; Cautilus planner declined on-demand
  eval as expected.

## Healthy

- The empty-policy classification trap is now closed for two more inventories:
  `inventory_cli_ergonomics.py` and `find_inline_prompt_bulk.py` carry an
  explicit `scope_classification` so a green run cannot be read as
  enforcement.
- `## References` link inventory is now enforced by
  `scripts/check_references_link_inventory.py`; one drift case
  (`docs/conventions/surface-driven-adapter-triggers.md`) was already
  link-shaped under the new continuation-aware scanner.
- Seed-fixture pytest-tmp footprint is now under a deterministic budget
  (total ≤10 GiB, per-seed ≤3 GiB); current 9.78 GiB places the gate
  near the ceiling, so future drift will fail visibly.

## Weak

- Seed-fixture footprint is close to ceiling: `check-seed-fixture-budget`
  reports total 9.78 GiB against a 10.00 GiB budget; the underlying
  duplicated seed materialization across pytest sessions is unchanged. The
  gate now exposes regression but does not yet shrink the footprint.
- `validate-inventory-consumption-declaration` latest 39.1s exceeded its
  35.0s budget once this run (median still 27.4s, no violation). Watch for
  drift before relaxing.
- prose review result: trigger-boundary and progressive-disclosure judgment
  for public skills still requires subagent/human critique, not the
  ergonomics script's `heuristic_finding_count=0`.

## Missing

- No maintained Cautilus scenario-registry edit (carried).
- No CI lane; security/quality proof stays local-runner enforced.
- No content-addressed seed cache yet — the budget gate names the cost but
  does not collapse the three duplicated seed roots into one shared
  materialization.

## Deferred

- Downstream-repo dogfood on the stronger generated skill-ergonomics default
  before changing the rule set again (carried).
- A faster `_pytest_temp_footprint` (e.g., depth-bounded `du`) so
  `check-seed-fixture-budget` does not have to use a 60s runtime budget.

## Advisory

- Bounded fresh-eye general-purpose subagent reviewed `inventory_standing_test_economics.py` and the empty-scope inventories on the prior pass; this turn implemented all three follow-on gates from that artifact.
- `validate_usage_episodes.py` evidence: `no_adapter`/`disabled` remain exit-zero with structured warning payloads.
- `check_seed_fixture_budget.py` reports `advisory_only_no_pytest_temp_yet` when no pytest tmp root exists; declared under `attention-state-visibility.json`.

## Delegated Review

- status: executed; reviewer: bounded general-purpose subagent, read-only on the prior pass; artifact this turn extends those findings with implemented gates rather than re-running review.
- slow-gate lenses still in scope: fixture-economics (still the dominant
  cost; budget gate now bounds it), parallel-critical-path (xdist worker
  startup unchanged), duplicated-proof (seed materialization not yet
  deduplicated).
- this turn's mutation: implemented the active and both passive
  Recommended Next Gates from the 2026-05-19 artifact and bounded their
  runtime via adapter budgets.

## Commands Run

- `./scripts/run-quality.sh`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate_attention_state_visibility.py --repo-root . --json`
- `python3 scripts/check_references_link_inventory.py --repo-root .`
- `python3 scripts/check_seed_fixture_budget.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_lint_ignores.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_cli_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/references/find_inline_prompt_bulk.py --repo-root . --json`
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --json`

## Recommended Next Gates

- active `AUTO_CANDIDATE` because the budget gate exposes regression but does not shrink the footprint: introduce a content-addressed seed cache (one materialization shared across sessions) for `charness-repo-seed`, `charness-git-repo-seed`, and `managed-home-seed`.
- passive `AUTO_CANDIDATE` because `check-seed-fixture-budget` currently relies on a coarse `du` walk that costs ~20–40s: replace `_pytest_temp_footprint` with a depth-bounded scan so the budget gate can tighten its runtime budget below 60s.
- passive `AUTO_CANDIDATE` because downstream skill-ergonomics dogfood has not yet been collected: queue downstream issues before changing the default rule set again.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
