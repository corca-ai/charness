# Disposition Review: capability-first-skill-redesign

Goal: `charness-artifacts/goals/2026-06-27-capability-first-skill-redesign.md`
Retro: `charness-artifacts/retro/2026-06-27-capability-first-skill-redesign-retro.md`
Reviewer: bounded fresh-eye subagent, requested during closeout
Date: 2026-06-27

This review audits whether the goal can honestly close and whether the retro's
surfaced improvements have a real home. It is presence-plus-substance review;
deterministic gates only prove form.

## Verdict

PASS WITH NOTES after remediation. Bounded reviewer
`019f076e-62e8-7b83-bc42-fb9c97842a46` initially returned BLOCK because the goal
had flipped to `Status: complete` while this bound disposition artifact still
carried an unfinalized reviewer-placeholder verdict, and because commit
`10b048e7` alone did not contain the final retro/disposition closeout bundle.
The remediation is this finalized disposition record plus a separate closeout
commit that stages the modified goal, retro, and disposition artifacts together.

## Surfaced Improvements Audited

| # | Surfaced improvement | Disposition | Verdict |
| --- | --- | --- | --- |
| NI-1 | Bind consumer pilot and final evidence before broad hooks | Applied in this goal via the `create-cli` pilot and explicit closeout lines | verified |
| NI-2 | Quality target-skill review should propose capability moves | Applied in quality planner/scaffold/validator and tests | verified |
| NI-3 | Keep unrelated release WIP out of design-skill proof | Applied through the dirty-worktree boundary and broad-closeout non-claim | verified |
| SF-1 | Closeout evidence was completed late | Existing repo-local guard: goal template plus `describe_goal_closeout_shape.py` | verified; no new floor |

## Reviewer Findings

Act Before Ship:

- The reviewer found this artifact still carried an unfinalized placeholder
  while the goal claimed complete. This is remediated here before commit.
- The reviewer found `10b048e7` was an implementation commit, not the completed
  closeout commit. The goal now names it as the implementation commit only; the
  final closeout bundle must be committed separately.
- The reviewer noted `check_goal_artifact.py` proves bound evidence presence but
  not the semantic content of a pending disposition artifact. This artifact now
  records the semantic verdict explicitly.

Bundle Anyway:

- Commit the modified goal, retro, and finalized disposition review together.
- Keep the real homes for the retro improvements: the quality move language in
  `skills/public/quality/SKILL.md` and related planner/scaffold/validator
  surfaces; the `create-cli` pilot artifact and hook; and the existing
  closeout-shape helper.

Over-Worry:

- Do not require broad locked closeout for this local design-skill goal while
  unrelated v0.56.7 release WIP is dirty, provided the broad-closeout non-claim
  remains explicit.
- Do not require Cautilus, live host proof, or external proof for this scoped
  local skill/design change.
- Do not treat the shared `genseq3` reference as over-broad; the applicability
  guard prevents universal mandate drift.

Valid But Defer:

- A future validator could reject unfinalized reviewer-placeholder language when
  a goal claims complete. This is a real possible hygiene improvement, but
  adding a new floor is not needed for this slice.
- Additional target-skill pilots beyond `create-cli` can wait.

## Reviewer Tier Evidence

- Requested tier: default inherited parent model
- Requested spawn fields: agent_type=explorer; fork_context=false; no model override
- Host exposure state: metadata-hidden
- Application state: parent spawned bounded reviewer
  `019f076e-62e8-7b83-bc42-fb9c97842a46`; host accepted the agent but did not
  expose applied tier metadata

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent spawned bounded reviewer
`019f076e-62e8-7b83-bc42-fb9c97842a46`, consumed the returned four-bin critique,
and remediated the one Act Before Ship blocker before final closeout.
