# Premortem Loop

Use this only when the handoff changed materially enough that the next operator
could plausibly pick up the wrong workflow or ownership model.

## Goal

Catch likely next-session misreads before the baton pass is finalized.

This is not for open-ended brainstorming. It is for bounded clarity failure
search.

## Preferred Path

If the runtime supports subagents:

1. run one premortem focused on workflow pickup ambiguity
2. run one premortem focused on ownership or boundary misread risk

Good prompt shapes:

- "What is the most likely wrong next action an operator would take from this
  handoff?"
- "Which line would make a future agent over-literalize an example or confuse
  reference code with runtime ownership?"

## Fallback

If subagents are unavailable:

- perform the same premortem yourself
- write down the single most likely misread
- tighten the handoff only where that misread is real

## Guardrails

- keep the loop bounded to one or two reads
- do not turn the handoff into a debate transcript
- do not preserve speculative objections that do not change the next pickup
- prefer fixing trigger lines, ownership wording, and references over adding
  more summary prose
