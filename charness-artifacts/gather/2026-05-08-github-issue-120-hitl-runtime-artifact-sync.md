# GitHub Issue 120: HITL Runtime Artifact Sync

Source: https://github.com/corca-ai/charness/issues/120
Access: `gh issue view 120 --repo corca-ai/charness --json number,title,state,author,body,comments,labels,assignees,createdAt,updatedAt,url`
Captured: 2026-05-08

## Source Identity

- Repository: `corca-ai/charness`
- Issue: `#120`
- Title: HITL should sync runtime state into the durable artifact before closeout
- State: open
- Author: `spilist`
- Created: 2026-05-08

## Requested Facts

The issue reports that HITL keeps live resumable state under
`.charness/hitl/runtime` while the checked-in current artifact lives at
`charness-artifacts/hitl/latest.md`. In a long session, runtime state can be
updated enough for local continuation while the durable artifact remains stale.
Because `.charness/hitl/` is intentionally uncommitted, the next session can
trust the wrong target, cursor, decisions, or queue.

## Desired Contract

Before HITL closeout or handoff, the workflow should sync live runtime state
into the adapter-owned durable artifact. The artifact should include:

- active target and cursor;
- accepted rules;
- reviewed, applied, pending, and superseded queue items;
- explicit next chunk to present;
- approval boundaries;
- links back to the runtime state files.

## Acceptance Shape

A future HITL closeout should warn or fail when:

- runtime changed after `charness-artifacts/hitl/latest.md`;
- durable target/cursor differs from runtime;
- durable artifact still names superseded decisions.

## Scope Boundaries

This issue does not require committing `.charness/hitl/runtime` or building a
full HITL execution engine. The immediate repair is a HITL-owned projection and
freshness check that makes hidden runtime state visible before closeout.
