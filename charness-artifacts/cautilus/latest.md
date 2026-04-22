# Cautilus Dogfood
Date: 2026-04-22

## Trigger

- slice: make external-seam risk survive `debug -> spec -> impl` through a
  repo-owned risk-interrupt planner, structured debug handoff fields, and a
  closeout backstop
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes public skill core wording for `debug`, `impl`, and
  `spec`, but it should preserve the checked-in startup routing contract while
  making the seam-risk carry-forward and interruption path explicit.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/debug/SKILL.md`
- `skills/public/impl/SKILL.md`
- `skills/public/spec/SKILL.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260422T050353833Z-run/`
- checked-in startup routing still preserves `bootstrapHelper=find-skills` plus
  `workSkill=impl`
- compact startup-bootstrap cases still passed unchanged:
  `find-skills -> impl` and `find-skills -> spec`

## Scenario Review

- representative scenario 1: a `debug` slice that crosses a host boundary
  should now leave structured `Seam Risk` and `Interrupt Decision` fields
  instead of relying on free-form handoff prose
- representative scenario 2: an `impl` slice that inherits a forced interrupt
  should now check the risk-interrupt planner before continuing plain
  implementation
- representative scenario 3: a `spec` slice that clears the interrupt must now
  consume it explicitly in `Premortem` with `Interrupt Source`, `Seam Summary`,
  `Chosen Next Step`, and `Impl Status`
- maintained scenario registry review: existing instruction-surface cases still
  cover the startup `find-skills -> impl/spec` contract, and this slice changes
  execution-sequence wording rather than the first-skill routing surface, so no
  new checked-in scenario id was required yet

## Outcome

- recommendation: `accept-now`
- routing notes: the maintained startup routing surface stayed green while the
  public skills now make forced seam-risk carry-forward and planner-backed
  interruption explicit

## Follow-ups

- add richer current-slice affinity than `debug/latest + named spec handoff`
  once the first interrupt path proves stable
- decide whether evaluator-required scenario coverage should grow from startup
  routing into a maintained `debug -> spec -> impl` interruption case
- review whether `latest.md` current-pointer generation should stay materialized
  or gain a repo-owned symlink policy instead of per-script write logic
