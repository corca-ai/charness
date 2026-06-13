# Disposition Review: achieve-efficiency internal follow-ups

Fresh-eye rung-2 disposition review (separate agent context, read-only) of the
goal `charness-artifacts/goals/2026-06-14-achieve-efficiency-internal-followups.md`
`## Auto-Retro` dispositions against the cited retro
`charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`
`## Next Improvements` / `## Sibling Search`.

## Verdict

**PASS-WITH-NOTES.** All three surfaced improvements are dispositioned; the
`applied:` commit is real and correctly scoped; the two
`none — first occurrence; restraint applies` dispositions are internally
consistent with the Floor-Addition Restraint rule this goal itself shipped (S2).
No improvement was silently dropped. One accepted note (lesson-durability) below.

## Per-Improvement

- **A2 `--goal-path` is the right first closeout step** → `applied: e6d1a59a`.
  **Genuine.** Commit verified real (`git show --stat`): it wires the After-phase
  (SKILL.md + lifecycle.md) onto `--goal-path` in both source and the `plugins/`
  mirror — exactly what the disposition claims.
- **Stage explicit paths, not `git add -A`** → `none — first occurrence`.
  **Genuine (with note).** The restraint rule says promote to a blocking floor only
  on a recorded recurrence count; first occurrence is the right level. Lesson
  persisted in the retro + `recent-lessons.md`. Note: no authoring-surface prose
  carries a "pre-stage `git status` sanity" nudge, so the lesson rides on the
  recent-lessons decay policy.
- **Repo-root `scripts/*.py` mirror into `plugins/charness/scripts/`** →
  `none — staged-mirror-drift gate already enforces it`. **Genuine.** The gate is a
  real hard blocking pre-commit check; the waste was a proactive-sync habit gap,
  not a gate gap. Recording the lesson is the right disposition.

## Self-Consistency Check

Using the just-shipped Floor-Addition Restraint rule to opt out of a structural
guard on the `git add -A` waste is **principled, not a dodge.** The incident was
genuinely first-occurrence (Sibling Search confirmed no charness helper does
`git add -A`; no convention prohibited it; downstream gates blocked the worst
outcome). Applying the rule to the goal's own dispositions is the intended dogfood.
Minor caveat the reviewer flagged honestly: the "existing gates block the worst
outcome" argument is strongest for the mirror-pollution case; a purely untracked
non-mirrored file (like the off-goal `pry.json`) would not trip the
staged-mirror-drift gate — so the broader concurrent-WIP class leans on the
pre-stage `git status` habit, recorded in recent-lessons.

## Notes

1. `applied:` commit `e6d1a59a` (and `c75de40f`) verified present and correctly
   scoped — no ghost commit.
2. **Accepted residual (lesson durability):** the "stage explicit paths / pre-stage
   `git status` sanity" lesson lives only in the retro + `recent-lessons.md`
   (adaptive half-life). Consistent with the `none — first occurrence` call and the
   restraint discipline (no new floor on first sight), but a future session relies
   on the digest carrying it forward until a recurrence justifies stronger teeth.
   Operator-accepted; revisit if the pattern recurs.
3. `Structural follow-up: none` holds — the downstream staged-mirror-drift +
   unmatched-path gates already block the worst outcome; a new closeout guard on
   first sight is the exact reflex the restraint rule names.
