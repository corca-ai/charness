# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `instruction-surface` bootstrapHelper/workSkill split adoption for `charness`
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: validate the released `Cautilus v0.5.5` split contract against the
  checked-in `charness` routing fixtures without changing the intended repo
  behavior

## Prompt Surfaces

- `evals/cautilus/instruction-surface-cases.json`

## Commands Run

- `cautilus --version`
- `pytest tests/test_cautilus_scenarios.py`
- `python3 scripts/validate-cautilus-scenarios.py --repo-root .`
- `python3 scripts/run-evals.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- binary version: `0.5.5`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in bootstrap case now evaluates as
  `bootstrapHelper=find-skills` plus `workSkill=impl`; compact no-bootstrap
  implementation still routes directly to `impl`; both contract-shaping cases
  still route to `spec`
- summary notes: `cautilus.instruction_surface_summary.v1` now reports
  `bootstrapHelperCounts` and `workSkillCounts`, so the previous false mismatch
  on `find-skills -> impl` is gone
- premortem notes: this issue did not promote `premortem` into standing
  evaluator-required coverage; current policy remains on-demand/HITL proof plus
  repo-owned seam checks

## Follow-ups

- close `charness#39` with the concrete `v0.5.5` evidence and note that the
  remaining `premortem` question is policy, not a blocker on the bootstrap/work
  split
- if `premortem` later gets its own low-noise route-only expectation, add it as
  a separate checked-in case instead of folding it into the `find-skills -> impl`
  split proof
