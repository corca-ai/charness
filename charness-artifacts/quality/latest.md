# Quality Review
Date: 2026-04-15

## Scope

Repo-wide quality posture for the current `charness` tree. This pass re-ran the
adapter bootstrap, preflight checks, advisory inventories, the full
`./scripts/run-quality.sh --review` gate, and one fresh-eye challenge pass
against coverage/spec/hook seams.

## Current Gates

- `.agents/quality-adapter.yaml` is valid and records gate, review, preflight,
  security, runtime-budget, concept-path, and prompt-asset policy fields.
- `./scripts/run-quality.sh` remains the quiet maintainer-local/pre-push gate.
- `./scripts/run-quality.sh --review` is the full quality-review gate: it
  replays PASS logs and enables online declared-link validation.
- `.githooks/pre-push` syncs checked-in plugin exports, fails on generated
  export drift, then runs the quiet quality gate.
- `core.hooksPath` points at `/home/ubuntu/charness/.githooks`.
- `check-command-docs` validates 8 command surfaces; install/update/doctor/
  reset doc drift is no longer an ungated missing item.

## Runtime Signals

- `./scripts/run-quality.sh --review`: `34 passed, 0 failed`, total `41.9s`.
- current budgeted phases: `pytest` `25.9s / 40.0s`, `check-coverage`
  `8.7s / 15.0s`, `check-secrets` `2.6s / 5.0s`, `run-evals` `1.7s / 5.0s`.
- runtime hot spots: `pytest` `25.9s`, `check-coverage` `8.7s`,
  `check-markdown` `3.7s`, `check-secrets` `2.6s`, and external links `2.9s`.
- online external links: `30 Total`, `30 OK`, `0 Errors`.
- coverage gate: present and passing.
- evaluator depth: maintained repo-local eval scenarios pass.
- runtime signals continue to persist under `.charness/quality/`.

## Coverage and Eval Depth

- coverage gate: `66.1%` (`879/1329`) against the `60.0%` aggregate
  control-plane floor.
- weakest control-plane modules are `upstream_release_lib.py` `48.8%`,
  `install_provenance_lib.py` `55.9%`, `install_tools.py` `64.4%`, and
  `support_sync_lib.py` `65.3%`.
- `check-test-completeness` verifies that standing pytest targets collect all
  discoverable tests.
- maintained eval depth exists: `run-evals` passes 19 repo-local scenarios.
- no `specs/` tree exists for `Covered by pytest:` reference validation in this
  repo snapshot.

## Maintainer-Local Enforcement

- `python3 scripts/validate-maintainer-setup.py --repo-root .` passed.
- `.githooks/pre-push` is installed through `core.hooksPath` and runs the
  canonical quiet quality gate before push.
- No GitHub Actions workflows are present; the enforced stop-before-finish path
  is maintainer-local.

## Enforcement Triage

- `AUTO_EXISTING`: validator/artifact/doc/security/style/test/eval/coverage/
  runtime-budget gates, plus plugin-export drift and maintainer hook setup.
- `AUTO_CANDIDATE`: strengthen focused tests around
  `scripts/upstream_release_lib.py`; add a bounded upper test-maintenance ratio
  or surface-size signal; decide whether repo-specific unfloored-file inventory
  should graduate from reference sample to an adapted local gate.
- `NON_AUTOMATABLE`: whether `recent-lessons.md` should remain latest-retro
  only or become a bounded rolling digest that preserves selected recurring
  traps; whether `gws` and `agent-browser` patch drift is worth updating now.

## Healthy

- The full review path now exposes PASS-phase diagnostics instead of relying on
  quiet pre-push output.
- `gitleaks` `8.30.1`, `go` `1.26.2`, `specdown` `0.47.2`, and `cautilus`
  `0.2.4` are detected and healthy locally.
- `doctor.py --json` reports support-skill readiness and materialized Cautilus
  support discovery.
- No dual-implementation parity candidates were found by the advisory inventory.
- Standing gate verbosity inventory is healthy: compact phase-level signal plus
  `--review`/verbose escape hatch.
- The stale retro-memory test anchor was corrected and documented in
  `charness-artifacts/debug/2026-04-15-retro-memory-test-anchor.md`.

## Weak

- `upstream_release_lib.py` remains the weakest covered control-plane seam at
  `48.8%`, while release metadata probing is operationally important.
- Skill ergonomics inventory is advisory only. It still flags long public cores
  for `create-skill`, `impl`, `quality`, and `spec`, plus mode/option pressure
  in several public skills.
- Entrypoint-doc ergonomics inventory flags `README.md` and
  `docs/operator-acceptance.md` as long first-touch docs; this is advisory, not
  a failing gate.
- `agent-browser` is installed at `0.25.3` while `doctor` observed latest
  `0.25.4`; `gws` is installed at `0.18.1` while latest is `0.22.5`.
- The coverage-floor reference inventory sample is not adapted to this repo's
  custom `scripts/check-coverage.py` gate shape.

## Missing

- No bounded upper test-maintenance ratio signal exists yet; test breadth is
  controlled by completeness and runtime budgets, not by a ratio/size ceiling.
- No repo-specific unfloored-file inventory gate exists beyond the custom
  aggregate control-plane coverage floor.

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

- active `AUTO_CANDIDATE`: add focused tests around `upstream_release_lib.py`
  failure modes, especially `gh` unavailable, `gh` unauthenticated, 404
  no-release behavior, and malformed release payloads.
- active `AUTO_CANDIDATE`: adapt the unfloored-file inventory idea to the
  existing `scripts/check-coverage.py` report shape, or explicitly document that
  the repo intentionally uses only an aggregate control-plane floor.
- passive `AUTO_CANDIDATE`: add an upper test-maintenance ratio because the
  repo still needs to decide what cost ceiling should mean.
- passive `NON_AUTOMATABLE`: because current behavior is latest-retro only,
  decide whether `recent-lessons.md` should become a bounded rolling digest.

## History

- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
