# Cautilus Dogfood
Date: 2026-04-22

## Trigger

- slice: lock `premortem` to fresh bounded subagent-only meaning, remove local
  fallback wording from `premortem` and `release`, and make `impl`/`release`
  closeout report `Premortem: skipped|blocked`
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes public skill core wording for `premortem`, `impl`,
  and `release`, but it should preserve the checked-in startup routing contract
  while making the no-local-premortem rule explicit and validator-backed.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/impl/SKILL.md`
- `skills/public/premortem/SKILL.md`
- `skills/public/release/SKILL.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260422T041859538Z-run/`
- checked-in startup routing still preserves `bootstrapHelper=find-skills` plus
  `workSkill=impl`
- compact startup-bootstrap cases still passed unchanged:
  `find-skills -> impl` and `find-skills -> spec`

## Scenario Review

- representative scenario 1: a maintainer reading `premortem` should now see no
  local variant at all; if subagent capability is blocked, the result stays
  `Execution: blocked <host-signal>` instead of drifting into same-agent review
- representative scenario 2: an `impl` slice that does not need premortem
  should close with `Premortem: skipped <reason>` rather than implying a cheap
  inline premortem ran
- representative scenario 3: a `release` slice that does need premortem should
  stop with `Premortem: blocked <host-signal>` when the canonical subagent path
  cannot run instead of reopening a local-premortem loophole
- maintained scenario registry review: existing instruction-surface cases still
  cover the startup `find-skills -> impl/spec` contract, and this slice is a
  wording/closeout-contract tightening rather than a new routed user workflow,
  so no new checked-in scenario id was required yet

## Outcome

- recommendation: `accept-now`
- routing notes: the maintained startup routing surface stayed green while the
  public skill contract now makes subagent-only premortem and blocked/skipped
  closeout states explicit

## Follow-ups

- add a repo-owned planner and validator for `premortem required` trigger
  decisions instead of relying on prose-only caller judgment
- consider extending reviewed/maintained scenarios once `spec`, `quality`,
  `handoff`, or `narrative` adopt the same `executed|skipped|blocked` reporting
