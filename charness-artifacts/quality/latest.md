# Quality Review
Date: 2026-04-15

## Scope

Repo-wide quality posture for the current `charness` tree. Current gates enforce
aggregate and per-file coverage, test-production ratio, recent-median runtime
budgets, first-pass specdown dogfood, and advisory HITL handoff inventory.

## Current Gates

- `.agents/quality-adapter.yaml` records gate, review, preflight, security,
  runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` is the quiet maintainer-local/pre-push gate;
  `--review` replays PASS logs and enables online declared-link validation.
- `check-coverage` now enforces both the `60.0%` aggregate control-plane floor
  and an `85.0%` per-file floor for every tracked control-plane file.
- `check-test-production-ratio` enforces a Python test/source ratio ceiling of
  `1.00` using source-of-truth Python files, excluding generated plugin exports.
- `specdown run -quiet -no-report` is now part of the quiet quality gate. The
  first spec covers stable CLI operator contracts by delegating to focused
  pytest e2e targets instead of introducing a custom adapter.
- `inventory-quality-handoff` is now part of `run-quality.sh`; it is advisory
  and reports missing HITL handoff fields for `NON_AUTOMATABLE`
  recommendations.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.

## Runtime Signals

- Latest local quality gate after this slice: `37 passed, 0 failed`, total
  `53.1s`; runtime budgets fail on recent-median drift.
- runtime hot spots: `pytest` `30.4s`, `check-coverage` `14.5s`,
  `run-evals` `4.5s`, `specdown` `4.1s`, `check-markdown` `4.0s`.
- Budgeted phases: `pytest` median `27.4s / 40.0s`,
  `check-coverage` median `9.6s / 15.0s`, `check-secrets` median `2.8s / 5.0s`,
  `run-evals` median `1.9s / 5.0s`, `specdown` median `4.4s / 5.0s`.
- runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- coverage gate: `89.9%` (`1127/1254`) against the `60.0%` aggregate
  floor and `85.0%` per-file floor.
- weakest tracked files are `upstream_release_lib.py` `87.6%`,
  `control_plane_lib.py` `88.1%`, and `install_tools.py` `88.2%`; these are
  above the floor but still ratchet candidates.
- direct trace scenarios cover lifecycle helpers, install provenance,
  support sync, update/install lifecycle branches, and upstream release errors.
- `specs/tool-doctor.spec.md` covers the stable specdown doctor contract and
  repo-local task envelope at the operator behavior level; fixture-heavy branch
  assertions remain in pytest.
- test-production ratio is `0.54` (`9345/17425` Python lines), under the `1.00`
  ceiling.
- `check-test-completeness` verifies that standing pytest targets collect all tests.
- evaluator depth: `run-evals` passes 19 repo-local scenarios.

## Healthy

- Runtime budget enforcement now distinguishes latest-sample spikes from
  recent-median drift.
- Every tracked control-plane file has an enforced `85.0%` floor and
  test-surface growth has a hard ratio ceiling.
- Specdown dogfood is now executable but intentionally narrow: one stable
  external-tool readiness behavior plus one task-envelope behavior, no custom
  adapter, and no duplicated shell fixture setup.
- `charness task` now provides a repo-local claim/submit/abort/status envelope
  under `.charness/tasks/` for bounded agent continuation.
- `gitleaks` `8.30.1`, `go` `1.26.2`, `specdown` `0.47.2`, and `cautilus`
  `0.2.4` are detected and healthy locally.

## Weak

- Several control-plane files sit close to the `85.0%` floor;
  `upstream_release_lib.py`, `control_plane_lib.py`, and `install_tools.py` are
  the next cleanup targets.
- Skill and entrypoint-doc ergonomics inventories remain advisory; they still
  flag long public cores, mode/option pressure, and long first-touch docs.
- `agent-browser` is installed at `0.25.3` while latest is `0.25.4`;
  `cautilus` is installed at `0.2.4` while latest is `0.4.0`; `gws` is
  installed at `0.18.1` while latest is `0.22.5`.
- The task envelope is intentionally local state only; it is not yet integrated
  into handoff, HITL, or any multi-agent scheduler.

## Missing

- No automated ratchet planner exists yet for deciding when the next per-file
  floor increase is honest.
- No dedicated specdown adapter exists yet. That remains acceptable until
  multiple specs start repeating the same setup or JSON extraction.

## Deferred

- Keep `check-supply-chain-online` out of default `--review`; registry
  reachability remains an operator-triggered diagnostic until a triage owner is
  assigned for provider outages.
- Do not update `gws` or `agent-browser` automatically from quality review; both
  are host-local tools and should move through the control-plane update flow.
- Do not turn skill ergonomics inventory into a hard gate until specific rules
  are selected in `skill_ergonomics_gate_rules`.

## Commands Run

- quality gate, specdown acceptance, adapter/package/doc validators, and local
  tool probes

## Recommended Next Gates

- active `AUTO_CANDIDATE`: refactor or delete code around `upstream_release_lib.py`,
  `control_plane_lib.py`, and `install_tools.py` before adding more tests; they
  are now the weakest tracked files near the enforced `85.0%` floor.
- active `AUTO_CANDIDATE`: add a small ratchet-planning report if future floor
  moves keep depending on manual inspection of the warn band.
- active `AUTO_CANDIDATE`: dogfood `charness task` in one real repo slice before
  broadening its semantics; the next separate sah-derived candidate is doctor
  next-action ergonomics.
- passive `NON_AUTOMATABLE`: because this needs maintainer judgment, decide
  whether `recent-lessons.md` should become a bounded rolling digest. HITL handoff: `target=recent-lessons.md`,
  `review_question=should recurring traps be retained beyond the latest
  retro`, `decision_needed=latest-only vs bounded rolling digest`,
  `must_not_auto_decide=true`, `observation_point=after next retro-producing
  session`, `revisit_cadence=after meaningful work units`,
  `automation_candidate=only after the human selects retention rules`.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
