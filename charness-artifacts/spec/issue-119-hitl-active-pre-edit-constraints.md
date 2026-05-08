# Issue 119 HITL Active Pre-Edit Constraints

## Source

- GitHub issue: https://github.com/corca-ai/charness/issues/119
- Opened: 2026-05-08
- Request: Before editing or rewriting a HITL chunk, re-apply accepted review
  rules as active constraints and verify target/cursor/bounds alignment.

## Current Slice

Add a visible pre-edit constraint gate to the portable HITL contract and runtime
bootstrap state.

## Fixed Decisions

- The gate is shown as `Pre-Edit Constraints` in the scratchpad; runtime state
  uses the concrete machine slots below.
- Runtime state uses `active_rules_applied` for the selected accepted rules and
  `target_cursor_checked` for target/cursor/queue/bounds alignment.
- The gate applies before chunk edits and rewrites, including the applied
  rewrite loop from issue 118.
- A failed rule scan or stale target/cursor check keeps the cursor on the same
  chunk until repaired.

## Acceptance Checks

- The public HITL skill requires accepted rules and target/cursor/bounds checks
  before editing or rewriting a chunk.
- `rule-propagation.md` documents active rule selection, risky-term scanning,
  and stale cursor handling.
- `state-model.md` documents `accepted_rules`, `active_rules_applied`, and
  `target_cursor_checked`.
- `bootstrap_review.py` seeds pre-edit constraint state and scratchpad slots.
- `check_review_state.py` blocks pre-edit or cursor-advance transitions when
  cursor evidence is missing, accepted rules are not active, or applied rewrite
  review is still pending.
- Focused tests cover the bootstrap schema and skill/reference contract.

## Deferred

- A future HITL runtime helper can automate rule selection, term scans, and
  cursor repair. This slice defines the portable loop contract, resumable state
  slots, and minimal transition checks without inventing the full execution
  engine.

## Premortem

- Fresh-eye HITL loop angle found that `target_cursor_checked: true` could go
  stale unless the check result names the chunk, queue item, line bounds, and
  queue epoch. Resolution: the state model now requires
  `target_cursor_check_result` to name the checked subject.
- Fresh-eye runtime/schema angle found that `target_cursor_check_result` was in
  state but not visible in the scratchpad pre-edit gate. Resolution: bootstrap
  now includes the result slot in the scratchpad and the focused test asserts
  both state and scratchpad output.
- Fresh-eye UX angle found that output shape did not mention the new pre-edit
  fields. Resolution: the public skill output shape now includes Active Rules
  Applied and Target/Cursor Checked.
- Counterweight review found no need to build rule-selection, risky-term scan,
  or cursor-repair automation in this slice; those remain deferred.
- Root-cause review found that prose-only transition rules would let the same
  failures recur. Resolution: add `check_review_state.py` as a lightweight
  runtime gate for pre-edit and cursor-advance phases.
