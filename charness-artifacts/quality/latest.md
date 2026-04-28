# Quality Review
Date: 2026-04-28
## Scope
Repo-wide quality posture for `charness`: standing gates, adapter policy,
operator-facing proof, runtime signals, and low-noise automation candidates.

## Concept Risks
- The architecture still matches the claim: public workflow skills, support
  capabilities, adapters, operator docs, and durable artifacts stay separated.
- Real drift found and fixed: stale host-cache `quality` bootstrap could strip
  mature Charness adapter fields; `validate_adapters.py` now rejects that.
- Real drift found and fixed: `.agents/quality-adapter.yaml`
  `coverage_floor_policy` now matches `scripts/check_coverage.py`.
- README/install/update claims still need a proof ledger that maps each claim
  to deterministic, evaluator, HITL, or deferred operator evidence.

## Current Gates
- `./scripts/run-quality.sh --review`: passed `49` phases, `0` failed,
  total `53.4s`.
- `validate-adapters`: enforces mature Charness quality-adapter fields and
  rejects coverage-floor drift against `scripts/check_coverage.py`.
- Standing phases include command docs, CLI probes, markdown/link checks,
  secrets, supply chain, ruff, pytest, coverage, specdown, evals, duplicate
  detection, startup probes, runtime budgets, and current-pointer freshness.
- #78 gate shape landed: quiet specdown-style failures now need actionable
  failure detail, not only a verbose rerun escape hatch.
- `.githooks/pre-push` is active through `core.hooksPath` and runs sync,
  current-pointer freshness, and the quality gate.

## Runtime Signals
- Runtime profile: `local-linux-aarch64-4cpu`.
- Budget violations: none; latest spikes for `run-evals` and `specdown` still
  pass on recent medians.
- runtime hot spots: `pytest` `39.2s` latest / `32.6s` median, `check-coverage`
  `17.4s` / `16.9s`, `check-markdown` `6.5s` / `5.1s`, `specdown`
  `6.4s` / `5.8s`, `check-duplicates` `6.2s` / `5.0s`.
- coverage gate: enforced and passing at `96.8%`, with `0` files below floor.
- evaluator depth: `run-evals` passed `20` repo-local scenarios.

## Standing Test Economics
- Pytest passed `488` tests in `34.59s`; phase time was `39.1s`.
- Test-production ratio is `0.22` (`18224/81358` Python lines), below `1.00`.
- Do not widen spec/eval proof before deciding which slices belong in
  standing, CI-only, or on-demand lanes.

## Coverage and Eval Depth
- Coverage: `96.8%` (`1187/1226`), with `2` files in the `85.0-95.0%` warn band.
- Weakest tracked files: `doctor.py` `90.7%`, `support_sync_lib.py` `92.8%`,
  `upstream_release_lib.py` `95.3%`.

## Maintainer-Local Enforcement
- `validate_maintainer_setup.py` passed and confirmed `.githooks` is active.
- The final local gate is checked in through `.githooks/pre-push`; no no-hook
  waiver is in effect.
- `doctor.py --json --skip-release-probe` reports validation/runtime tools
  healthy, including `cautilus`, `gitleaks`, `glow`, `ruff`, and `specdown`.

## Enforcement Triage
- `AUTO_EXISTING`: full quality gate, maintainer hook validation,
  adapter validation, current-pointer freshness, command docs, CLI probes,
  coverage floor, test ratio, secrets, supply-chain, ruff, pytest, specdown,
  evals, duplicates, startup probes, runtime budgets, markdown links.
- `AUTO_CANDIDATE`: README/operator proof ledger; narrower freshness checks for
  ergonomics and dogfood inventories.
- `NON_AUTOMATABLE`: broad ergonomics pressure until the repo narrows it to
  portability/discoverability invariants with a clear structural response.

## Healthy
- Delegated `gate-design`, `adapter-policy`, and `operator-signal` reviews ran.
- CLI help, doctor readiness, command docs, hooks, current pointers, artifact
  validation, and runtime budgets all have executable proof.
- CLI ergonomics, lint-ignore, and dual-implementation inventories are clean.

## Weak
- `README.md` remains `long_entrypoint` with mode/option pressure;
  `docs/operator-acceptance.md` remains `long_entrypoint`.
- Public skill ergonomics still flags long cores in mature skills; keep this
  advisory until a structural split is obvious.
- `cli_skill_surface_skill_paths` is empty, so CLI/skill surface checking falls
  back to common layout discovery.
- Generic `coverage_floor_inventory.py` is not adapted to this repo; current
  coverage authority is `scripts/check_coverage.py` plus adapter drift
  validation.

## Missing
- No README/operator proof ledger yet.
- Generated CLI reference proves help parity, not full semantic workflow
  success for every command.

## Deferred
- Do not budget `check-duplicates` or `check-markdown` until another local/CI
  sample shows whether current latest costs are representative.
- Do not hard-gate skill/entrypoint ergonomics as taste checks.
- Do not widen specdown coverage before removing duplicated cheaper proof.

## Advisory
- `find_inline_prompt_bulk.py` remains advisory; `prompt_asset_roots: []` is
  not an inventory opt-out.
- `inventory_public_spec_quality.py` reports `0` source-guard rows and `0`
  affected public specs; source-guard rollups are now explicit.

## Delegated Review
- status: executed.
- Fresh-eye context: parent-delegated reviewers completed `gate-design`,
  `adapter-policy`, `operator-signal`, `fixture-economics`,
  `parallel-critical-path`, and `duplicated-proof`.
- Main outcome: enforce coverage-floor alignment, require advisory disclosure,
  add #78 quiet-failure/source-guard signals, and narrow generic Cautilus
  trigger pressure.

## Commands Run
- `./scripts/run-quality.sh --review`
- `python3 scripts/validate_maintainer_setup.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_standing_gate_verbosity.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_public_spec_quality.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260428T000000000Z-cautilus-trigger-narrowing`
- `python3 scripts/validate_quality_closeout_contract.py --repo-root .`
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- Targeted pytest, ruff, adapter validation, and quality inventory commands.

## Fresh-Eye Premortem
- Misread risk: treating host-cache bootstrap drift as legitimate adapter
  update. Counterweight: diff restored and mature-field gate added.
- Misread risk: calling generic adapter validation enough. Counterweight:
  repo-specific Charness adapter contract now fails coverage and mature-field
  drift.
- Misread risk: generic review wording makes Cautilus feel mandatory.
  Counterweight: trigger manifest and skill guidance now require evaluator intent.

## Recommended Next Gates
- active `AUTO_CANDIDATE`: create and validate the README/operator proof ledger.
- active `AUTO_CANDIDATE`: extend current-pointer freshness beyond the
  quality closeout contract into artifact-to-final-response review.
- passive `AUTO_CANDIDATE`: because another sample should confirm cost before
  budgeting `check-duplicates` and `check-markdown`.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
