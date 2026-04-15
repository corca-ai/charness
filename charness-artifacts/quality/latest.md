# Quality Review
Date: 2026-04-15

## Scope

Repo-wide quality posture for the current `charness` tree. This pass promoted
control-plane coverage from aggregate-only to an enforced per-file floor,
trimmed duplicated lifecycle helper code, added a test-production ratio gate,
and kept the HITL handoff inventory advisory.

## Current Gates

- `.agents/quality-adapter.yaml` records gate, review, preflight, security,
  runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` remains the quiet maintainer-local/pre-push gate.
- `./scripts/run-quality.sh --review` is the full quality-review gate: it
  replays PASS logs and enables online declared-link validation.
- `check-coverage` now enforces both the `60.0%` aggregate control-plane floor
  and an `80.0%` per-file floor for every tracked control-plane file.
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

- Latest full review after this slice: `36 passed, 0 failed`, total `52.1s`.
- runtime hot spots: `pytest` `30.0s`, `check-coverage` `9.8s`,
  `check-markdown` `6.8s`, `check-secrets` `4.8s`, external links `3.1s`.
- current budgeted phases: `pytest` `30.0s / 40.0s`, `check-coverage`
  `9.8s / 15.0s`, `check-secrets` `4.8s / 5.0s`, `run-evals` `2.6s / 5.0s`.
- online external links: `30 Total`, `30 OK`, `0 Errors`.
- coverage gate: present and passing.
- evaluator depth: maintained repo-local eval scenarios pass.
- runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- coverage gate: `86.4%` (`1137/1316`) against the `60.0%` aggregate
  floor and `80.0%` per-file floor.
- weakest tracked files are `sync_support.py` `80.0%`,
  `control_plane_lib.py` `82.2%`, and `install_tools.py` `82.5%`; these are
  fragile but no longer unfloored.
- direct trace scenarios now cover lifecycle helpers, install provenance,
  support sync, update/install lifecycle branches, and upstream release errors.
- test-production ratio is `0.53` (`9240/17454` Python lines), under the `1.00`
  ceiling.
- `check-test-completeness` verifies that standing pytest targets collect all tests.
- maintained eval depth exists: `run-evals` passes 19 repo-local scenarios.
- no `specs/` tree exists for `Covered by pytest:` reference validation in this
  repo snapshot.

## Healthy

- `upstream_release_lib.py` is no longer the weakest covered control-plane
  seam; focused failure-mode tests are in place.
- `install_tools.py` and `update_tools.py` no longer duplicate lifecycle
  metadata/healthcheck serialization helpers.
- Every tracked control-plane file now has an enforced `80.0%` floor.
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
- The stale retro-memory test anchor was corrected and documented separately.

## Weak

- Several control-plane files sit close to the `80.0%` floor; `sync_support.py`
  is exactly on the threshold and should be the next cleanup target.
- Skill ergonomics inventory is advisory only. It still flags long public cores
  for `create-skill`, `impl`, `quality`, and `spec`, plus mode/option pressure
  in several public skills.
- Entrypoint-doc ergonomics inventory flags `README.md` and
  `docs/operator-acceptance.md` as long first-touch docs; this is advisory, not
  a failing gate.
- `agent-browser` is installed at `0.25.3` while `doctor` observed latest
  `0.25.4`; `gws` is installed at `0.18.1` while latest is `0.22.5`.

## Missing

- No higher ratchet policy exists yet for files that clear `80.0%` but remain
  close to the floor.

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
- targeted pytest for upstream release probing, coverage floor, ratio, and HITL
  handoff inventory

## Recommended Next Gates

- active `AUTO_CANDIDATE`: refactor or delete code around `sync_support.py`
  before adding more tests; it is exactly at the enforced `80.0%` floor.
- active `AUTO_CANDIDATE`: ratchet per-file floors above `80.0%` only after the
  near-floor files have been simplified enough to make the higher bar honest.
- passive `NON_AUTOMATABLE`: because this needs maintainer judgment, decide
  whether `recent-lessons.md` should become a bounded rolling digest. HITL handoff: `target=recent-lessons.md`,
  `review_question=should recurring traps be retained beyond the latest
  retro`, `decision_needed=latest-only vs bounded rolling digest`,
  `must_not_auto_decide=true`, `observation_point=after next retro-producing
  session`, `revisit_cadence=after meaningful work units`,
  `automation_candidate=only after the human selects retention rules`.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
