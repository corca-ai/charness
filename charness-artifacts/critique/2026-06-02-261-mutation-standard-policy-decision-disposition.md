# #261 Mutation Standard Policy Decision Disposition Review

Goal under review:
`charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`

Retro source:
`charness-artifacts/retro/2026-06-02-261-mutation-standard-policy-decision.md`

Reviewer disposition: closeout rung, read-only relative to the retro. This
review checks that each `## Next Improvements` item has concrete teeth or a
tracked follow-up.

## Per-Improvement Verdict

| # | Improvement | Claimed disposition | Verdict | Proof |
| --- | --- | --- | --- | --- |
| 1 | Decision carriers that accept low-value mutation survivors must state that accepted survivors remain report-visible and countable residue unless a real exclusion rule is introduced. | applied | dispositioned | The #261 issue carrier says accepted survivors remain report-visible and countable residue, not a hidden exclusion precedent. |
| 2 | Active achieve goals must remove draft-only closeout placeholders before final critique and complete-flip validation. | applied | dispositioned | This goal replaces the draft-only `Final Verification`, `User Verification Instructions`, and `Auto-Retro` placeholders before complete-flip validation. |
| 3 | For no-code issue closure, preserve the carrier/commit distinction: validate the closeout draft locally, then use a direct default-branch commit with `Close #<number>` rather than claiming remote closure before publication. | applied | dispositioned | The local issue carrier was draft-validated, and the final commit body is required to carry `Close #261`; remote GitHub closure remains a post-publication verification, not a local claim. |

## Verdict

All surfaced improvements are dispositioned without filing new issues. The
review found no memory-only improvement smuggled as `applied:`: each item maps to
an edited artifact or an explicit closeout publication invariant.

## Non-Claims

- This review does not claim GitHub issue #261 is already closed.
- This review does not introduce or validate a global equivalent-mutant
  exclusion policy.
- This review does not claim a fresh live mutation workflow or CI run.
