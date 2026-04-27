# Cautilus Dogfood
Date: 2026-04-27

## Trigger

- slice: portable field lessons for #77.
- issue: user-visible scheduled workflows and local/pre-push gates can hide the
  actual owner of visible acknowledgement or network refresh work.

## Validation Goal

- goal: preserve
- reason: preserve startup skill routing and validation routing while adding
  portable debug and quality guidance for the field note.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/debug/SKILL.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/maintainer-local-enforcement.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `pytest -q tests/quality_gates/test_docs_and_misc.py::test_debug_and_quality_carry_async_and_hidden_network_field_lessons`

## Regression Proof

- run artifact: `.cautilus/runs/20260427T091923140Z-run/`
- summary:
  `.cautilus/runs/20260427T091923140Z-run/instruction-surface-summary.json`
- result: 5 passed, 0 failed, 0 blocked; recommendation `accept-now`

## Scenario Review

- Representative scenario: an agent debugs a scheduled or async user-visible
  workflow where the worker never starts, or reviews a local/pre-push gate that
  quietly performs external fetch/refresh work.
- Expected behavior: `debug` separates pre-worker acknowledgement, worker
  execution, and post-worker side effects, then names the earliest component
  that can produce observable status. `quality` treats hidden network,
  external-repo fetch, latest-release, or supply-chain refresh inside local
  gates as a review target rather than silent local proof.
- Observed behavior: the public guidance now records those two portable lessons
  without adding Ceal-, Slack-, or scheduler-specific vocabulary.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`.
  Existing instruction-surface routing still passed, and the new behavior is
  pinned by targeted doc tests plus public-skill dogfood notes.

## Outcome

- recommendation: `accept-now`
- routing notes: startup discovery still routes to `find-skills`; validation
  closeout still routes to `quality` before HITL or same-agent manual review.
- field-note notes: #77 is absorbed as portable debug/quality guidance, not as
  repo-specific Ceal behavior.

## Follow-ups

- If hidden network checks become a repeated deterministic failure mode, add a
  small quality inventory helper instead of expanding the public skill core.
