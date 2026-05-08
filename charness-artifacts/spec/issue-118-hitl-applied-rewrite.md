# Issue 118 HITL Applied Rewrite Review

## Source

- GitHub issue: https://github.com/corca-ai/charness/issues/118
- Opened: 2026-05-08
- Request: After a reviewer asks HITL to rewrite the current chunk and the edit
  is applied, show the rewritten chunk back to the reviewer before advancing.

## Current Slice

Add a visible applied-rewrite review gate to the portable HITL contract and
runtime bootstrap state.

## Fixed Decisions

- The gate is named `applied_rewrite_review` so skill text, state fields, queue
  policy, and scratchpad section use one stable identifier.
- The gate is activated only after a reviewer-requested rewrite, revision, or
  current-chunk change has been applied.
- The next review response must show the rewritten chunk excerpt with a source
  anchor when possible, enough surrounding context, secondary verification
  results if available, and a decision prompt for accept vs another revision.
- HITL must not advance `last_presented_chunk_id` to a new chunk while
  `applied_rewrite_review_status` is pending.

## Acceptance Checks

- The public HITL skill requires showing the applied rewritten chunk before
  cursor advancement.
- `chunk-contract.md` documents the applied-rewrite excerpt shape.
- `state-model.md` documents the pending applied-rewrite state fields and the
  cursor advancement rule.
- `bootstrap_review.py` seeds `applied_rewrite_review` policy and state.
- Focused tests cover the bootstrap schema and skill/reference contract.

## Deferred

- A future HITL runtime helper can automate recording actual rewritten excerpts
  and applying the accept/revise decision. This slice defines the portable loop
  contract and resumable state slots without inventing a full execution engine.

## Premortem

- Fresh-eye HITL loop angle found that "applied" could be misread as permission
  to edit the target file mid-loop. Resolution: the public skill now says the
  requested rewrite is applied to HITL working text or session state before
  showing the rewritten excerpt.
- Fresh-eye runtime/state angle found that `applied_rewrite_review` policy and
  `applied_rewrite_review_status` runtime state could look like competing
  status owners. Resolution: the guardrail now names
  `applied_rewrite_review_status` as the pending runtime state.
- The same runtime angle recommended scratchpad placeholders for the seeded
  state fields. Resolution: bootstrap now creates pending chunk id, source
  anchor, applied excerpt, verification, and review result slots.
- Counterweight review found no full queue item lifecycle or runtime engine
  requirement for this slice; those remain deferred.
