# Quality Review
Date: 2026-04-17

## Scope

Repo-wide quality posture for the current `charness` tree, focused on turning standing-gate and advisory pressure into maintainable structural fixes.

## Current Gates

- `.agents/quality-adapter.yaml` records gate, review, preflight, security,
  runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` is the canonical local quality gate; `--review`
  replays PASS logs and enables online declared-link validation.
- `check-coverage` enforces both the `60.0%` aggregate control-plane floor and
  an `85.0%` per-file floor for every tracked control-plane file.
- `check-test-production-ratio` enforces a Python test/source ratio ceiling of
  `1.00`.
- `check-python-lengths` and `check-duplicates --fail-on-match` are standing
  gates, not advisory review notes.
- `specdown run -quiet -no-report` remains part of the quiet quality gate.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.

## Runtime Signals

- Latest local review gate after this slice: `38 passed, 0 failed`, total `50.3s`.
- runtime hot spots: `pytest` `30.7s`, `check-coverage` `11.3s`, `check-secrets`
  `3.6s`, `check-markdown` `4.1s`, `specdown` `2.8s`.
- coverage gate: enforced and passing at aggregate `60.0%` plus per-file
  `85.0%`; current result is `98.0%` (`1196/1221`).
- evaluator depth: `run-evals` passes 19 repo-local scenarios, so the bar is
  stronger than smoke-only review.
- Budgeted phases: `pytest` median `31.7s / 40.0s`,
  `check-coverage` median `10.7s / 15.0s`, `check-secrets` median `3.5s / 5.0s`,
  `run-evals` median `2.3s / 5.0s`, `specdown` median `2.8s / 8.0s`.
- Runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- Coverage gate: `98.0%` (`1196/1221`) against the `60.0%` aggregate floor and
  `85.0%` per-file floor; test-production ratio is `0.54`
  (`11279/20721` Python lines), and standing proof is `321 passed` plus
  19 repo-local eval scenarios.
- Every tracked control-plane file now clears the warn band. Weakest remaining
  tracked files are `doctor.py` `95.8%`, `upstream_release_lib.py` `95.3%`,
  and `update_tools.py` `98.3%`.
- Specdown remains intentionally narrow and honest; the current bar is stronger
  than smoke-only but still not broad behavioral parity coverage.

## Healthy

- Earlier standing-gate failures were removed through structural
  simplification: `docs/handoff.md` now fits the enforced artifact limit,
  helper logic moved into repo-level seams, and duplicate `init_adapter.py`
  helpers collapsed into thin wrappers.
- Thin skill-side wrappers still preserve path-loaded compatibility for
  `load_adapter` callers while keeping reusable adapter logic in repo-level
  seams.
- Public executable-spec boundaries are explicit in `spec`, and `quality` now
  inventories proof layering instead of asking only what proof is missing.
- Public spec inventory now reads actual `run:shell` blocks instead of
  misclassifying them as prose, so the quality lens matches specdown's real executable boundary.
- `README.md` was reduced into a short operator orienter while keeping the
  command-doc contract intact, so the root entrypoint doc now clears the
  length-pressure heuristic instead of acting like a second install manual.
- `specs/index.spec.md` and `specs/tool-doctor.spec.md` now prove current CLI
  contracts with direct command checks instead of delegating the whole story to pytest, and public-spec inventory is clean again.
- CLI ergonomics inventory, lint-ignore inventory, and dual-implementation
  inventory are currently clean: no flat-help registry pressure, no ignore
  debt, and no likely parity-smell candidates were detected in this tree.
- Control-plane traced coverage scenarios now include helper-contract branches
  for support sync, release probing, manifest/capability validation, and
  install helper lock-writing paths, so the coverage gate better reflects real
  maintained behavior instead of only top-level command flows.
- Remaining control-plane quality pressure is no longer coverage-floor debt; the
  standing gap moved back to documentation and skill ergonomics advisories.

## Weak

- Entry-point doc ergonomics remain advisory pressure, not hard failures.
  `README.md` no longer flags `long_entrypoint`, but it still carries
  `option_pressure_terms_present` because standing command-doc anchors require
  literal flag-bearing examples. `AGENTS.md` and `UNINSTALL.md` still flag
  mode/option-pressure wording.
- Skill ergonomics remain advisory pressure in public cores:
  `init-repo`, `retro`, and `spec` still flag mode-pressure terms, while
  `quality` itself now trips the `long_core` heuristic at `165` core lines.
- `spec` still trips the mode-pressure heuristic because a checked-in contract
  test currently requires the exact phrase `user-facing mode choice`.
- `doctor.py --json` still reports `markdown-preview` as locally `not-ready`
  because the preferred `glow` backend is missing. The standing quality gate
  still passes, but preview proof for that support runtime is degraded.

## Missing

- No automated ratchet planner exists yet for deciding when ergonomics
  inventories are narrow enough to become a hard gate.

## Deferred

- Do not promote ergonomics inventory into a hard gate until the repo narrows
  it to portability/discoverability rules instead of generic prose taste.
- Do not add a dedicated specdown adapter until multiple specs start repeating
  the same setup or extraction work.
- Fresh-eye premortem used the reference checklist only. The canonical
  subagent path was blocked because this session did not explicitly allow
  subagents.

## Commands Run
- `./scripts/run-quality.sh --review`
- quality inventories: standing-gate verbosity, entrypoint docs, skill
  ergonomics, public spec quality, CLI ergonomics, lint ignores, and dual
  implementation
- `python3 scripts/doctor.py --json`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: decide whether the remaining mode/option-pressure
  wording in `AGENTS.md`, `README.md`, `UNINSTALL.md`, `init-repo`, `retro`,
  and the contract-constrained `spec` phrase reflects real distinctions or
  should collapse into stronger defaults.
- active `AUTO_CANDIDATE`: decide whether `skills/public/quality/SKILL.md`
  should move more review prose into references or helper scripts so the core
  falls back under the `long_core` advisory threshold without losing routing
  precision.
- active `AUTO_CANDIDATE`: decide whether command-doc-required flag examples
  should stay inline, move behind owner-doc links, or gain a small inventory
  exemption so README/UNINSTALL pressure tracks real prose clutter.
- active `AUTO_CANDIDATE`: if the repo wants another deterministic ratchet
  after coverage cleanup, decide whether entrypoint-doc or skill-ergonomics
  inventories should graduate into a narrow hard gate.
- passive `AUTO_CANDIDATE`: because the repo can operate in degraded mode
  today, install `glow` or document an explicit no-`glow` posture for
  `markdown-preview` only if maintainers want preview readiness as a local bar.
- passive `NON_AUTOMATABLE`: because gate promotion still needs maintainer
  judgment, only harden ergonomics heuristics that can survive without turning
  prose review into taste policing.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
