# Issue 117 HITL Full Target Review

## Source

- GitHub issue: https://github.com/corca-ai/charness/issues/117
- Opened: 2026-05-08
- Request: HITL should present the full updated target after all chunk reviews
  compose, then persist whole-target acceptance or another-pass status before
  closing the target.

## Current Slice

Add a visible full-target completion gate to the portable HITL contract and
runtime bootstrap state.

## Fixed Decisions

- The gate is named `full_target_review` so state, queue, and scratchpad use one
  stable identifier.
- The initial bootstrap state seeds the item as `pending_after_chunks` with an
  activation condition; later review execution advances it after chunks are
  accepted and the target edit is applied or staged.
- HITL may show a bounded full target-scope view for very large files, but it
  must name the boundary and cannot silently close the target as accepted.

## Acceptance Checks

- `bootstrap_review.py` writes `full_target_review` into `state.yaml`,
  `queue.json` items/completion metadata, and `hitl-scratchpad.md`.
- The public HITL skill requires a full target review after the Apply Phase.
- The state model reference documents accepted vs `needs_another_pass` outcomes.
- Focused tests cover the bootstrap schema and skill/reference contract.

## Deferred

- A future runtime helper can automate advancing `full_target_review` after a
  real chunk queue drains. This slice defines the portable state contract and
  closeout rule without inventing a larger HITL execution engine.

## Premortem

- Fresh-eye runtime/state angle found an item-vs-gate mismatch and a temporal
  naming mismatch in the first draft. Resolution: model `full_target_review` as
  a pending completion item in `queue.json`, include it in `items`, and use
  `activation_condition` rather than `created_after`.
- Fresh-eye packaging/validator angle found that startup `find-skills` artifact
  refresh was unrelated to #117. Resolution: commit that capability inventory
  refresh separately from the issue-closing HITL change.
