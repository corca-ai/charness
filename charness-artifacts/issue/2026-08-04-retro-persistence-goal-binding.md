# Retro persistence can produce evidence that is not bound to the owning goal

## Situation

An active `achieve` goal requires its `Retro:` closeout evidence to bind to the
goal slug. The retro persistence workflow currently accepts a session-level
artifact name without requiring an owning goal identity.

## Operator experience

During goal `charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md`,
the closeout record cited `charness-artifacts/retro/2026-08-04-session-retro.md`.
That file existed and had a valid retro shape, but its `Goal:` named a different
objective. The goal was marked `Status: complete` until the authoritative
`check_goal_artifact.py` binding check rejected it. The operator had to create a
new goal-specific retro and repair the closeout record after the status claim had
already been written.

## Evidence

- Failing command: `python3 skills/public/achieve/scripts/check_goal_artifact.py
  --repo-root . --goal-path
  charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md`
  reported `retro_artifact` unbound because the cited file contained no goal
  slug.
- The repaired artifact is
  `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`.
- The persistence entrypoint is
  `skills/public/retro/scripts/persist_retro_artifact.py`; its current input is
  an artifact name and markdown file, not an owning goal reference.

## Impact

The validator catches the mismatch eventually, but the persistence boundary
allows a plausible, shape-valid retro to be selected for the wrong goal. This
creates closeout churn and makes a status claim look complete until the final
evidence-binding gate runs. The failure can recur for any goal whose operator
reuses a session retro path.

## Candidate direction (non-binding)

Consider an optional goal identity input or a goal-aware persistence helper that
stamps and validates the owning goal slug when a retro is intended as achieve
closeout evidence. Preserve session retros as a separate mode; do not force every
retro to become goal-scoped.
