# Session Retro: achieve early-close report gap

## Context

The user correctly pointed out that the completed 2026-06-05 three-hour
code-quality goal ended early without delivering the report they needed: why it
ended early, which decisions required the user, and what waste was identified.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-05-3h-code-quality-bugfix.md`.
- Added report:
  `charness-artifacts/goals/2026-06-05-3h-code-quality-bugfix-early-close-report.md`.
- Skill change: `achieve` now requires an `Early close report:` evidence line
  whenever final verification records `No safe next slice:` or
  `Early close rationale:`.

## Waste

- The prior closeout treated the stop condition as sufficient because the local
  validator accepted `No safe next slice:`. It missed the user's operational
  need for a compact decision-and-waste report.
- The closeout message forced the user to ask a follow-up to get information
  that should have been included by default.

## Critical Decisions

- The fix adds a deterministic evidence floor instead of only improving prose.
  This makes the next early closeout fail before completion if the report is
  missing.
- The detailed report contract lives in `references/lifecycle.md` and
  `references/goal-artifact.md`, while `SKILL.md` keeps only a short trigger
  reminder to preserve core headroom.

## Expert Counterfactuals

- A release manager would have treated early termination as a stakeholder
  communication event, not only a local proof event: stop reason, owner
  decisions, and waste should ship together.

## Next Improvements

- Workflow: for every timeboxed early closeout, include a bound report artifact
  before status completion so the user receives stop rationale, decisions
  needed, and waste retro without asking.

## Sibling Search

- The transferable pattern is specific to `achieve` timebox closeout. Other
  closeout skills already require their own final summaries, and no sibling
  `No safe next slice:` evidence gate was found outside `achieve`.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-05-achieve-early-close-report-gap.md`
