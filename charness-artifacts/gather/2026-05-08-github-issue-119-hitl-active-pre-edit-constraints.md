# GitHub Issue 119: HITL Active Pre-Edit Constraints

Source: https://github.com/corca-ai/charness/issues/119
Access: `gh issue view 119 --repo corca-ai/charness --json number,title,state,author,body,comments,labels,assignees,createdAt,updatedAt,url`
Captured: 2026-05-08

## Source Identity

- Repository: `corca-ai/charness`
- Issue: `#119`
- Title: HITL should turn accepted rules into active pre-edit constraints
- State: open
- Author: `spilist`
- Created: 2026-05-08T10:53:36Z
- Updated: 2026-05-08T10:59:51Z

## Requested Facts

The issue reports that a chunked HITL reviewer may establish stable rules such
as preferred product vocabulary, forbidden internal terms, or review-surface
expectations. Those rules can be recorded in scratchpad or runtime state, but
the workflow does not currently force the next edit to re-apply them as active
constraints.

The issue also ties rule application to stale target and cursor failures: before
editing or rewriting a chunk, HITL should verify that target, cursor, queue item,
and line bounds match the chunk being edited.

## Desired Contract

Before editing or rewriting a HITL chunk, the workflow should:

- read accepted rules for the current HITL run;
- verify target, cursor, queue item, and line bounds against the chunk being
  edited;
- select relevant rules for the current chunk;
- state active constraints briefly before patching;
- scan the changed chunk for known forbidden or risky term classes before
  presenting it;
- record newly accepted rules so they apply to later chunks.

## Scope Boundaries

- This is core HITL loop behavior.
- Adapters may define repo-specific terms, forbidden classes, or chunk sizing.
- The base loop owns promoting accepted rules into pre-edit constraints and
  preventing stale target/cursor state from steering the next edit.
- This slice does not need to implement a full HITL execution engine.

## Acceptance Shape

A future HITL runtime should make visible:

- `accepted_rules` contains durable review rules;
- each chunk edit records `active_rules_applied`;
- each chunk edit records `target_cursor_checked` or equivalent;
- the assistant shows which active rules guided the edit;
- a rule violation or stale cursor keeps the cursor on the same chunk until
  repaired.
