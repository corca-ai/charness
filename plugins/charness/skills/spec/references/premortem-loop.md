# Premortem Loop

Use this when the contract is concrete enough to review, but still risky enough
that a fresh implementer could misread the next move.

## Goal

Catch the most likely wrong implementation or review path before `impl`
inherits the contract.

## Preferred Path

If the runtime supports subagents and the session explicitly allows them:

1. run one bounded fresh-eye read with a contrasting lens
2. ask for the single most likely wrong next action
3. tighten only the lines that caused that misread

Good prompt shapes:

- "What would a fresh five-minute implementer most likely build wrong from
  this contract?"
- "Which acceptance check sounds stronger than the artifact actually proves?"
- "Which example line would make a reviewer over-generalize the intended
  behavior?"

## Fallback

If subagents are unavailable or not justified:

- do the same pass yourself without rereading the full discovery history first
- look for hidden sequencing, undeclared invariants, and examples that could be
  mistaken for policy
- keep the loop bounded to one pass plus one focused edit round

## Guardrails

- do not reopen broad ideation or option trees
- do not preserve speculative objections that do not change implementation
- prefer clarifying invariants, acceptance honesty, and next-step sequencing
  over adding more summary prose
