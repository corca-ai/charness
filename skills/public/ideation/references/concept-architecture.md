# Concept Architecture

`ideation` is not just discovery. It is the loop for building a concept
incrementally when the user may not yet know the full shape.

## Core View

Treat the concept as a living model that gets sharper through conversation.

The agent should maintain:

- verified facts
- assumptions
- open questions
- candidate direction
- rejected or obsolete ideas when they still matter briefly

Then rewrite the model as new information arrives. Do not let contradictory
versions accumulate just because the conversation was long.

When the concept persists across turns, this model should live in repo
documents, not only in chat summaries.

## Why This Matters

Working memory is limited for both humans and agents. `Ideation` should
externalize the emerging world instead of pretending the whole concept can stay
in short-term conversational context.

## The Main Loop

1. restate the concept
2. model the current world
3. test the riskiest assumption
4. sharpen the wedge or structure
5. update the world model
6. decide whether to keep exploring, run validation, or hand off to `spec`

## Document Discipline

If the user is building the concept incrementally, update the working document
at each meaningful step.

- sharpen the existing concept doc when one exists
- split into multiple views only when that reduces confusion
- prefer a stable canonical home over spawning fresh ad-hoc notes

## Philosophy Anchors

- worldbuilding through conversation is normal, not a failure
- some concepts win by choosing a hard problem because that becomes the moat
- some concepts need a deliberately easy first move to learn faster
- feedback should arrive early and often
- agent-native surfaces should be considered from the beginning
- understanding humans and understanding agents are both design work
