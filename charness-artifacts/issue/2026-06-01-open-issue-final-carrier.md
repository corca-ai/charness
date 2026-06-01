# Open Issue Final Carrier

Date: 2026-06-01
Repo: corca-ai/charness
Goal: `charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`

## Carrier Scope

This carrier publishes the active open-issue closeout goal and then mutates live
GitHub issue state according to the goal matrix.

Close in the final carrier:

- #272 mutation report clarity
- #265 remaining coordination-cues survivor triage
- #259 symbol-residue advisory
- #258 shared-worktree review index safety
- #252 compact setup AGENTS contracts
- #243 usage episode report consumer and capture-gap visibility
- #241 create-skill host-extension adapter metadata
- #237 achieve closeout commit classification
- #236 CI-only failure retry discipline
- #185 AI/ML engineering success pattern investigation

Leave open intentionally:

- #261 mutation-standard policy for equivalent/low-value survivors
- #184 product success criteria and metric definition

## Evidence

Implementation and decision commits on `main` before publication:

- `cd9cfc5 Clarify mutation report blockers`
- `45fa641 Record mutation survivor disposition`
- `d7fb8e4 Harden workflow safety closeout`
- `ec229ea Support compact setup and adapter extensions`
- `13b861f Report usage episodes in quality`
- `aed6470 Record AI ML engineering success conditions`
- goal progress commits through `517b734 Record AI ML success goal progress`

Local proof recorded in the goal includes targeted tests per slice and slice
closeout gates. Final carrier proof added:

- live open-issue refresh before close/comment: `gh issue list --state open
  --limit 100 --json number,title,labels,updatedAt,url` still returned the 12
  scoped issues on 2026-06-01;
- final `./scripts/run-quality.sh --read-only`: PASS, 69 passed / 0 failed,
  total 46.3s;
- final bounded fresh-eye review: Ptolemy found carrier validation, untracked
  artifact, and stale handoff blockers; this artifact and
  [handoff](../../docs/handoff.md) record the fixes;
- closeout draft validation: `issue_tool.py validate-closeout-draft` PASS for
  #272/#265/#259/#258/#252/#243/#241/#237/#236/#185;
- push result and live GitHub close/comment result: to be recorded in the goal
  artifact after publication.

## Close Comment

Resolved in the open-issue generative closeout carrier.

JTBD: close the live open-issue backlog items that this goal actually resolved,
while preserving the two remaining policy/product issues as explicit non-claims.

Root cause: the backlog had accumulated several solved-or-solvable maintenance
issues without one auditable carrier tying local proof, final publication, and
live GitHub state together.

Debug artifact:
`charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`

Siblings: open-issue closeout matrix | decision: close only rows marked close in
the final carrier and comment on leave-open rows | proof: the goal matrix and
this carrier list #261 and #184 as leave-open rows with no close keywords.

Prevention: the active goal records per-slice proof, final carrier proof, and
leave-open reasons so future broad closeouts do not silently over-close product
or policy issues.

Critique: charness-artifacts/issue/2026-06-01-open-issue-final-carrier.md

Close #272.
Close #265.
Close #259.
Close #258.
Close #252.
Close #243.
Close #241.
Close #237.
Close #236.
Close #185.

Evidence:
- Goal artifact: charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md
- Final carrier artifact: charness-artifacts/issue/2026-06-01-open-issue-final-carrier.md
- Local branch was published after final quality proof and bounded fresh-eye review.

Scope note:
- #261 remains open for mutation-standard policy on equivalent/low-value survivors.
- #184 remains open for product-success synthesis and source-thread refresh.

## Fresh-Eye Review

Final-carrier fresh-eye review was performed by bounded read-only reviewer
Ptolemy (`019e8153-211d-7641-b531-b81a5c97c53d`) under the shared-worktree
guard: no checkout/restore/reset/stash/add and no file or issue mutation.

Initial blockers found:

- the carrier lacked close keywords and failed closeout validation;
- the carrier artifact was untracked;
- `docs/handoff.md` was stale and still pointed to Slice 4.

Disposition:

- this carrier now carries exact close keywords for the 10 close rows;
- the artifact is committed with the final carrier;
- `docs/handoff.md` is refreshed in the same final carrier commit before
  publication.

## Leave-Open Comments

For #261:

```text
Leaving this open intentionally after the open-issue closeout carrier.

The mechanical survivor triage path was handled through #265, but this issue
still owns the mutation-standard policy boundary for equivalent or low-value
survivors. This goal did not implement a gate-design exclusion or decide that
policy.

Relevant evidence:
- Goal artifact: charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md
- Final carrier artifact: charness-artifacts/issue/2026-06-01-open-issue-final-carrier.md
```

For #184:

```text
Leaving this open intentionally after the open-issue closeout carrier.

#185 was narrowed to necessary AI/ML engineering success conditions. Product
success remains separate: it needs maintainer synthesis of newer thinking and a
fresh read of the originating Slack thread before numeric targets, product
priorities, or outcome metrics are final.

Relevant evidence:
- Goal artifact: charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md
- Final carrier artifact: charness-artifacts/issue/2026-06-01-open-issue-final-carrier.md
- Engineering boundary: charness-artifacts/spec/issue-185-ai-ml-engineering-success.md
```

## Non-Claims

- No release is part of this carrier.
- Remote CI is not a separate claim unless it is observed after push.
- #261 and #184 are not closed by this carrier.
- Product success is not proven by #185 or by the usage episode report.
