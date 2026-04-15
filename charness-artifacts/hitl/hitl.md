# HITL Review Queue

Date: 2026-04-09

## Review Goal

Run the first durable human review pass for the `HITL recommended` public
skills under the current validation-tier policy.

## Target

- `announcement`
- `hitl`
- `ideation`
- `quality`
- `retro`

## Current State

- tier policy is fixed in `docs/public-skill-validation.md`
- repo-owned smoke and representative intent checks pass
- no human review decisions have been recorded yet for this pass

## Decision Needed

For each target skill, record whether the current public body:

- stays at `HITL recommended` with the current rationale
- should move toward a stronger evaluator path later
- has drift, ambiguity, or adapter seams that need follow-up fixes first

## Accepted Rules

- do not auto-promote a skill to `evaluator-required` without a concrete,
  defensible scenario path
- use the current public body and adjacent references as the primary review
  surface
- capture stable review rules before moving to the next skill

## Pending Queue

1. `quality`: confirm that proposal-skill behavior versus gate-skill behavior is
   still the right boundary
2. `ideation`: confirm that concept-shaping guidance is still judgment-heavy
   enough to stay HITL-first
3. `retro`: confirm that session and weekly mode guidance still belongs in one
   public skill
4. `announcement`: confirm that delivery seams remain adapter-driven and not
   product philosophy
5. `hitl`: confirm that the runtime model stays minimal without losing useful
   operator context

## Next State

When a human reviewer is available, run `hitl` against this queue and record
accepted rules plus any tier changes or follow-up fixes here.
