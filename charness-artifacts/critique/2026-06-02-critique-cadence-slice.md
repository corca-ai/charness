# Critique: Slice-Level Critique Cadence

Date: 2026-06-02
Fresh-Eye Satisfaction: `parent-delegated`
Packet Consumed:
`charness-artifacts/critique/2026-06-02-critique-cadence-slice-packet.md`

## Reviewed Change

Slice 2 of the workflow-review goal encodes critique cadence by risk boundary
instead of commit count. The change updates the repo operating contract,
`critique` skill trigger contract, new `critique/references/cadence.md`,
`achieve` slice packet guidance, dogfood notes, tests, and plugin exports.

## Reviewer Angles

- Lovelace: contract correctness/regression.
- Russell: workflow/process fit.
- Hooke: counterweight.

## Findings And Disposition

- applied: Lovelace found the same-agent local-risk rung omitted forced
  fresh-eye classes that the standalone rung named, including issue-closeout,
  rename, deletion, design-lock, and migration. The local-risk exclusion list
  now matches the standalone risk-boundary set, and
  `tests/quality_gates/test_critique_skill.py` pins those terms.
- applied: Lovelace and Russell found the high-visibility `achieve/SKILL.md`
  packet guidance still omitted owning/generated surfaces and out-of-scope
  lines. The source and plugin mirror now carry the expanded packet shape.
- applied: Hooke and Russell found the active goal still described Slice 2 as
  next/planned and carried the old packet fields. The active operating frame and
  Slice Plan now show Slice 2 in progress with the expanded packet fields.
- applied: Russell found `docs/handoff.md` would become stale after this slice.
  The handoff now says Slice 2 is in progress and the next move is to fold or
  verify remaining cadence findings before moving to invariant-first review.
- applied: Russell suggested clarifying that same-agent scoped critique is not a
  standalone `critique` invocation and that final closeout for non-trivial goals
  is standalone fresh-eye review. `critique/references/cadence.md` now says so.
- accepted: Hooke recommended no broad automation for every cadence decision in
  this slice. The change remains prose plus focused tests; no brittle cadence
  classifier was added.

## Verification

- `pytest -q tests/quality_gates/test_critique_skill.py
  tests/quality_gates/test_goal_artifact_lib.py` passed after folding blockers.
- `python3 scripts/validate_skills.py --repo-root .` passed.
- `./scripts/check-markdown.sh` passed.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .` passed.
- `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root .
  --goal-path
  charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`
  passed with status active.

