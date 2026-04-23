# Quality Review
Date: 2026-04-23

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
- `validate-current-pointer-freshness` rejects known-stale claims in this
  quality pointer and `docs/handoff.md`.
- Runtime EWMA is advisory in `.charness/quality/runtime-smoothing.json`;
  enforcement still uses raw latest samples, medians, and spikes.
- `specdown run -quiet -no-report` remains part of the quiet quality gate.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.

## Runtime Signals

- Latest local quality gate after this slice: `43 passed, 0 failed`, total
  `69.5s`.
- runtime hot spots: latest full gate had `pytest` `37.9s`, `check-secrets`
  `19.5s`, `check-markdown` `14.9s`, `specdown` `2.5s`, and `run-evals` `2.0s`.
- coverage gate: enforced and passing at aggregate `60.0%` plus per-file
  `85.0%`; current result is `97.9%` (`1186/1211`).
- evaluator depth: `run-evals` passes 20 repo-local scenarios, so the bar is
  stronger than smoke-only review.
- Budgeted phases: `pytest` median `35.3s / 45.0s`,
  `check-coverage` median `11.9s / 15.0s`, `check-secrets` median
  `5.8s / 6.0s` with a latest-sample spike, `run-evals` median
  `2.4s / 5.0s`, `specdown` median `2.7s / 8.0s`.
- Runtime signals and smoothing state persist under `.charness/quality/`.

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

- Earlier standing-gate failures were removed through structural
  simplification: helper logic moved into repo-level seams, duplicate
  `init_adapter.py` wrappers collapsed, and `docs/handoff.md` now fits the enforced artifact limit.
- Public executable-spec boundaries are explicit in `spec`, and `quality` now inventories proof layering instead of asking only what proof is missing.
- Public spec inventory now reads actual `run:shell` blocks instead of misclassifying them as prose, so the quality lens matches specdown's real executable boundary.
- `README.md` was reduced into a short operator orienter while keeping the
  command-doc contract intact, so the root entrypoint doc now clears the
  length-pressure heuristic instead of acting like a second install manual.
- `specs/index.spec.md` and `specs/tool-doctor.spec.md` now prove current CLI contracts with direct command checks instead of delegating the whole story to pytest, and public-spec inventory is clean again.
- CLI ergonomics inventory, lint-ignore inventory, and dual-implementation inventory are currently clean: no flat-help registry pressure, no ignore debt, and no likely parity-smell candidates were detected in this tree.
- External-link review no longer fails on private/demo placeholder hosts such
  as `.internal`, `.test`, or `localhost`; `list_external_links.py` now keeps
  public URL health separate from repo-local or private SaaS examples.
- Control-plane traced coverage scenarios now include helper-contract branches
  for support sync, release probing, manifest/capability validation, and
  install helper lock-writing paths, so the coverage gate better reflects real
  maintained behavior instead of only top-level command flows.
- Remaining control-plane quality pressure is no longer coverage-floor debt; the
  standing gap moved back to documentation and skill ergonomics advisories.

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
- Rolling current-pointer artifacts now have an initial freshness ratchet for
  stale validator-existence claims, but most resolved claims are not yet
  cross-checked against current inventories automatically.

## Missing

- No broad freshness check yet cross-validates runtime, ergonomics, release, or
  dogfood claims against their owning live inventories.

## Deferred

- Do not promote ergonomics inventory into a hard gate until the repo narrows
  it to portability/discoverability rules instead of generic prose taste.
- Do not add a dedicated specdown adapter until multiple specs start repeating
  the same setup or extraction work.
- Do not describe the canonical fresh-eye path as blocked without a bounded
  capability probe and a concrete host signal; if the host still cannot spawn
  subagents, stop and leave the host-side contract gap visible.

## Commands Run
- `./scripts/run-quality.sh`
- `python3 scripts/check_coverage.py --repo-root .`, `python3 scripts/check_test_production_ratio.py --repo-root .`, and `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root .`

## Recommended Next Gates

- active `AUTO_CANDIDATE`: decide whether the remaining mode/option-pressure
  wording in `AGENTS.md`, `README.md`, `init-repo`, `retro`, and the
  contract-constrained `spec` phrase reflects real distinctions or should
  collapse into stronger defaults.
- active `AUTO_CANDIDATE`: decide whether `skills/public/quality/SKILL.md`
  should move more review prose into references or helper scripts so the core
  falls back under the `long_core` advisory threshold without losing routing
  precision.
- active `AUTO_CANDIDATE`: extend `validate-current-pointer-freshness` beyond
  stale validator-existence claims so rolling pointers cannot claim resolved
  ergonomics or runtime states that disagree with current inventories.
- active `AUTO_CANDIDATE`: decide whether command-doc-required flag examples
  should stay inline, move behind owner-doc links, or gain a small inventory
  exemption so README/UNINSTALL pressure tracks real prose clutter.
- active `AUTO_CANDIDATE`: if the repo wants another deterministic ratchet
  after coverage cleanup, decide whether entrypoint-doc or skill-ergonomics
  inventories should graduate into a narrow hard gate.
- active `AUTO_CANDIDATE`: decide which workflow should call the now-bootstrapped
  markdown-preview seam by default (`narrative`, `announcement`, `quality`, or
  a command surface) instead of leaving it as a helper that only exists on paper.
- passive `NON_AUTOMATABLE`: because gate promotion still needs maintainer
  judgment, only harden ergonomics heuristics that can survive without turning
  prose review into taste policing.

## History
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
