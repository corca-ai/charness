# Disposition Review — goal 2026-07-08-fix-421-mutation-regression
Date: 2026-07-08

Rung-1b review of the Auto-Retro dispositions for this goal (binding + honesty
check). Source retro:
`charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md`.

## Decision Under Review

Whether each Auto-Retro disposition for the fix-421-mutation-regression goal
is bound to a real committed/working-tree change or an honest destination,
never prose-only memory.

## Failure Angles

- An `applied:` disposition naming a carrier file that does not actually
  contain the claimed lesson (the exact decay class the disposition floor
  exists to stop).
- A retro-recorded follow-up commitment silently dropped by Auto-Retro.
- A `none` structural-follow-up reason that misstates the restraint doctrine.

## Counterweight Pass

- Real (folded): the reviewer found disposition 1 overclaimed — the
  inherited-red↔CI-regression lesson was never selected by the
  recent-lessons refresher (grep-verified absent); the disposition text was
  corrected to name the actual carriers (debug Detection Gap + handoff
  Discuss entry). Same for disposition 4's unbound "and recent-lessons"
  clause — removed. The retro Sibling Search follow-up (RULE_DATE
  landing-day practice → handoff Discuss) was pending Slice 6; it is now an
  explicit item in the closeout handoff refresh so it cannot drop.
- Over-worry (not folded): none of the failures were dishonesty — the
  refresher's deterministic selection simply picked different lessons than
  the disposition prose assumed; the correction binds prose to reality
  rather than re-running the refresher to force a selection.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-07-08-fix-421-mutation-regression.md Auto-Retro disposition 1 | action: fix | note: claimed lesson absent from recent-lessons.md (grep-verified); disposition corrected to the real carriers before the complete flip.
- F2 | bin: act-before-ship | evidence: strong | ref: Auto-Retro structural follow-up line | action: fix | note: "and recent-lessons" evidentiary clause unbound (no RULE_DATE/landing-day trace in the file); clause corrected.
- F3 | bin: act-before-ship | evidence: strong | ref: retro Sibling Search follow-up (docs/handoff.md#discuss) | action: fix | note: retro-committed handoff Discuss entry for the RULE_DATE landing-day practice was still unwritten; added to the closeout handoff refresh so Auto-Retro and the baton agree.
- F4 | bin: over-worry | evidence: strong | ref: Auto-Retro disposition 2 (#422) and 3 (critique folds) | action: defer | note: both verified bound-and-honest (gh issue view 422 OPEN with matching body; git diff shows both test-file folds as described).

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent, separate context, read-only.
- Requested spawn fields: subagent_type=general-purpose, lower-power model
  (sonnet), named reviewer, bounded packet (four dispositions + source retro
  + binding checks to run).
- Host exposure state: applied
- Application state: host-confirmed: reviewer transcript recorded under the
  session subagents directory; verdicts returned with grep/gh/git-diff
  evidence per disposition.

## Fresh-Eye Satisfaction

parent-delegated — the rung-1b reviewer ran in a separate subagent context;
the parent folded its three binding corrections (disposition 1 and the
structural-follow-up clause reworded to actual carriers; handoff Discuss
entry added) before flipping the goal to complete.

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: the goal's Auto-Retro section (disposition claims) and the retro
  refresher (actual lesson selection).
- Consumer: the next session/operator reading dispositions as durable truth
  about where each lesson lives.
- Owning surface: the goal artifact owns disposition prose; generated
  recent-lessons.md owns refresher-selected lessons — the fix bound the
  former to the latter instead of hand-editing the generated surface.
- Verdict: owned-correctly
