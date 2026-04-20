# Premortem Loop

Use this only when the handoff changed materially enough that the next operator
could plausibly pick up the wrong workflow or ownership model.

## Goal

Catch likely next-session misreads before the baton pass is finalized.

This is not for open-ended brainstorming. It is for bounded clarity failure
search.

## Canonical Path

Canonical execution uses two bounded premortem subagent reads:

1. run one premortem focused on workflow pickup ambiguity
2. run one premortem focused on ownership or boundary misread risk

Good prompt shapes:

- "What is the most likely wrong next action an operator would take from this
  handoff?"
- "Which line would make a future agent over-literalize an example or confuse
  reference code with runtime ownership?"

## Capability Check

Run the capability check in
`../../premortem/references/subagent-capability-check.md`: attempt the bounded
subagent setup, resolve availability uncertainty, and cite the concrete host
signal. Do not assume subagents are unavailable from priors.

## If The Host Blocks The Canonical Path

Stop and record the concrete host signal. Treat it as a host-side operating
gap for this run. Do not replace the misunderstanding premortem with a
same-agent local pass and still call the baton pass verified.

## Guardrails

- keep the loop bounded to one or two reads
- do not turn the handoff into a debate transcript
- do not preserve speculative objections that do not change the next pickup
- prefer fixing trigger lines, ownership wording, and references over adding
  more summary prose
