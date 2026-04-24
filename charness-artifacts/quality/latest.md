# Quality Review
Date: 2026-04-24

## Scope

Repo-wide quality posture for the current `charness` tree, focused on turning standing-gate and advisory pressure into maintainable structural fixes.

## Current Gates

- `.agents/quality-adapter.yaml` records gate, review, preflight, security,
  runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` is the canonical local quality gate; `--review`
  replays PASS logs and enables online declared-link validation.
- `check-coverage` enforces the `60.0%` aggregate and `85.0%` per-file floors
  for every tracked control-plane file.
- `check-test-production-ratio` enforces a Python test/source ratio ceiling of
  `1.00`.
- `check-python-lengths` and `check-duplicates --fail-on-match` are standing
  gates, not advisory review notes.
- `validate-current-pointer-freshness` rejects known-stale current-pointer claims.
- `validate-debug-seam-index` and `validate-retro-lesson-index` keep derived
  memory indexes current.
- Runtime EWMA is advisory in `.charness/quality/runtime-smoothing.json`;
  enforcement still uses raw latest samples, medians, and spikes.
- `specdown run -quiet -no-report` remains part of the quiet quality gate.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.

## Runtime Signals

- Latest local quality gate after this slice: `45 passed, 0 failed`, total
  `49.4s`.
- runtime hot spots: latest recorded samples have `pytest` `37.1s`, `check-coverage`
  `11.7s`, `check-markdown` `4.1s`, `check-duplicates` `2.8s`, and `specdown` `2.9s`.
- coverage gate: enforced and passing at aggregate `60.0%` plus per-file
  `85.0%`; current result is `97.9%` (`1186/1211`).
- evaluator depth: `run-evals` passes 20 repo-local scenarios, so the bar is
  stronger than smoke-only review.
- Budgeted phases: `pytest` median `41.2s / 45.0s`,
  `check-coverage` median `11.9s / 15.0s`, `check-secrets` median
  `2.2s / 6.0s`, `run-evals` median `2.1s / 5.0s`, `specdown` median
  `2.7s / 8.0s`.
## Coverage and Eval Depth

- Coverage gate: `97.9%` (`1186/1211`) against the configured floors;
  test-production ratio is `0.19` (`14560/77051` Python lines), and standing
  proof is the latest full pytest gate plus 20 repo-local eval scenarios.
- Every tracked control-plane file now clears the warn band. Weakest remaining
  tracked files are `doctor.py` `95.8%`, `upstream_release_lib.py` `95.3%`,
  and `update_tools.py` `98.3%`.
- Specdown remains intentionally narrow and honest; the current bar is stronger
  than smoke-only but still not broad behavioral parity coverage.

## Healthy

- CLI ergonomics, lint-ignore, and dual-implementation inventories are clean:
  no flat-help pressure, ignore debt, or likely parity-smell candidates were detected.
- Online external-link review caught a stale Cautilus install URL; the repo now
  points integration manifests, release checklist guidance, plugin export, and
  tests at the live upstream `install.sh` URL.
- Cautilus instruction-surface proof initially rejected the slice because
  validation-shaped closeout routed directly to `hitl`; checked-in AGENTS
  routing now makes `quality` before HITL explicit, and the refreshed proof is
  `4 passed / 0 failed / 0 blocked`.

## Weak

- Entry-point doc ergonomics remain advisory pressure, not hard failures.
  `AGENTS.md`, `README.md`, `docs/development.md`, and
  `docs/operator-acceptance.md` still flag `long_entrypoint`; `README.md` also
  still carries `option_pressure_terms_present`.
- Skill ergonomics remain advisory pressure in public cores:
  `create-cli`, `gather`, `init-repo`, `retro`, and `spec` still flag
  mode-pressure terms, while `quality` and `spec` both trip `long_core`.
- `markdown-preview` is now wired through checked-in config, repo-owned install
  guidance, and a local `glow` runtime. Remaining quality work is no longer
  backend availability; it is deciding which workflow should invoke rendered
  preview by default instead of leaving the seam as an opt-in helper.
- Rolling current-pointer artifacts now have freshness ratchets for stale
  validator-existence, runtime, budget, and release target-version claims.
- Public spec quality inventory still reports `duplicate_public_spec_examples`
  because it sees `.artifacts/cautilus-experiments/...` copies alongside
  checked-in `specs/`; treat that as inventory-scope pressure before promoting
  it to a hard public-spec layering failure.

## Missing

- No broad freshness check yet cross-validates ergonomics or dogfood claims
  against their owning live inventories.

## Deferred

- Do not promote ergonomics inventory into a hard gate until the repo narrows
  it to portability/discoverability rules instead of generic prose taste.
- Do not add a dedicated specdown adapter until multiple specs start repeating
  the same setup or extraction work.
- Do not describe the canonical fresh-eye path as blocked without a bounded
  capability probe and a concrete host signal; if the host still cannot spawn
  subagents, stop and leave the host-side contract gap visible.

## Advisory

- Current advisory findings are present from ergonomics, public-spec scope, and
  dogfood freshness inventories; they remain `NON_AUTOMATABLE` or
  `AUTO_CANDIDATE` until a low-noise structural response is clear.

## Delegated Review

- status: executed; bounded subagent review ran for the quality advisory
  omission retro and issue #64 spec planning, and future blocked states must
  include `host signal:` or `tool signal:` evidence.

## Commands Run
- `./scripts/run-quality.sh` and `./scripts/run-quality.sh --review`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/check_coverage.py --repo-root .` and `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root .`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: decide whether `skills/public/quality/SKILL.md`
  should move more review prose into references or helper scripts so the core
  falls back under the `long_core` advisory threshold without losing routing
  precision.
- active `AUTO_CANDIDATE`: keep expanding `validate-current-pointer-freshness`;
  runtime EWMA, hot-spot, and budget-median claims are now checked, but
  ergonomics/dogfood claims still need inventory-backed checks.
- active `AUTO_CANDIDATE`: decide which workflow should call the now-bootstrapped
  markdown-preview seam by default (`narrative`, `announcement`, `quality`, or
  a command surface) instead of leaving it as a helper that only exists on paper.
- active `AUTO_CANDIDATE`: narrow public-spec inventory scope so generated
  `.artifacts/cautilus-experiments` copies do not look like duplicate checked-in
  public spec examples unless the repo intentionally wants artifact previews in
  that advisory lens.
- passive `NON_AUTOMATABLE`: because gate promotion still needs maintainer
  judgment, only harden ergonomics heuristics that can survive without turning
  prose review into taste policing.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
