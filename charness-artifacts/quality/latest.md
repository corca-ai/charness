# Quality Review
Date: 2026-04-28
## Scope
Repo-wide quality posture for `charness`: standing gates, adapter policy,
operator-facing proof, runtime signals, and low-noise automation candidates.

## Concept Risks
- The architecture still matches the claim: public workflow skills, support
  capabilities, adapters, operator docs, and durable artifacts stay separated.
- Real drift found and fixed: stale host-cache `quality` bootstrap can strip
  mature Charness adapter fields while defaults keep generic validation green.
  `validate_adapters.py` now rejects that for `repo: charness`.
- README/install/update claims still need a proof ledger that maps each claim
  to deterministic, evaluator, HITL, or deferred operator evidence.

## Current Gates
- `./scripts/run-quality.sh --review`: passed `47` phases, `0` failed,
  total `75.0s`.
- `validate-adapters`: now enforces explicit mature quality-adapter fields for
  Charness: product surfaces, CLI probes/docs, canonical markdown surfaces,
  runtime profile/budgets, startup probes, and gate/review/security commands.
- Standing phases include command docs, CLI probes, markdown/link checks,
  secrets, supply chain, ruff, pytest, coverage, specdown, evals, duplicate
  detection, startup probes, runtime budgets, and current-pointer freshness.
- `.githooks/pre-push` is active through `core.hooksPath` and runs sync,
  current-pointer freshness, and the quality gate.

## Runtime Signals
- Runtime profile: `local-linux-aarch64-4cpu`.
- Budget violations: none.
- Latest spikes: `run-evals` `6.5s` latest against `5.0s` budget; `specdown`
  `9.4s` latest against `8.0s` budget. Medians still pass.
- runtime hot spots: `pytest` `57.5s` latest / `32.4s` median, `check-coverage`
  `17.9s` / `16.5s`, `check-markdown` `9.8s` / `5.1s`, `specdown`
  `9.4s` / `5.8s`, `check-duplicates` `9.0s` / `5.0s`.
- coverage gate: enforced and passing at `96.8%`, with `0` files below floor.
- evaluator depth: `run-evals` passed `20` repo-local scenarios.

## Standing Test Economics
- Pytest passed `481` tests in `52.99s`; phase time was `57.4s`.
- Test-production ratio is `0.22` (`17902/81233` Python lines), below the
  `1.00` ceiling.
- Do not widen spec/eval proof before deciding which slices belong in
  standing, CI-only, or on-demand lanes.

## Coverage and Eval Depth
- Coverage: `96.8%` (`1187/1226`), with `2` files in the `85.0-95.0%` warn band.
- Weakest tracked files: `doctor.py` `90.7%`, `support_sync_lib.py` `92.8%`,
  `upstream_release_lib.py` `95.3%`.
- Rendered Markdown proof ran with `glow`: `52` previews for `26` docs/spec
  surfaces at widths `80` and `100`.

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
- `AUTO_CANDIDATE`: README/operator proof ledger; align adapter
  `coverage_floor_policy` with `check_coverage.py`; narrower freshness checks
  for ergonomics and dogfood inventories.
- `NON_AUTOMATABLE`: broad ergonomics pressure until the repo narrows it to
  portability/discoverability invariants with a clear structural response.

## Healthy
- Delegated `gate-design`, `adapter-policy`, and `operator-signal` reviews ran.
- CLI help, doctor readiness, command-doc generation, hooks, current pointers,
  artifact validation, and runtime budgets all have executable proof.
- CLI ergonomics, lint-ignore, and dual-implementation inventories are clean.

## Weak
- `README.md` remains `long_entrypoint` with mode/option pressure;
  `docs/operator-acceptance.md` remains `long_entrypoint`.
- Public skill ergonomics still flags long cores in mature skills; keep this
  advisory until a structural split is obvious.
- `cli_skill_surface_skill_paths` is empty, so CLI/skill surface checking falls
  back to common layout discovery.
- Generic `coverage_floor_inventory.py` is not adapted to this repo; current
  coverage authority is `scripts/check_coverage.py`.
- Public spec inventory still sees duplicate examples under local
  `.artifacts/cautilus-experiments/...`; treat as inventory scope pressure.

## Missing
- No README/operator proof ledger yet.
- Generated CLI reference proves help parity and required strings, not full
  semantic workflow success for every command.

## Deferred
- Do not budget `check-duplicates` or `check-markdown` until another local/CI
  sample shows whether current latest costs are representative.
- Do not hard-gate skill/entrypoint ergonomics as taste checks.
- Do not widen specdown coverage before removing duplicated cheaper proof.

## Advisory
- Inline prompt/content bulk inventory mostly found docstrings, fixtures, test
  payloads, and generated/local experiment copies; adapter policy currently
  opts out with `prompt_asset_roots: []`.
- `coverage_floor_policy` is more generic than the actual coverage gate; align
  the adapter declaration or make `check_coverage.py` consume it.

## Delegated Review
- status: executed.
- Fresh-eye context: parent-delegated reviewers completed `gate-design`,
  `adapter-policy`, `operator-signal`, `fixture-economics`,
  `parallel-critical-path`, and `duplicated-proof`.
- Main outcome: implement explicit mature quality-adapter field enforcement.

## Commands Run
- `./scripts/run-quality.sh --review`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe`
- `python3 scripts/validate_maintainer_setup.py --repo-root .`
- `python3 scripts/check_coverage.py --repo-root .`
- `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root . --json`
- `python3 skills/public/quality/scripts/bootstrap_markdown_preview.py --repo-root . --execute`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- Targeted pytest, ruff, adapter validation, and quality inventory commands.

## Fresh-Eye Premortem
- Misread risk: treating host-cache bootstrap drift as legitimate adapter
  update. Counterweight: diff restored and mature-field gate added.
- Misread risk: calling generic adapter validation enough. Counterweight:
  repo-specific Charness adapter contract now fails the exact drift class.
- Misread risk: turning ergonomics pressure into taste policing. Counterweight:
  kept it advisory until structural action is clear.

## Recommended Next Gates
- active `AUTO_CANDIDATE`: create and validate the README/operator proof ledger.
- active `AUTO_CANDIDATE`: align adapter `coverage_floor_policy` with
  `check_coverage.py` or make the coverage gate consume the adapter policy.
- passive `AUTO_CANDIDATE`: because one more sample should confirm representative
  cost before budgeting `check-duplicates` and `check-markdown`.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
