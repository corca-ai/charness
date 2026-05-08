# GitHub Issue 118: HITL Applied Rewrite Review

Source: https://github.com/corca-ai/charness/issues/118
Access: `gh issue view 118 --repo corca-ai/charness --json number,title,state,author,body,comments,labels,assignees,createdAt,updatedAt,url`
Captured: 2026-05-08

## Source Identity

- Repository: `corca-ai/charness`
- Issue: `#118`
- Title: HITL should show the applied chunk after a rewrite request
- State: open
- Author: `spilist`
- Created: 2026-05-08T10:35:59Z
- Updated: 2026-05-08T10:35:59Z

## Requested Facts

The issue reports that a chunked HITL reviewer may ask the agent to rewrite the
current chunk. After the edit is applied, the workflow can respond only with a
summary that the edit and checks passed. That breaks the review loop because the
human asked for a document change and needs to judge the changed material before
the cursor advances.

The desired public HITL contract is: when the user asks HITL to rewrite,
revise, or otherwise change the current chunk, the next assistant response shows
the applied chunk excerpt, preferably line-anchored or hunk-anchored, with
enough surrounding context to judge the rewrite. Verification results may be
included, but only as secondary information. The response should end with a
clear decision prompt asking whether the rewritten chunk is accepted or still
needs changes.

## Scope Boundaries

- This is a public HITL skill rule, not only an adapter preference.
- Adapters may tune chunk size, target scope, or display format.
- The core obligation is to show rewritten material after a requested rewrite
  before advancing the review cursor.
- This slice does not need to build a full HITL execution engine.

## Acceptance Shape

A future HITL run should leave runtime state or scratchpad evidence for:

- current chunk shown;
- reviewer requests rewrite;
- edit applied;
- rewritten chunk shown back before cursor advancement;
- reviewer accepts or requests another revision.

## Open Gaps

- The implementation should prove the public rule is present in `hitl` skill
  surfaces and that bootstrap state has a stable place to record pending
  applied-rewrite review status.
