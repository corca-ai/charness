# Quality Review
Date: 2026-05-10

## Scope
Repo-wide posture pickup after the compact-AGENTS.md refactor and the
#136-#139 close batch, triggered by `/charness:setup and /quality`. Setup ran
a NORMALIZE-mode no-op (operating surfaces aligned; `Skill Routing` block
acknowledged drift in `.agents/setup-adapter.yaml`).

## Concept Risks
- `bootstrap_quality_adapter` writes semantically no-op canonicalization to
  `.agents/quality-adapter.yaml` (filling
  `public_spec_implementation_guard_min_lines: 100` equal to the default),
  tripping `validate-cautilus-proof` and violating the "no-op without
  canonical content change" invariant.
- `check-coverage` is change-gated; `scripts/doctor.py` standalone coverage
  79.8% violates the 85% per-file floor, but the pre-push lane skipped it
  this slice (no control-plane source changed).

## Current Gates
- `./scripts/run-quality.sh`: 54 passed / 0 failed across 3 runs today
  (~66-79s). The first run reported 53/54 because bootstrap had rewritten
  the quality adapter; reverting the no-op diff restored 54/54.
- `validate-cautilus-proof` clean once the adapter diff was reverted.
- `core.hooksPath = .githooks` confirmed; `.githooks/pre-push` active.

## Runtime Signals
- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by `render_runtime_summary.py`; profile `local-linux-aarch64-4cpu`.
- runtime hot spots: `pytest` 56.1s / 56.1s / 70.0s budget (prior 35.1s, ~25% headroom); `check-coverage` 33.6s / 17.9s / 22.0s (last sample 2026-05-09; today skipped); `check-duplicates` 9.2s / 9.3s / 11.0s.
- coverage gate: control-plane standalone 91.1% (1250/1372); 1 file below 85% floor (`scripts/doctor.py` 79.8%); 5 in 85-95% warn band.
- evaluator depth: 20 evals pass; Cautilus proof not re-run today (policy `ask`).
- 4 phases unbudgeted on aarch64: `check-spec-evidence-durability` (~1.5s), `inventory-ci-local-gate-parity` (~60ms), `inventory-sloc` (~150ms), `inventory-ubiquitous-language` (~1.6s).

## Standing Test Economics
- Pytest collected `844/866` (22 deselected) — up from 515 in the prior
  artifact (+64%); 139 test files; 46 nested CLI tests in
  `tests/charness_cli/**` are a duplicated-proof candidate.

## Maintainer-Local Enforcement
- `validate_maintainer_setup.py` passed; `.githooks` active. `doctor.py
  --json --skip-release-probe` reports `agent-browser 0.27.0` healthy.
  CI/local parity vacuously healthy (no `.github/workflows/*.yml`).

## Enforcement Triage
- `AUTO_EXISTING`: 54-phase quality gate covering hooks, adapter validation,
  pointer freshness, command docs, CLI probes, secrets, supply-chain
  offline, ruff/pytest/specdown/evals/duplicates, runtime budgets, markdown
  links, spec evidence durability, parity tripwire.
- `AUTO_CANDIDATE`: bootstrap no-op short-circuit; 4 unbudgeted phases;
  check-coverage standing cadence; pytest growth target.
- `NON_AUTOMATABLE`: operator-acceptance Progressive Operator Path extract;
  skill-ergonomics mode/option heuristic tightening.

## Healthy
- 54/54 quality gate after revert; cautilus-proof clean.
- Compact-AGENTS.md operator orientation honest; bounded fresh-eye review
  contract executed today (4 reviewers). Skill ergonomics `status: clean`.
- Pre-push active; supply-chain offline gate covers JS lockfile + Python.

## Weak
- `scripts/doctor.py` coverage 79.8% violates the 85% per-file floor;
  standalone `check_coverage.py` exits 1 today. Change-gated pre-push
  silences this regression (doctor.py last touched in `796491c`).
- `bootstrap_quality_adapter` writes semantically no-op canonicalization
  that trips `validate-cautilus-proof`. Reverted manually this slice.
- `pytest` 515 -> 844 in 10 days; ~25% headroom against 70s budget.
- `docs/operator-acceptance.md` (227 lines) `long_entrypoint`: Progressive
  Operator Path on lines 25-57 delays `## Remaining Items` to ~line 60.
- 4 quality phases unbudgeted on `local-linux-aarch64-4cpu`.

## Missing
- Periodic / release-time full coverage gate independent of changed paths.
- `inventory_cli_ergonomics.py` runs `unconfigured` (no
  `command-registry.json` / `command-archetypes.json`).

## Deferred
- README/operator proof ledger Cautilus claim-discovery wiring (gated on
  cautilus rework re-enable per #32).
- Online supply-chain audit promotion (passive; CI lane absent).
- `runtime_profile_default: default` synthesizes a profile not in
  `runtime_budget_profiles` (silent fall-through; reviewer-flagged latent).

## Advisory
- `validate-cautilus-proof` will trip on any future
  `.agents/quality-adapter.yaml` write until the helper short-circuit lands.
- `coverage_relevant_changes_present` (run-quality.sh:112-132) is a
  hardcoded path list — new control-plane code outside it will not enable
  check-coverage.

## Delegated Review
- status: executed.
- adapter/gate-design: bootstrap rewrite is a real defect; smallest fix at
  `scripts/quality_bootstrap_lib.py:447-466`.
- runtime/economics (slow-gate lenses: fixture-economics,
  parallel-critical-path, duplicated-proof): check-coverage 33.6s spike
  advisory; 4 unbudgeted phases real; pytest test-count growth dominant.
- security/CI parity: vacuously healthy; offline supply-chain adequate;
  pre-push active.
- skill/operator ergonomics: critique long_core leave; mode/option pressure
  flags heuristic noise; only moveable surface is operator-acceptance
  Progressive Operator Path.

## Commands Run
- `./scripts/run-quality.sh` (3 runs)
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root .` (mutated; reverted after no-op diff confirmed)
- `python3 scripts/validate_cautilus_proof.py --repo-root .` plus `plan_cautilus_proof.py --json`
- `python3 scripts/check_coverage.py --repo-root .` (standalone — exit 1, doctor.py 79.8%)
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root .` and inventory_* (skill_ergonomics, cli_ergonomics, lint_ignores, standing_test_economics, standing_gate_verbosity, public_spec_quality) `--json` runs.

## Recommended Next Gates
- active `AUTO_CANDIDATE`: fix bootstrap no-op rewrite at
  `scripts/quality_bootstrap_lib.py:447-466` — short-circuit when every diff
  is appending defaulted-equals-default fields. Helper edit is not
  prompt-affecting alone.
- active `AUTO_CANDIDATE`: surface the silent doctor.py coverage regression.
  Either remove change-gating on `check-coverage` in
  `scripts/run-quality.sh:362` or add a release-time non-conditional
  coverage invocation.
- active `AUTO_CANDIDATE`: fill 4 budgets in `.agents/quality-adapter.yaml`
  `runtime_budget_profiles.local-linux-aarch64-4cpu.budgets`
  (`check-spec-evidence-durability: 2500`, `inventory-ci-local-gate-parity: 500`,
  `inventory-sloc: 1000`, `inventory-ubiquitous-language: 3000`). Adapter
  edit is prompt-affecting (cautilus eval refresh required; policy `ask`).
- active `NON_AUTOMATABLE`: extract `docs/operator-acceptance.md:25-57`
  Progressive Operator Path into `docs/operator-progressive-path.md` with a
  2-line pointer.
- passive `AUTO_CANDIDATE` because budget headroom is still 25% (no immediate breach): pytest growth target — consolidate the 46 nested CLI test files toward in-process tests; aim median 50s.

## History
- [2026-04-30 archive](2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](2026-04-09-through-2026-04-10.md)
