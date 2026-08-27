<!-- charness-work-item-key: goal-draft-ownership-collapse -->

## Objective

Make the Goal Draft a planning-only record whose execution and closeout truth belongs to Goal Run and Work Items.

## Owned scope

Retain one planning validator/scaffold for naming, Markdown shape, safe paths, planning discussion, and frozen identity. Delete Slice Log, Auto-Retro, closeout, metric-window, timebox, blocked/superseded, operator-queue, terminal-evidence, `/goal @file`, append-slice, and related lifecycle helpers, fixtures, tests, validators, and stale prose. Remove implicit keyword activation behavior.

During draft-first ambiguity interview, ask only unresolved consequential questions, with a maximum ceiling of 15 questions. If none remain, report zero unresolved questions. End with one direct approval question stating the exact authorized provider effects. An unanswered turn is an ordinary wait and is not blocked.

## Acceptance

- Draft validation covers only planning concerns and frozen identity.
- No local execution, progress, retro, or closeout state remains.
- `/goal #N`, Goal Binding, Goal Run, and Work Items remain the execution path.
- Activation presents one bounded direct approval question with exact provider effects.
- No magic response token is required and no unanswered turn becomes failure or blocked state.

## Focused verification

Run focused Goal Draft and `/goal` tests for retained planning validation, frozen identity, zero/unresolved interview behavior, direct approval wording, unanswered approval, and absence of deleted lifecycle paths. Search consumers before deleting each helper family.

## Dependencies

`task-run-parallel-contract`.

## Non-claims

Do not create progress mirrors, handoff files, retro receipts, closeout bundles, compatibility shims, or a new activation protocol.
