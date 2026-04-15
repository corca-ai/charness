# Quality Review
Date: 2026-04-15

## Scope

Repo-wide quality posture for the current `charness` tree. This pass promoted
control-plane coverage from aggregate-only to an enforced per-file floor,
trimmed duplicated lifecycle helper code, lifted all tracked control-plane files
above 85%, raised the enforced per-file floor to 85%, added a test-production
ratio gate, made runtime budgets recent-median based, and kept the HITL handoff
inventory advisory.

## Current Gates

- `.agents/quality-adapter.yaml` records gate, review, preflight, security,
  runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` remains the quiet maintainer-local/pre-push gate.
- `./scripts/run-quality.sh --review` is the full quality-review gate: it
  replays PASS logs and enables online declared-link validation.
- `check-coverage` now enforces both the `60.0%` aggregate control-plane floor
  and an `85.0%` per-file floor for every tracked control-plane file.
- `check-test-production-ratio` enforces a Python test/source ratio ceiling of
  `1.00` using source-of-truth Python files, excluding generated plugin exports.
- `inventory-quality-handoff` is now part of `run-quality.sh`; it is advisory
  and reports missing HITL handoff fields for `NON_AUTOMATABLE`
  recommendations.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.
- `core.hooksPath` points at `/home/ubuntu/charness/.githooks`.
- `check-command-docs` validates 8 command surfaces; install/update/doctor/
  reset doc drift is no longer an ungated missing item.

## Runtime Signals

- Latest full review after this slice: `36 passed, 0 failed`, total `43.6s`.
- Runtime budgets now fail on recent-median drift and report single latest
  sample spikes separately.
- runtime hot spots: `pytest` `25.6s`, `check-coverage` `10.7s`,
  `check-markdown` `3.7s`, `check-secrets` `2.7s`, external links `2.5s`.
- current budgeted phases: `pytest` median `26.8s / 40.0s`,
  `check-coverage` median `9.3s / 15.0s`, `check-secrets` median `2.7s / 5.0s`,
  `run-evals` median `1.7s / 5.0s`.
- coverage gate: present and passing.
- evaluator depth: maintained repo-local eval scenarios pass.
- runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- coverage gate: `89.9%` (`1127/1254`) against the `60.0%` aggregate
  floor and `85.0%` per-file floor.
- weakest tracked files are `upstream_release_lib.py` `87.6%`,
  `control_plane_lib.py` `88.1%`, and `install_tools.py` `88.2%`; these are
  above the floor but still ratchet candidates.
- direct trace scenarios now cover lifecycle helpers, install provenance,
  support sync, update/install lifecycle branches, and upstream release errors.
- test-production ratio is `0.54` (`9345/17425` Python lines), under the `1.00`
  ceiling.
- `check-test-completeness` verifies that standing pytest targets collect all tests.
- maintained eval depth exists: `run-evals` passes 19 repo-local scenarios.

## Healthy

- Prior cleanup lifted `sync_support.py`, `install_tools.py`, and
  `control_plane_lib.py` above the 85% floor through production simplification.
- `support_sync_lib.py` now centralizes the upstream support skill-root
  invariant and moved from `87.5%` to `88.5%`.
- Runtime budget enforcement now distinguishes latest-sample spikes from
  recent-median drift.
- Clean temp-home update proof confirms installed `charness update` propagates
  checked-in plugin export changes into the host-visible plugin root.
- Every tracked control-plane file now has an enforced `85.0%` floor.
- Test-surface growth now has a hard ratio ceiling.
- The full review path exposes PASS-phase diagnostics instead of relying on
  quiet pre-push output.
- `gitleaks` `8.30.1`, `go` `1.26.2`, `specdown` `0.47.2`, and `cautilus`
  `0.2.4` are detected and healthy locally.
- `doctor.py --json` reports support-skill readiness and materialized Cautilus
  support discovery.
- No dual-implementation parity candidates were found by the advisory inventory.
- Standing gate verbosity inventory is healthy: compact phase-level signal plus
  `--review`/verbose escape hatch.

## Weak

- Several control-plane files sit close to the `85.0%` floor;
  `upstream_release_lib.py`, `control_plane_lib.py`, and `install_tools.py` are
  the next cleanup targets.
- Skill ergonomics inventory is advisory only. It still flags long public cores
  for `create-skill`, `impl`, `quality`, and `spec`, plus mode/option pressure
  in several public skills.
- Entrypoint-doc ergonomics inventory flags `README.md` and
  `docs/operator-acceptance.md` as long first-touch docs; this is advisory, not
  a failing gate.
- `agent-browser` is installed at `0.25.3` while `doctor` observed latest
  `0.25.4`; `gws` is installed at `0.18.1` while latest is `0.22.5`.

## Missing

- No automated ratchet planner exists yet for deciding when the next per-file
  floor increase is honest.

## Deferred

- Keep `check-supply-chain-online` out of default `--review`; registry
  reachability remains an operator-triggered diagnostic until a triage owner is
  assigned for provider outages.
- Do not update `gws` or `agent-browser` automatically from quality review; both
  are host-local tools and should move through the control-plane update flow.
- Do not turn skill ergonomics inventory into a hard gate until specific rules
  are selected in `skill_ergonomics_gate_rules`.

## Commands Run

- quality adapter/bootstrap/tool-recommendation scripts and advisory inventories
- maintainer preflight, `doctor.py --json`, full review, coverage, reference
  probes, and local tool version probes

## Recommended Next Gates

- active `AUTO_CANDIDATE`: refactor or delete code around `upstream_release_lib.py`,
  `control_plane_lib.py`, and `install_tools.py` before adding more tests; they
  are now the weakest tracked files near the enforced `85.0%` floor.
- active `AUTO_CANDIDATE`: add a small ratchet-planning report if future floor
  moves keep depending on manual inspection of the warn band.
- passive `NON_AUTOMATABLE`: because this needs maintainer judgment, decide
  whether `recent-lessons.md` should become a bounded rolling digest. HITL handoff: `target=recent-lessons.md`,
  `review_question=should recurring traps be retained beyond the latest
  retro`, `decision_needed=latest-only vs bounded rolling digest`,
  `must_not_auto_decide=true`, `observation_point=after next retro-producing
  session`, `revisit_cadence=after meaningful work units`,
  `automation_candidate=only after the human selects retention rules`.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
