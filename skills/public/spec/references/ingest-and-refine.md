# Ingest and Refine

`spec` should start from the current concept artifact, not from zero.

## Preferred Inputs

Use these in order:

1. checked-in ideation or concept docs
2. user-provided requirement docs or notes
3. a concise concept summary produced in the current conversation

## Refinement Rule

Refine the current concept into an implementation contract.

- keep stable ideas
- rewrite vague language into executable language
- keep discovery history out of the main spec unless it still affects scope
- preserve entities or stages when they are already the clearest representation

## Minimal Clarification Rule

Only ask follow-up questions when the answer changes:

- build scope
- acceptance criteria
- external dependency choice
- sequencing or rollout risk

If the answer does not change implementation in a meaningful way, choose a
reasonable default and explain it.
