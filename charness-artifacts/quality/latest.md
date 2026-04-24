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
- `run-quality.sh` now detects `pytest-xdist` by capturing help output before
  matching it, avoiding the prior pipefail false negative from
  `pytest --help | grep`.
- `check-runtime-budget` now emits top-N runtime hot spots, including
  unbudgeted phases.

## Runtime Signals

- Latest local quality gate after this slice: `48 passed, 0 failed`, total
  `59.0s`.
- runtime hot spots: latest recorded samples have `pytest` `41.9s`,
  `check-coverage` `14.4s`, `check-markdown` `4.9s`,
  `check-cli-skill-surface` `4.8s`, and `specdown` `3.3s`.
- Fixture economics moved broad managed-install/update lifecycle checks to
  `ci_only`; standing pytest still keeps representative install coverage and
  the full on-demand slice remains green.
- CLI/skill surface probes now run `doctor.py --skip-release-probe` so standing
  readiness checks do not spend wall time on upstream release freshness.
- `pytest` and `check-coverage` now run in the same quality-runner phase, and
  `check-coverage` uses support-sync fixtures instead of fetching upstream
  support archives during standing coverage proof.
- coverage gate: enforced and passing at aggregate `60.0%` plus per-file
  `85.0%`; current result is `96.8%` (`1187/1226`).
- evaluator depth: `run-evals` passes 20 repo-local scenarios, so the bar is
  stronger than smoke-only review.
- Budgeted phases: `pytest` median `41.9s / 70.0s`,
  `check-coverage` median `12.8s / 15.0s`, `check-secrets` median
  `2.3s / 6.0s`, `run-evals` median `2.3s / 5.0s`, `specdown` median
  `2.9s / 8.0s`.
## Coverage and Eval Depth

- Coverage gate: `96.8%` (`1187/1226`) against the configured floors;
  test-production ratio is `0.19` (`14560/77051` Python lines), and standing
  proof is the latest full pytest gate plus 20 repo-local eval scenarios.
- Every tracked control-plane file clears the enforced floor. Weakest remaining
  tracked files are `doctor.py` `90.7%`, `support_sync_lib.py` `92.8%`,
  and `upstream_release_lib.py` `95.3%`.
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

- status: executed; bounded subagent review ran `gate-design`,
  `adapter-policy`, and `operator-signal` lenses for this runtime investigation.
  Future blocked states must include `host signal:` or `tool signal:` evidence.

## Commands Run
- `./scripts/run-quality.sh`; targeted pytest/coverage timing; Cautilus proof;
  surface closeout for packaging, docs, markdown, secrets, integrations, ruff,
  support/update dry-runs, and runtime budgets.

## Recommended Next Gates

- active `AUTO_CANDIDATE`: keep expanding `validate-current-pointer-freshness`
  for ergonomics and dogfood claims, and keep broad install/update coverage in
  on-demand or CI slices unless a cheaper standing fixture proves the contract.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
