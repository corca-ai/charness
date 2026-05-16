# Quality Review
Date: 2026-05-16

## Scope
Repo-wide quality/setup run after the gather acquisition critique work and the
operator request to run `quality` plus `setup` and reflect findings into the
repo. Scope includes operating-surface normalization, adapter bootstrap
posture, plugin export integrity, standing gates, and the quality defects found
while running those gates.

## Current Gates
- `./scripts/run-quality.sh`: 60 passed / 0 failed in 80.8s on
  `local-linux-x86_64-36cpu`.
- First run failed on five real signals and all were repaired: agent-browser
  orphan runtime state, `quality_bootstrap_lib.py` length, plugin import smoke
  for `web-fetch`, managed-doctor onboarding expectation drift, and coverage
  cascading from pytest failure.
- `setup` inspection now reports `repo_mode: NORMALIZE`, no missing core
  surfaces, `AGENTS.md` / `CLAUDE.md` normalized, and `Skill Routing` matching
  the compact block.
- `quality` bootstrap now reports `mutation_testing: preserved`; the helper no
  longer drops the Cosmic Ray adapter block when refreshing defaults.

## Runtime Signals
- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py` via `scripts/record_quality_runtime.py`;
  profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 57.4s latest / 29.1s median, budget 140.0s;
  `check-coverage` 41.2s latest / 36.8s median, budget 45.0s;
  `validate-inventory-consumption-declaration` 16.0s latest / 10.4s median,
  budget 35.0s; `check-duplicates` 6.7s latest / 6.1s median, budget 11.0s.
- coverage gate: `check-coverage` passed in 41.2s; no coverage failure remains
  after the managed-doctor expectation update.
- evaluator depth: `run-evals` passed in 2.2s; no Cautilus run was triggered
  because there was no log-backed prompt regression.

## Healthy
- Full quality closeout is green: validators, packaging, plugin import smoke,
  docs, markdown, secrets, supply-chain, ruff, py-compile, pytest, coverage,
  specdown, evals, and runtime budget all passed.
- Setup normalization is green after adding the compact `Skill Routing` block
  to `AGENTS.md`; `CLAUDE.md` remains a symlink to `AGENTS.md`.
- The first-run doctor failure was machine state, not repo logic:
  `agent_browser_runtime_guard.py --cleanup-orphans --execute` removed the
  orphan daemon tree and doctor returned exit 0 afterward.
- Plugin export integrity is restored: `sync_root_plugin_manifests.py` ran and
  `check_plugin_import_smoke.py` imported every plugin Python file.

## Weak
- `defuddle` and `gws-cli` are missing on this machine. Doctor classifies both
  as non-blocking missing/advisory for the current repo, but public gather
  fallback dogfood will remain weaker until `defuddle` is installed.
- Lint ignore pressure rose to 34 narrow inline `noqa` entries, including the
  new `web-fetch` import-path shim in source and plugin export. Inventory still
  reports 0 blanket and 0 file-level ignores.
- Standing test economics remains a maintenance signal: after excluding ignored
  `mutants/`, the inventory reports 153 real test files and 58 nested CLI
  process-spawning files.
- `check-coverage` is close to its local budget at 41.2s / 45.0s.

## Missing
- There is still no CI lane in this checkout; security-bearing checks are local
  hook / maintainer-machine enforced.
- `defuddle` local runtime is not installed, so the new reader fallback is only
  covered by deterministic command-shape tests here.
- No aarch64 runtime sample was collected in this run.

## Deferred
- Full repair of the gather acquisition stack remains governed by
  `charness-artifacts/critique/2026-05-16-gather-acquisition-repair-plan-critique.md`.
  This quality/setup run did not implement that next slice.
- Raw acquired-content persistence for gather remains deferred until the repair
  contract chooses acquisition maximization versus trace/proof correctness.
- No-site-name / generic-helper lint from the insane-search review remains a
  follow-up, not part of this quality/setup normalization.

## Advisory
- `mutants/` is gitignored but can still distort ad hoc inventories; the
  standing-test economics inventory now excludes it by command-backed change in
  `standing_test_economics_lib.py`.
- `quality` bootstrap previously dropped unknown explicit fields from its
  rendered adapter output; the concrete observed casualty was
  `.agents/quality-adapter.yaml` `mutation_testing`. The helper now preserves
  that validated block.
- The `web-fetch` script uses a narrow `E402` shim so exported plugin modules
  can import sibling helper scripts when loaded by path; this is validated by
  `check_plugin_import_smoke.py`.
- Public-skill scenario review used `suggest_public_skill_dogfood.py` for
  `quality`; the existing slow-gate consumer prompt still routes to `quality`
  and needs no new maintained Cautilus scenario for this setup/quality slice.

## Delegated Review
- status: blocked.
- host signal: active Codex tool contract limits `spawn_agent` use to tasks
  where the current user message asks for subagent work. This quality/setup run
  therefore records deterministic gates and inventories only; fresh-eye review
  remains unprobed for this slice.

## Commands Run
- `python3 skills/public/setup/scripts/inspect_repo.py --repo-root .`
- `python3 skills/public/setup/scripts/render_skill_routing.py --repo-root . --json`
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
- `python3 scripts/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `pytest -q tests/quality_gates/test_standing_test_economics.py tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_quality_mutation_testing.py tests/charness_cli/test_managed_install.py::test_charness_doctor_reports_managed_surface tests/test_web_fetch_support.py`
- `ruff check scripts/quality_bootstrap_lib.py scripts/quality_bootstrap_common.py tests/quality_gates/test_quality_bootstrap.py skills/support/web-fetch/scripts/acquire_public_url.py tests/charness_cli/test_managed_install.py skills/public/quality/scripts/standing_test_economics_lib.py tests/quality_gates/test_standing_test_economics.py`
- `python3 scripts/check_plugin_import_smoke.py --repo-root .`
- `./scripts/run-quality.sh`

## Recommended Next Gates
- active `AUTO_CANDIDATE`: install or expose `defuddle` locally, then dogfood a
  public article URL through the gather/web-fetch repair path once that repair
  contract lands.
- active `AUTO_CANDIDATE`: keep `mutation_testing` in the quality bootstrap
  preservation test whenever the adapter renderer grows new explicit blocks.
- passive `AUTO_CANDIDATE` because current quality is green: add a minimal CI
  lane mirroring security-bearing local hooks when maintainer policy allows CI.
- passive `AUTO_CANDIDATE` because budget still passes: track `check-coverage`
  budget pressure before raising the 45s budget.

## History
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
