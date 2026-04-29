# Quality Review
Date: 2026-04-29

## Scope
Repo-wide quality posture for `charness`: gates, adapter policy, operator proof,
runtime signals, security, and low-noise next gates.

## Concept Risks
- Architecture remains coherent: public workflow skills, support capabilities,
  adapters, operator docs, generated exports, and durable artifacts are still
  separate.
- Fixed: the Charness quality adapter now rejects stale `gate_commands` and
  `review_commands` instead of requiring only non-empty lists.
- Remaining risk: README/operator proof layering is still weak because generated
  CLI reference proves help parity, not semantic workflow success.

## Current Gates
- `./scripts/run-quality.sh --review`: passed `48` phases, `0` failed, total
  `46.1s`; includes 515 pytest cases and 20 evals.
- Targeted post-patch proof passed: adapter validation, focused adapter tests,
  Ruff, runtime-budget check, online supply-chain audit, and Cautilus routing
  regression proof.
- `.githooks/pre-push` is active through `core.hooksPath`.

## Runtime Signals
- runtime source: `.charness/quality/runtime-signals.json` rendered by
  `check_runtime_budget.py`; profile `local-linux-aarch64-4cpu`.
- runtime hot spots: `pytest` 33.5s latest / 35.1s median, budget 70.0s;
  `check-coverage` 17.9s / 16.9s, budget 22.0s; `specdown` 6.2s / 6.2s,
  budget 8.0s; `check-duplicates` 5.6s / 5.7s, budget 8.0s;
  `check-markdown` 5.2s / 5.4s, budget 8.0s.
- coverage gate: enforced at `96.8%` with `0` files below floor.
- evaluator depth: 20 evals plus Cautilus `accept-now`.
- `check-cli-skill-surface` is also budgeted at 8.0s after repeated 5s-class samples.

## Standing Test Economics
- Pytest passed `515` tests in `32.75s`; phase time was `33.4s`.
- Test-production ratio is `0.23` (`19087/82166` Python lines), below `1.00`.

## Coverage and Eval Depth
- Coverage: `96.8%` (`1187/1226`), with `2` files in the warn band.
- Weakest tracked files: `doctor.py` `90.7%`, `support_sync_lib.py` `92.8%`,
  `upstream_release_lib.py` `95.3%`.
- `run-evals` passed `20` scenarios; Cautilus proof passed `accept-now`.

## Maintainer-Local Enforcement
- `validate_maintainer_setup.py` passed and confirmed `.githooks` is active.
- The final local gate is checked in through `.githooks/pre-push`; no no-hook
  waiver is in effect.
- `doctor.py --json --skip-release-probe` reports validation/runtime tools healthy.

## Enforcement Triage
- `AUTO_EXISTING`: full quality gate, maintainer hook validation, adapter
  validation, exact quality gate/review command validation, current-pointer
  freshness, command docs, CLI probes, coverage floor, test ratio, secrets,
  supply-chain, ruff, pytest, specdown, evals, duplicates, startup probes,
  runtime budgets, markdown links.
- `AUTO_CANDIDATE`: README/operator proof ledger; command-docs ownership split
  between README first-touch claims and generated CLI-reference parity.
- `NON_AUTOMATABLE`: broad skill and entrypoint ergonomics pressure until the
  repo defines low-noise structural invariants.

## Healthy
- Delegated `adapter/gate-design`, `operator-proof-layering`, and
  `gate-economics/security` reviews executed.
- CLI help, doctor readiness, command docs, hooks, current pointers, artifact
  validation, budgets, coverage floor, and security scans have executable proof.
- CLI ergonomics, lint-ignore, dual-implementation, brittle source-guard, and
  public-spec source-guard inventories are clean.

## Weak
- `README.md` remains `long_entrypoint`; `docs/operator-acceptance.md` remains
  `long_entrypoint`.
- Command-docs checks pooled README plus generated CLI-reference content, so
  generated reference text can mask a missing README first-touch cue.
- Public skill ergonomics still flags long mature skill cores; keep this
  advisory until a structural split is obvious.

## Missing
- No README/operator proof ledger yet.
- Generated CLI reference proves help parity, not full semantic workflow
  success for every command.

## Deferred
- Do not promote online supply-chain audit into default pre-push. The checked
  online audit passed at `--audit-level=high`; broader freshness belongs in
  review or CI-only lanes unless the repo first prices the noise.
- Do not hard-gate skill/entrypoint ergonomics as taste checks.
- Do not widen specdown coverage before removing duplicated cheaper proof.

## Advisory
- Inline prompt/content bulk inventory remains advisory; `prompt_asset_roots: []`
  is not an inventory opt-out.
- Adapter-gate phrase-detector policy seams remain `NON_AUTOMATABLE`.
- Markdown preview rendered 26 targets at widths 80 and 100 through `glow`.

## Delegated Review
- status: executed.
- slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof.
- Adapter/gate design found stale command strings could pass validation; fixed.
- Operator proof layering found the README/operator proof ledger is still
  missing and command-docs pooling can mask missing first-touch cues.
- Gate economics/security found stable unbudgeted 5s-class phases; runtime
  budgets now cover them. Secrets and manifest/lockfile checks are locally
  enforced.

## Commands Run
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root .`
- `./scripts/run-quality.sh --review`
- `python3 scripts/validate_maintainer_setup.py --repo-root .`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe`
- `python3 scripts/check_coverage.py --repo-root . --json`
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --json`
- `python3 skills/public/quality/scripts/bootstrap_markdown_preview.py --repo-root . --execute`
- quality inventory scripts for CLI, docs, spec, guard, lint, adapter, skill,
  gitignore, and inline prompt/content pressure.
- `python3 scripts/check_supply_chain_online.py --repo-root . --audit-level=high --triage-owner repo-maintainers`
- focused adapter-validation pytest; targeted Ruff and adapter validation.
- `../cautilus/bin/cautilus eval test ... 20260429T232900000Z-quality-budget-command-gates`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`

## Fresh-Eye Premortem
- Misread risk: pooled command-doc checks look like README proof. Counterweight:
  keep README/operator proof ledger as the active next quality slice.
- Misread risk: runtime budgets fail on one-off spikes. Counterweight:
  budgets fail on recent medians and report latest spikes separately.
- Misread risk: stale adapter command strings stay invisible. Counterweight:
  exact command validation now owns this invariant.

## Recommended Next Gates
- active `AUTO_CANDIDATE`: create and validate the README/operator proof ledger.
- active `AUTO_CANDIDATE`: split command-docs ownership so README first-touch
  claims and generated CLI-reference parity cannot satisfy each other.
- passive `AUTO_CANDIDATE`: online supply-chain freshness, because advisory
  noise and triage ownership need a CI/review policy decision first.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
