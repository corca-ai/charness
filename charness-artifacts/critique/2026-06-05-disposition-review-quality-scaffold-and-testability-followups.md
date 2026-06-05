# Disposition Review: quality-scaffold-and-testability-followups

Goal: charness-artifacts/goals/2026-06-05-quality-scaffold-and-testability-followups.md
Reviewer: fresh-eye disposition review (bounded subagent)

Slug: quality-scaffold-and-testability-followups

## Verdict per improvement

- workflow ("check recent-lessons + per-skill budget test before editing any
  SKILL.md"): **over-claimed** — marked `adopt` ("folded into this session's
  practice; candidate `recent-lessons` entry"), but `grep` of
  `charness-artifacts/retro/recent-lessons.md` finds NO budget/SKILL.md entry,
  and the selection policy's `next_improvement=4` slots are full of older
  lessons. "candidate ... entry" is the tell: nothing durable landed. The
  in-session "folded into practice" is real but evaporates with the session.
  Honest label is `defer` (or `adopt — pending landing`), not bare `adopt`.

- capability ("goal-draft interviews verify target-contract shapes in the Before
  phase"): **sound** — `defer` is correct. It is an `achieve`/goal-drafting skill
  change, genuinely out of scope for a repo-work goal, and it is also recorded in
  the goal's `## Off-Goal Findings`. Honest and right-scoped.

- memory ("baseline regenerated to canonical form, not hand-edited; decreases lag
  silently under `no_increase`"): **adjust (mild over-claim)** — marked `adopt`,
  "captured in the slice-3 commit + testability doc." Verified commit `0604f3d2`:
  its body does say "Regenerate the baseline to reflect the REAL conversions (no
  exemptions)", so the regenerate-not-hand-edit *practice* is demonstrated for
  this change. But `docs/testability-dsl-initiative.md` (the `no_increase` policy
  at lines 76-86) does NOT add the new forward "decreases can lag silently"
  maintainer warning, and `recent-lessons.md` has no such note either. The
  demonstrated practice is durable; the *lesson/warning* (the actual content of
  the improvement) did not land as guidance. `adopt` is half-true.

## Overall

The capability `defer` is honest and acceptable for closeout. The workflow
`adopt` should be downgraded to `defer` (or `adopt — pending`): its only durable
claim — a `recent-lessons` entry — was never written, so nothing outlives the
session. The memory `adopt` is partly substantiated (the commit demonstrates the
practice) but the silent-lag warning itself was not captured durably. Neither
mislabel is a closeout blocker — the two code-bearing slices had real fresh-eye
review and green gates — but the two `adopt`s overstate durability. Recommend the
goal record these as `adopt — pending recent-lessons landing` so a later session
is not misled into thinking the notes already exist.
