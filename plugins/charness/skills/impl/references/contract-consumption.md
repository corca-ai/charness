# Contract Consumption

`impl` should start from the current implementation contract, not from memory or
conversation drift.

## Read First

Use these in order:

1. the repo's canonical spec or design artifact
2. the most relevant handoff note when it materially changes the next action
3. the current diff or target files

If none of these give you an honest contract for the current slice, bootstrap a
small one inline before implementation begins.

## What To Carry Forward

Carry forward:

- the current slice
- fixed decisions
- success criteria
- acceptance checks
- probe questions that the implementation should answer

## What Not To Reopen

Do not reopen:

- broad product exploration
- already fixed decisions for this slice
- deferred decisions that do not block the current work

If any of those must reopen, the contract was not actually stable enough and
the work should route back to `spec` or `ideation`.
