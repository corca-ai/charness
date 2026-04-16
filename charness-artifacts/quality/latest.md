# Quality Review
Date: 2026-04-16

## Scope

Repo-wide quality posture for the current `charness` tree, with emphasis on
turning existing standing-gate failures and nearby advisory pressure into
maintainable structural fixes rather than one-off bypasses.

## Current Gates

- `.agents/quality-adapter.yaml` records gate, review, preflight, security,
  runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` is the canonical local quality gate; `--review`
  replays PASS logs and enables online declared-link validation.
- `check-coverage` enforces both the `60.0%` aggregate control-plane floor and
  an `85.0%` per-file floor for every tracked control-plane file.
- `check-test-production-ratio` enforces a Python test/source ratio ceiling of
  `1.00` using source-of-truth Python files, excluding generated plugin exports.
- `check-python-lengths` and `check-duplicates --fail-on-match` now matter
  operationally: this slice had to satisfy them through seam extraction and
  wrapper reduction, not through threshold changes.
- `specdown run -quiet -no-report` remains part of the quiet quality gate.
- `inventory-quality-handoff` remains advisory and reports missing HITL handoff
  fields for `NON_AUTOMATABLE` recommendations.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.

## Runtime Signals

- Latest local review gate after this slice: `38 passed, 0 failed`, total
  `49.1s`.
- runtime hot spots: `pytest` `29.6s`, `check-coverage` `11.2s`,
  `specdown` `7.8s`, `check-secrets` `3.2s`, `run-evals` `2.4s`.
- coverage gate: enforced and passing at aggregate `60.0%` plus per-file
  `85.0%`; current result is `90.6%` (`1152/1272`).
- evaluator depth: `run-evals` passes 19 repo-local scenarios, so the bar is
  stronger than smoke-only review.
- Budgeted phases: `pytest` median `28.1s / 40.0s`,
  `check-coverage` median `9.9s / 15.0s`, `check-secrets` median `3.0s / 5.0s`,
  `run-evals` median `2.3s / 5.0s`, `specdown` median `7.3s / 8.0s`.
- Runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- Coverage gate: `90.6%` (`1152/1272`) against the `60.0%` aggregate floor and
  `85.0%` per-file floor.
- Test-production ratio is `0.52` (`10253/19626` Python lines), under the
  `1.00` ceiling.
- Standing pytest passes at `287 passed`; `run-evals` passes 19 repo-local
  scenarios.
- Weakest tracked files are still warn-band candidates:
  `support_sync_lib.py` `87.7%`, `upstream_release_lib.py` `87.6%`,
  `control_plane_lib.py` `88.1%`, `install_tools.py` `88.6%`.
- Specdown remains intentionally narrow and honest; the current bar is stronger
  than smoke-only but still not broad behavioral parity coverage.

## Healthy

- Standing gate failures were removed through structural simplification:
  `docs/handoff.md` was tightened below the enforced artifact limit, overlong
  skill-side helper scripts were split through repo-level helper libs, and
  duplicate `init_adapter.py` helpers were collapsed into thin wrappers.
- Thin skill-side wrappers now preserve path-loaded compatibility for
  `load_adapter` callers while keeping the actual adapter logic in repo-level
  seams that are easier to test and reuse.
- Plugin exports were resynced so the repo and shipped plugin tree now agree on
  the new helper seams.
- Lint-ignore inventory is currently clean: no blanket, file-level, or inline
  suppression debt was needed to make this slice pass.

## Weak

- Entry-point doc ergonomics remain advisory pressure, not hard failures:
  `README.md` still flags `long_entrypoint` and mode-pressure terms,
  `docs/operator-acceptance.md` still flags `long_entrypoint`,
  `AGENTS.md` and `UNINSTALL.md` still flag mode/option-pressure wording.
- Skill ergonomics remain advisory pressure in a few large public cores:
  `create-skill`, `quality`, and `spec` still flag `long_core`,
  while `create-skill`, `init-repo`, `quality`, `retro`, and `spec` still flag
  mode-pressure terms.
- Coverage warn-band files remain above the floor but are still the most honest
  next cleanup targets; more tests are not automatically the right move if the
  branches can be deleted or simplified first.

## Missing

- No automated ratchet planner exists yet for deciding when the next per-file
  coverage floor increase is honest.
- No hard gate yet exists for the current skill or entrypoint-doc ergonomics
  inventories; they still depend on maintainer judgment.

## Deferred

- Do not promote skill or entrypoint-doc ergonomics into a hard gate until the
  repo selects a narrower rule subset that reflects actual portability and
  discoverability goals rather than generic prose taste.
- Do not add a dedicated specdown adapter until multiple specs start repeating
  the same setup or extraction work.
- Do not solve warn-band coverage mechanically with more tests if the better
  next move is deletion or branch flattening in the underlying code.

## Commands Run

- focused structural validators, focused pytest around the touched seams, and
  full `./scripts/run-quality.sh --review`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: reduce complexity in `support_sync_lib.py`,
  `upstream_release_lib.py`, `control_plane_lib.py`, and `install_tools.py`
  before widening tests again; the warn band is now the sharpest deterministic
  signal.
- active `AUTO_CANDIDATE`: tighten `README.md` and
  `docs/operator-acceptance.md` so first-touch docs orient and link rather than
  carry the whole procedure inline.
- active `AUTO_CANDIDATE`: shrink long public skill cores in `create-skill`,
  `quality`, and `spec` by moving repeated rationale into references or helper
  scripts.
- passive `NON_AUTOMATABLE`: because these heuristics should stay advisory
  until a narrower, defensible rule set is chosen, decide which ergonomics
  heuristics are strong enough to graduate from advisory inventory to a real
  gate.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
