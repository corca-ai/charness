# Quality Review
Date: 2026-04-15

## Scope

Repo-wide quality posture for the current `charness` tree. This pass consumed a
fresh dogfood log in `temp-log.txt`, implemented the proposed focused coverage
and coverage-inventory follow-ups, added an advisory HITL handoff inventory,
and re-ran the repo quality gates.

## Current Gates

- `.agents/quality-adapter.yaml` records gate, review, preflight, security,
  runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` remains the quiet maintainer-local/pre-push gate.
- `./scripts/run-quality.sh --review` is the full quality-review gate: it
  replays PASS logs and enables online declared-link validation.
- `inventory-quality-handoff` is now part of `run-quality.sh`; it is advisory
  and reports missing HITL handoff fields for `NON_AUTOMATABLE`
  recommendations.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.
- `core.hooksPath` points at `/home/ubuntu/charness/.githooks`.
- `check-command-docs` validates 8 command surfaces; install/update/doctor/
  reset doc drift is no longer an ungated missing item.

## Runtime Signals

- Latest full review after this artifact update: `35 passed, 0 failed`, total
  `39.9s`.
- runtime hot spots: `pytest` `24.2s`, `check-coverage` `8.5s`,
  `check-markdown` `3.7s`, external links `2.8s`, `check-secrets` `2.4s`.
- current budgeted phases: `pytest` `24.3s / 40.0s`, `check-coverage`
  `8.5s / 15.0s`, `check-secrets` `2.5s / 5.0s`, `run-evals` `1.6s / 5.0s`.
- online external links: `30 Total`, `30 OK`, `0 Errors`.
- coverage gate: present and passing.
- evaluator depth: maintained repo-local eval scenarios pass.
- runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- coverage gate: `69.8%` (`933/1337`) against the `60.0%` aggregate
  control-plane floor.
- weakest control-plane modules are `install_provenance_lib.py` `55.9%`,
  `install_tools.py` `64.4%`, `support_sync_lib.py` `65.3%`, and
  `update_tools.py` `68.2%`.
- `upstream_release_lib.py` improved from `48.8%` to `87.6%` after focused
  tests and direct trace scenarios for `gh`, HTTP, malformed JSON, and
  malformed payload paths.
- `check-coverage.py` now reports an advisory unfloored-file inventory:
  5 files below `80.0%` and 3 files in the `80.0-95.0%` warn band. The
  relationship remains `aggregate-floor-only`; no per-file floor was added.
- `check-test-completeness` verifies that standing pytest targets collect all tests.
- maintained eval depth exists: `run-evals` passes 19 repo-local scenarios.
- no `specs/` tree exists for `Covered by pytest:` reference validation in this
  repo snapshot.

## Healthy

- `upstream_release_lib.py` is no longer the weakest covered control-plane
  seam; focused failure-mode tests are in place.
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

- Five aggregate-covered control-plane files remain below the advisory
  `80.0%` per-file inventory threshold.
- Skill ergonomics inventory is advisory only. It still flags long public cores
  for `create-skill`, `impl`, `quality`, and `spec`, plus mode/option pressure
  in several public skills.
- Entrypoint-doc ergonomics inventory flags `README.md` and
  `docs/operator-acceptance.md` as long first-touch docs; this is advisory, not
  a failing gate.
- `agent-browser` is installed at `0.25.3` while `doctor` observed latest
  `0.25.4`; `gws` is installed at `0.18.1` while latest is `0.22.5`.

## Missing

- No bounded upper test-maintenance ratio signal exists yet; test breadth is
  controlled by completeness and runtime budgets, not by a ratio/size ceiling.
- No per-file coverage floor exists; the new unfloored-file inventory is
  advisory and intentionally does not fail the gate.

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
- targeted pytest for upstream release probing, coverage inventory, and HITL
  handoff inventory

## Recommended Next Gates

- active `AUTO_CANDIDATE`: use the unfloored-file inventory to choose the next
  focused coverage target, starting with `install_provenance_lib.py`,
  `install_tools.py`, `support_sync_lib.py`, `update_tools.py`, or
  `control_plane_lib.py`; do not add a hard per-file floor until at least one
  more focused target proves the cost.
- passive `AUTO_CANDIDATE`: add an upper test-maintenance ratio because the
  repo still needs to decide what cost ceiling should mean.
- passive `NON_AUTOMATABLE`: because this needs maintainer judgment, decide
  whether `recent-lessons.md` should become a bounded rolling digest. HITL handoff: `target=recent-lessons.md`,
  `review_question=should recurring traps be retained beyond the latest
  retro`, `decision_needed=latest-only vs bounded rolling digest`,
  `must_not_auto_decide=true`, `observation_point=after next retro-producing
  session`, `revisit_cadence=after meaningful work units`,
  `automation_candidate=only after the human selects retention rules`.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
