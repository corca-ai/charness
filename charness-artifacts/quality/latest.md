# Quality Review
Date: 2026-05-12

## Scope
Repo-wide posture pickup after `66c7a72 Make Cautilus proof log-backed on
demand`, triggered by `/charness:quality` on `local-linux-x86_64-36cpu`. Tracks
whether the 2026-05-10 active recommendations actually landed.

## Concept Risks
- `runtime_profile_default: default` (`.agents/quality-adapter.yaml:112`)
  still synthesizes a profile not present in `runtime_budget_profiles`; today
  it falls through silently because the runner picks the matching host
  profile, but the field stays latent. Previous reviewer flagged this; still
  unresolved.
- Runtime-signals coverage is single-host: `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  has 20 samples for `local-linux-x86_64-36cpu` only. The
  `local-linux-aarch64-4cpu` budgets in the adapter are not backed by any
  observed sample on this checkout — they encode a guess.

## Current Gates
- `./scripts/run-quality.sh`: 55 passed / 0 failed in 55.0s wall
  (`local-linux-x86_64-36cpu`). +1 phase vs 2026-05-10 because
  `check-coverage` (36.8s) now runs every time on this host instead of being
  change-gated out.
- `validate-cautilus-proof`, `validate-current-pointer-freshness`,
  `validate-quality-closeout-contract`, `check-spec-evidence-durability`,
  `inventory-ci-local-gate-parity`, `inventory-sloc`,
  `inventory-ubiquitous-language` all pass.
- `core.hooksPath = .githooks` active; pre-push runs `run-quality.sh
  --read-only`; pre-commit fans out staged-file validators.

## Runtime Signals
- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source --> rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu` (20 recent samples per phase).
- runtime hot spots: `pytest` 44.9s latest / 38.7s median, budget 140s (~32% used, ~68% headroom); `check-coverage` 36.9s latest / 36.0s median, budget 45s (~82% used, brittle margin pp = 1.0); `check-duplicates` 5.3s / 5.3s, budget 11s; `specdown` 3.6s / 3.5s, budget 10.5s; `check-markdown` 3.3s / 3.3s, budget 11s.
- coverage gate: standalone `check_coverage.py` exits 0; control-plane 90.4% (1398/1547), 0 files below 85% floor, 6 in 85-95% warn band.
- evaluator depth: 20 evals pass via `run-evals` (2.1s); Cautilus proof not re-run today (now log-backed on demand per `66c7a72`).
- runtime visibility: configured on x86_64. **Missing signals**: zero samples on `local-linux-aarch64-4cpu`; the aarch64 budgets in the adapter are unbacked observations.
- 2 phases unbudgeted on `local-linux-x86_64-36cpu`: `check-spec-evidence-durability` (370ms), `inventory-ci-local-gate-parity` (55ms). Prior artifact listed 4 unbudgeted on aarch64 — `inventory-sloc: 1000` and `inventory-ubiquitous-language: 1000` were added to x86_64 only; aarch64 profile still has all 4 missing.

## Standing Test Economics
- Pytest collected 144 test files (up from 139, +3.6%). 50 nested CLI process-spawning files (up from 46) under `tests/charness_cli/**` and `tests/quality_gates/**` — the duplicated-proof and per-file-startup-cost candidate continues to grow.
- Pytest budget on `local-linux-x86_64-36cpu` is 140s (raised from 70s in prior adapter snapshot); 32% used today. Aarch64 budget stayed at 70s without an aarch64 sample to justify it.
- Standing-gate verbosity: pytest `-q`, healthy. No orchestrator chatter regression.

## Coverage and Eval Depth
- Control-plane coverage 90.4% (1398/1547 executable lines), **0 files below 85% floor** (was 1 at 79.8%). 6 files in 85-95% warn band. The doctor.py regression flagged 2026-05-10 is resolved (now 95.4%).
- `check-coverage` now runs every quality pass on this host; the prior change-gating concern is moot here, but the underlying `coverage_relevant_changes_present` allowlist (`scripts/run-quality.sh:112-132`) remains a hardcoded path list that can still silence new control-plane code added outside it.
- evaluator depth: 20 evals pass (`run-evals` 2.1s). Cautilus proof not re-run today; `66c7a72` made Cautilus proof log-backed on demand, so deterministic gates own closeout unless a failing prompt/log triggers a fresh run.

## Maintainer-Local Enforcement
- `validate_maintainer_setup.py` passed; `.githooks/pre-commit` + `.githooks/pre-push` active.
- Pre-push owns: plugin export sync drift, pointer freshness, full read-only quality gate, and an artifact-mutation tripwire after the read-only run.
- Pre-commit owns: staged-file `py_compile`/`ruff`, plus path-targeted validators (`skills/`, `profiles/`, `.agents/`, `presets/`, `integrations/`, `*.md`).
- `doctor.py --json --skip-release-probe` reports `agent-browser 0.9.2` healthy (different host than 2026-05-10's `0.27.0` reading — version constraint is `advisory`, not a regression signal alone).

## CI/Local Gate Parity
- `.github/` does not exist on this checkout. `inventory_ci_local_gate_parity.py` reports `workflows_scanned: 0`, `parity_issues: []`. The validator's `healthy` reading is technically correct but masks the structural posture: **all security and contract enforcement lives in `.githooks` on a single maintainer machine**. A clone with `core.hooksPath` unset bypasses everything, including `check-secrets` and supply-chain.
- This is the same "vacuously healthy" finding the prior artifact carried; calling it Weak (not Healthy) is the honest read.

## Enforcement Triage
- `AUTO_EXISTING`: the 55-phase quality gate (validate-skills/skill-ergonomics/surfaces/public-skill-validation/public-skill-dogfood/cautilus-scenarios/cautilus-proof/profiles/presets/adapters/integrations/packaging/packaging-committed/handoff-artifact/debug-artifact/debug-seam-index/retro-lesson-index/quality-artifact/quality-closeout-contract/critique-artifacts/current-pointer-freshness/maintainer-setup, plus check-cli-skill-surface/python-lengths/python-filenames/python-runtime-inheritance/skill-contracts/export-safe-imports/plugin-import-smoke/command-docs/doc-links/spec-evidence-durability/title-slug-drift/markdown/secrets/supply-chain/github-actions/shell/links-internal/links-external/py-compile/ruff/pytest/coverage/test-completeness/test-production-ratio/specdown/run-evals/duplicates/ci-local-gate-parity/measure-startup-probes/sloc/ubiquitous-language/runtime-budget, plus inventory-quality-handoff).
- `AUTO_CANDIDATE`: aarch64 runtime signal capture; 2 remaining unbudgeted phases on x86_64 (`check-spec-evidence-durability`, `inventory-ci-local-gate-parity`); all 4 unbudgeted on aarch64; `coverage_relevant_changes_present` hardcoded allowlist; `runtime_profile_default: default` synthesized name.
- `NON_AUTOMATABLE`: `docs/operator-acceptance.md` Progressive Operator Path extract; `critique` SKILL.md core trim; CI lane creation policy (single-machine enforcement risk).

## Healthy
- 55/55 quality gate, 55.0s wall. Prior 2026-05-10 active recommendations 1 (bootstrap no-op short-circuit at `scripts/quality_bootstrap_lib.py:435-461`) and 2 (`doctor.py` coverage regression — now 95.4%) landed.
- Coverage 90.4% with 0 files below the 85% floor.
- Lint suppressions: 20 inline noqa, 0 blanket. Narrow E402/BLE001 only; `inventory_lint_ignores.py` shows no accumulation pressure.
- CLI side-effect probes clean (7 mutating commands probed, no findings).
- Skill ergonomics overall `status: clean`; only `critique` carries `long_core`.

## Weak
- **`critique` SKILL.md is 199 raw / 170 non-empty lines vs `max_core_lines: 160`** (the inventory reported `core_nonempty_lines: 166`; fresh-eye `wc -l` confirms 199 raw / 170 non-empty). The top 57 lines are anchor/contract; Target Selection (line 59+) is the moveable surface.
- CI/local parity is vacuously healthy because no CI exists at all. Security-bearing phases (`check-secrets`, `check-supply-chain`, validator scripts) have no second enforcement lane.
- `docs/operator-acceptance.md` (227 lines) still has Progressive Operator Path on lines 25-57; `## Remaining Items` does not appear until ~line 60. Prior recommendation 4 unresolved.
- Pytest test-file growth: 144 (+3.6% in 2 days) and nested-CLI fanout 50 (+8.7%). Budget headroom is wide, but the maintenance-cost trend is the signal, not the wall time.
- `check-coverage` is at 82% of budget (36.9s / 45s; brittle margin 1.0pp) — closer to its budget than any other standing phase.

## Missing
- Aarch64 runtime samples in `.charness/quality/runtime-signals.json` <!-- reproduction-source -->; the aarch64 budgets are unobserved guesses (fresh-eye catch).
- 2 unbudgeted phases on `local-linux-x86_64-36cpu` (`check-spec-evidence-durability`, `inventory-ci-local-gate-parity`); all 4 unbudgeted on `local-linux-aarch64-4cpu`.
- `inventory_cli_ergonomics.py` still runs `unconfigured` (no `command-registry.json` / `command-archetypes.json`).
- Periodic / release-time full coverage gate independent of changed-path allowlist.
- Any CI lane at all.

## Deferred
- README/operator proof ledger Cautilus claim-discovery wiring (gated on Cautilus rework re-enable per corca-ai/cautilus#32; the new log-backed-on-demand model means deterministic gates own closeout until a failing log appears).
- Online supply-chain audit promotion (passive; no CI lane to host it).
- Doctor-host `agent-browser 0.9.2` vs 2026-05-10's `0.27.0` — different host, version is `advisory`; revisit only if a per-host minimum constraint becomes warranted.

## Advisory
- `coverage_relevant_changes_present` (`scripts/run-quality.sh:112-132`) is a hardcoded path list — new control-plane code outside it will not enable change-gated `check-coverage`. Today's standing run sidesteps this because the gate runs unconditionally, but a future change-gated cadence inherits the same blind spot.
- `runtime_profile_default: default` synthesizes a name absent from `runtime_budget_profiles`. Reader-flagged latent 2026-05-10; still latent.
- 20 narrow `noqa` suppressions are all E402 (legacy `sys.path` shims in `plugins/charness/scripts/**` and `skills/**` re-export shims) or single BLE001. No accumulation pressure, but `validate_packaging_install_surface`-style re-export shims keep producing new E402 callsites; promoting the `skill_iter` shared helper (handoff item 5 sub-bullet) would shrink the surface organically.

## Delegated Review
- status: executed.
- adapter / gate design: confirmed `_diff_is_defaulted_only` (`scripts/quality_bootstrap_lib.py:435-442`) handles the safe direction — any field disappearing from `rendered` re-triggers a write; benign whitespace diffs over-write but never under-write. Confirmed `runtime_budget_profiles.local-linux-aarch64-4cpu` (`.agents/quality-adapter.yaml:124-134`) still has only 7 budgets; `check-spec-evidence-durability` and `inventory-ci-local-gate-parity` absent from both profiles.
- runtime / economics (slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof): aarch64 pytest budget (70000ms) is unbacked by any aarch64 runtime sample on this checkout — the apparent 56.1s figures in the prior artifact were aarch64-labeled but the current signals file holds only x86_64 data. Real risk: 50 process-spawning CLI tests on 4 cpu likely exceed 70s; duplicated-proof candidate (nested CLI fanout 50 files) and parallel-critical-path (xdist `-n auto`) are the natural next moves before raising the budget. fixture-economics: pytest fixture setup is not yet a hot spot but worth tracking after consolidation.
- security / CI parity: `.github/` absent; pre-push owns `check-secrets`, `check-supply-chain`, and validator suite — single-machine enforcement is the real posture.
- skill / operator ergonomics: `critique` SKILL.md is 199 raw lines (not 166); the gap vs threshold is +39 raw / +10 non-empty, not +6. Target Selection from line 59 onward is the moveable surface; the top 57 lines are load-bearing anchor/contract. `docs/operator-acceptance.md` extract recommendation remains valid.

## Commands Run
- `python3 scripts/validate_maintainer_setup.py --repo-root .`
- `python3 scripts/doctor.py --json --skip-release-probe`
- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root .` (no-op, status `unchanged`)
- `python3 skills/public/quality/scripts/resolve_quality_artifact.py --repo-root . --intent current`
- `./scripts/run-quality.sh` (single run, 55/55 in 55.0s)
- `python3 scripts/check_coverage.py --repo-root .` (standalone — exit 0, 90.4%)
- `python3 scripts/check_supply_chain.py --repo-root .`
- `./scripts/check-secrets.sh`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_cli_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_gate_verbosity.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_lint_ignores.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_public_spec_quality.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_dual_implementation.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_cli_side_effect_probes.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_entrypoint_docs_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_ci_local_gate_parity.py --repo-root . --json`

## Recommended Next Gates
- active `AUTO_CANDIDATE`: capture aarch64 runtime samples before trusting the `local-linux-aarch64-4cpu.budgets` entries — run `record_quality_runtime.py` on the aarch64 maintainer machine and commit the merged `.charness/quality/runtime-signals.json` <!-- reproduction-source -->. Then prune or correct any budget that the actual sample contradicts (start with pytest 70000 ms vs ~56s claim).
- active `AUTO_CANDIDATE`: fill the 2 remaining unbudgeted phases on `local-linux-x86_64-36cpu` (`check-spec-evidence-durability: 2500`, `inventory-ci-local-gate-parity: 500`) in `.agents/quality-adapter.yaml`. Adapter edit is prompt-affecting; with `66c7a72` Cautilus proof is log-backed on demand, so a deterministic re-run of `validate-cautilus-proof` covers closeout absent a failing log.
- active `NON_AUTOMATABLE`: extract `docs/operator-acceptance.md:25-57` Progressive Operator Path to `docs/operator-progressive-path.md` with a 2-line pointer. Same recommendation as 2026-05-10; still warranted.
- active `NON_AUTOMATABLE`: trim `skills/public/critique/SKILL.md` Target Selection (line 59 onward) to a reference. The top 57 lines are anchor/contract; the residual is the moveable surface. Aim ≤ 170 non-empty / `max_core_lines: 160`.
- passive `AUTO_CANDIDATE` because budget headroom (68%) is wide: pytest growth and nested-CLI fanout. 144 test files / 50 nested-CLI files is +3.6%/+8.7% in 2 days. The move is consolidation pressure, not budget; revisit when headroom drops below 30% or nested-CLI count crosses 60.
- passive `AUTO_CANDIDATE`: minimal CI lane that mirrors pre-push for clones without `core.hooksPath` (security-bearing phases at minimum: `check-secrets`, `check-supply-chain`, ruff, py-compile). Deferred only because no `.github/` exists today; promoting this to `active` waits on a maintainer-policy decision about whether charness wants any CI lane at all.

## History
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
