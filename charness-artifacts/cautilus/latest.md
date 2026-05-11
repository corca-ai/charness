# Cautilus Dogfood
Date: 2026-05-11

## Trigger

- slice: 2026-05-10 quality follow-up Slice A — surface silent doctor.py
  coverage regression + bootstrap no-op short-circuit. Adapter edit bumps
  `runtime_budget_profiles.local-linux-aarch64-4cpu.budgets.check-coverage`
  from 22000ms to 40000ms because check-coverage now runs unconditionally
  in `--full` mode (pre-bump observed: latest 35008ms, median 23969ms,
  max 35676ms per `charness-artifacts/quality/latest.md` runtime hot
  spots; 40000ms gives ~12% headroom over observed max).
- source: [docs/handoff.md](../../docs/handoff.md) Next Session item 1.
- user approval: explicit approval to keep the budget bump in this slice and
  include the cautilus refresh after `validate_cautilus_proof.py` requested it.

## Validation Goal

- goal: preserve
- reason: the change adjusts a numeric runtime budget and a Bash gate condition
  that only affect when `check-coverage` runs; no public/support skill prompt
  surface text changes. Existing whole-repo skill routing should remain stable.

## Change Intent

- `prompt_affecting_change` (policy-classified — `.agents/*-adapter.yaml` is in
  the cautilus adapter's `prompt_affecting_patterns`, not because any prompt
  text changed)
- `adapter_contract_change`
- `truth_surface_change` (slice closeout updates `docs/handoff.md` Next
  Session pointer and adds the doctor.py untested-branch follow-up)
- `scenario_review_change`

## Prompt Surfaces

- `.agents/quality-adapter.yaml` (numeric `check-coverage` budget bump only —
  no SKILL.md, references, or AGENTS.md text changed in this slice).
- `docs/handoff.md` (next-session pointer update — truth surface, not a
  routed prompt).

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `python3 scripts/plan_cautilus_proof.py --json`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`

## Regression Proof

- eval test: 5 passed / 0 failed / 0 blocked, recommendation `accept-now`.
- run artifact: `.cautilus/runs/20260511T013107130Z-run/`
  - summary: `eval-summary.json`; counts 5 passed / 0 failed / 0 blocked.
  - All five cases matched expected routing: `checked-in-bootstrap-before-impl`,
    `checked-in-bootstrap-before-spec`,
    `validation-closeout-routes-before-hitl`,
    `compact-startup-bootstrap-before-impl`, and
    `compact-startup-bootstrap-before-spec`.
- cautilus tool recommendation: `accept-now`.

## Scenario Review

- Maintained routing fixture unchanged: the budget bump is a numeric tuning to
  reflect that `check-coverage` now runs unconditionally in `--full` mode; no
  expected whole-repo route is renamed, removed, or rerouted.
- The change touches no SKILL.md / references / AGENTS.md text; routing
  fixtures should be insensitive to runtime-budget knobs.
- Scenario-registry decision: no mutation to
  `evals/cautilus/scenarios.json`.

## Outcome

- recommendation: `accept-now`
- Surfacing the silent `scripts/doctor.py` 79.8% coverage regression and the
  bootstrap no-op short-circuit do not regress current whole-repo routing
  proof; the `--full` mode budget bump is the only adapter delta and remains
  routing-neutral.

## Follow-ups

- Slice A2: raise `scripts/doctor.py` coverage above the 85% per-file floor
  (covered by the regression now visible in `check-coverage`); revisit the
  `check-coverage: 40000` budget after coverage stabilizes.
- Keep the existing compact-surface discriminator follow-up from
  `docs/handoff.md`; this run is a single clean regression proof, not a
  multi-run robustness claim for compact `impl` versus `create-cli` routing.
