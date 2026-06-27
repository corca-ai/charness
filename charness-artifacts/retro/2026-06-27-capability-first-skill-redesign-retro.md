# Session Retro: capability-first-skill-redesign

Date: 2026-06-27
Mode: session

## Context

This retro reviews
`charness-artifacts/goals/2026-06-27-capability-first-skill-redesign.md`:
the skill-design slice that absorbed `genseq3` as a shared sequencing lens,
migrated `quality` from next-gate language to next-quality-move language, and
piloted the pattern on `create-cli` without adding a new blocking floor.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-27-capability-first-skill-redesign.md`
- Implementation commit: `10b048e7 Add capability-first quality move pilot`
- Source capture:
  `charness-artifacts/gather/2026-06-27-genseq3-skill.md`
- Pilot artifact:
  `charness-artifacts/quality/2026-06-27-create-cli-capability-move-pilot.md`
- Checks recorded in the goal: focused quality pytest `80 passed`, targeted
  inference/skill-doc pytest `40 passed`, ruff, `validate_skills.py`, doc links,
  markdown, attention-state visibility, and pre-commit on commit `10b048e7`.
- Packet Consumed: yes - `prepare_packet.py --prepared-for "capability-first
  skill redesign closeout"` reported changed files and owning surfaces.

## Waste

- The implementation slice was already coherent before closeout, but the goal
  artifact still carried unfilled closeout placeholders for retro, host-log
  probe, disposition review, and timebox fields. That made closeout a second
  artifact-repair task rather than a cheap final proof step.
- The active worktree also contains unrelated v0.56.7 release WIP. Keeping that
  boundary explicit was necessary, but it means broad lock-style closeout cannot
  honestly be claimed for this goal without mixing unrelated release state.

## Critical Decisions

- Treating `genseq3` as a shared reference, not `create-skill` doctrine, was the
  right coupling point. The lens is useful whenever order changes capability
  formation, not only when authoring skills.
- Renaming `quality` output to `Recommended Next Quality Moves` was more than a
  heading change because the planner/scaffold/validator now carry capability,
  center, proof-boundary, and enforcement-posture fields while preserving the
  old `Recommended Next Gates` alias.
- Piloting on `create-cli` before spreading hooks kept the change reversible and
  prevented a common concept from becoming a broad paperwork requirement.

## Expert Counterfactuals

- Christopher Alexander would have asked whether each step creates the next
  center that makes the following step easier. That would have led directly to
  the chosen order: shared lens, quality move language, target-skill packet,
  then a bounded `create-cli` pilot.
- Kent Beck would have asked for the smallest compatibility proof. That maps to
  keeping the legacy `Recommended Next Gates` parser alias while making new
  scaffolds write only the move vocabulary.

## Next Improvements

- workflow: When a goal changes shared skill contracts, bind the consumer pilot
  and the final closeout evidence names before broad hook propagation.
  Disposition: applied: this goal records the `create-cli` pilot before the
  adjacent hooks and closes with explicit retro/disposition evidence; no new
  blocking gate is added.
- capability: Quality target-skill review should be able to propose skill
  improvements in the same language used here: capability failure, current
  center, next center, proof boundary, and enforcement posture.
  Disposition: applied: `quality` planner/scaffold/validator now write and read
  `Recommended Next Quality Moves`, while the compatibility alias keeps old
  artifacts non-blocking.
- workflow: Do not let unrelated release WIP become proof for or against a
  design-skill goal.
  Disposition: applied: the goal's dirty-worktree boundary keeps v0.56.7 release
  WIP out of scope, and final verification records the broad-closeout non-claim.

## Sibling Search

- transferable pattern: closeout evidence was completed after implementation
  instead of being kept current as the slice advanced.
- siblings checked: achieve goal template already seeds final evidence lines,
  and `describe_goal_closeout_shape.py` surfaces the exact missing fields before
  complete.
- disposition: repo-local guard already exists; this run applies it by filling
  the evidence lines and records no new floor.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-27-capability-first-skill-redesign-retro.md

## Packet Consumed

Packet Consumed: yes - `prepare_packet.py --prepared-for "capability-first skill redesign closeout"`.
