# Premortem Loop

Use this when the contract is concrete enough to review, but still risky enough
that a fresh implementer could misread the next move.

## Goal

Catch the most likely wrong implementation or review path before `impl`
inherits the contract.

## Canonical Path

Canonical execution uses a bounded fresh-eye subagent with a contrasting lens:

1. run one bounded fresh-eye read with a contrasting lens
2. ask for the single most likely wrong next action
3. tighten only the lines that caused that misread

Good prompt shapes:

- "What would a fresh five-minute implementer most likely build wrong from
  this contract?"
- "Which acceptance check sounds stronger than the artifact actually proves?"
- "Which example line would make a reviewer over-generalize the intended
  behavior?"

## Capability Check

Run the capability check in
`../../premortem/references/subagent-capability-check.md`: attempt the bounded
subagent setup, resolve availability uncertainty, and cite the concrete host
signal. Assuming subagents are unavailable from priors is the exact failure
mode that check exists to stop.

## If The Host Blocks The Canonical Path

Stop and report the concrete host signal. Treat it as a host-side operating
gap for this run. Do not replace the fresh-eye premortem with a same-agent
local pass and still call the contract reviewed.

## Guardrails

- do not reopen broad ideation or option trees
- do not preserve speculative objections that do not change implementation
- prefer clarifying invariants, acceptance honesty, and next-step sequencing
  over adding more summary prose
