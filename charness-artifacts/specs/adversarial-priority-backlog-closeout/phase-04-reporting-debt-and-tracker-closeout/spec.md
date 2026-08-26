# Phase 4: Resolve reporting debt and close the cohort

Status: planned
Goal: [adversarial-priority-backlog-closeout](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)

## Objective

Disposition the remaining structural/reporting issues and close every claimed tracker row with issue-specific evidence, without waiting for one oversized bundle carrier.

## Scope In

- #717, #710, #708, #706, #704, and #703
- final reconciliation of all 26 claimed issues
- goal closeout, retro, and successor design after tracker readback

## Scope Out

- P3 backlog work
- a full release solely to close locally verifiable tracker records
- keeping an issue open because an ideal but unnecessary proof channel is expensive

## Dependencies

- Prior phases have published per-issue local carriers or explicit no-change dispositions
- Any issue requiring shared-history publication has an explicit operator grant before that boundary

## Completion Criteria

- All 26 claimed issues are CLOSED with concise evidence-backed comments
- No open claimed issue is hidden by a goal-complete status; an unavoidable open boundary blocks rather than completes the goal
- Final reconciliation lists closed issue state, behavior/disposition channel, residual risks, and any successor goal

## Verification

- GitHub source-of-truth readback returns CLOSED for every claimed issue
- Each issue has an independent behavior verdict or explicit typed disposition
- Goal artifact validation, final quality evidence, retro, and terminal records pass at the frozen target

## Non-Claims

- The goal does not claim P3 issues
- Issue closure does not authorize push, tag, or release
- A future regression may be filed as a new issue rather than keeping resolved records open indefinitely

## Failure Handling

If verification fails, use `debug` and a 5-whys root-cause pass. Record the structural pattern and repair before retrying; a retry alone is not completion.
