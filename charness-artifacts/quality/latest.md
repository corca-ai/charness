# Quality Review
Date: 2026-04-17

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
  fields for `NON_AUTOMATABLE` recommendations when the artifact omits them.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.

## Runtime Signals

- Latest local review gate after this slice: `38 passed, 0 failed`, total
  `48.2s`.
- runtime hot spots: `pytest` `31.8s`, `check-coverage` `10.9s`,
  `specdown` `7.8s`, `check-markdown` `3.8s`, `check-secrets` `3.2s`.
- coverage gate: enforced and passing at aggregate `60.0%` plus per-file
  `85.0%`; current result is `98.0%` (`1196/1221`).
- evaluator depth: `run-evals` passes 19 repo-local scenarios, so the bar is
  stronger than smoke-only review.
- Budgeted phases: `pytest` median `30.4s / 40.0s`,
  `check-coverage` median `10.7s / 15.0s`, `check-secrets` median `3.3s / 5.0s`,
  `run-evals` median `2.5s / 5.0s`, `specdown` median `7.8s / 8.0s`.
- Runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- Coverage gate: `98.0%` (`1196/1221`) against the `60.0%` aggregate floor and
  `85.0%` per-file floor.
- Test-production ratio is `0.54` (`10749/19905` Python lines), under the
  `1.00` ceiling.
- Standing pytest passes at `302 passed`; `run-evals` passes 19 repo-local
  scenarios.
- Every tracked control-plane file now clears the warn band. Weakest remaining
  tracked files are `doctor.py` `95.8%`, `upstream_release_lib.py` `95.3%`,
  and `update_tools.py` `98.3%`.
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
- `README.md` was reduced into a short operator orienter while keeping the
  command-doc contract intact, so the root entrypoint doc now clears the
  length-pressure heuristic instead of acting like a second install manual.
- `docs/capability-resolution.md` and `docs/control-plane.md` now carry thin
  command-surface anchors, which keeps ownership closer to the actual seam.
- Control-plane traced coverage scenarios now include helper-contract branches
  for support sync, release probing, manifest/capability validation, and
  install helper lock-writing paths, so the coverage gate better reflects real
  maintained behavior instead of only top-level command flows.
- Remaining control-plane quality pressure is no longer coverage-floor debt; the
  standing gap moved back to documentation and skill ergonomics advisories.
- Lint-ignore inventory is currently clean: no blanket, file-level, or inline
  suppression debt was needed to make this slice pass.

## Weak

- Entry-point doc ergonomics remain advisory pressure, not hard failures.
  `README.md` no longer flags `long_entrypoint`, but it still carries
  `option_pressure_terms_present` because standing command-doc anchors require
  literal flag-bearing examples. `AGENTS.md` and `UNINSTALL.md` still flag
  mode/option-pressure wording.
- Skill ergonomics remain advisory pressure in two public cores:
  `init-repo`, `retro`, and `spec` still flag mode-pressure terms.
- The recent cleanup pass removed `docs/operator-acceptance.md`, README length
  pressure, `create-skill`, and `quality` from the advisory list, so remaining
  ergonomics pressure is now concentrated in a smaller set of docs/skills.
  `spec` still trips the mode-pressure heuristic because a checked-in contract
  test currently requires the exact phrase `user-facing mode choice`.

## Missing

- No automated ratchet planner exists yet for deciding when the next per-file
  coverage floor increase is honest, and ergonomics inventories are still advisory.

## Deferred

- Do not promote ergonomics inventory into a hard gate until the repo narrows
  it to portability/discoverability rules instead of generic prose taste.
- Do not add a dedicated specdown adapter until multiple specs start repeating
  the same setup or extraction work.

## Commands Run
- `python3 scripts/check-command-docs.py --repo-root .`,
  `python3 scripts/check-doc-links.py --repo-root .`,
  `./scripts/check-markdown.sh`, `python3 scripts/sync_root_plugin_manifests.py --repo-root .`,
  and full `./scripts/run-quality.sh --review`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: decide whether the remaining mode/option-pressure
  wording in `AGENTS.md`, `README.md`, `UNINSTALL.md`, `init-repo`, `retro`,
  and the contract-constrained `spec` phrase reflects real distinctions or
  should collapse into stronger defaults.
- active `AUTO_CANDIDATE`: decide whether command-doc-required flag examples in
  first-touch docs should stay inline, move behind owner-doc links, or gain a
  small inventory exemption so README/UNINSTALL pressure tracks real prose clutter.
- active `AUTO_CANDIDATE`: if the repo wants another deterministic ratchet
  after coverage cleanup, decide whether entrypoint-doc or skill-ergonomics
  inventories should graduate into a narrow hard gate.
- passive `NON_AUTOMATABLE`: keep this passive because gate promotion still
  needs maintainer judgment on which heuristics are defensible. HITL handoff:
  `target=entrypoint-doc and skill-ergonomics heuristics`,
  `review_question=which heuristics are strong enough to become a hard gate
  without turning prose review into taste policing`,
  `decision_needed=select promotable heuristics vs keep inventory-only posture`,
  `must_not_auto_decide=true`,
  `observation_point=after one more cleanup pass on remaining mode-pressure docs/skills and command-anchor tension`,
  `revisit_cadence=after meaningful quality cleanup slices`,
  `automation_candidate=promote only the narrowed rule subset that survives maintainer review`.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
