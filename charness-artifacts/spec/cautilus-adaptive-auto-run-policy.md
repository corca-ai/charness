# Cautilus Adaptive Auto-Run Policy
Date: 2026-04-22

## Scope

Tighten `cautilus` adaptive execution policy so it stops asking before routine
prompt-surface proof runs while still preserving explicit confirmation for more
expensive maintained-scenario mutations.

## Decision

`adaptive` should mean:

- run prompt-surface regression proof automatically
- include short scenario review automatically when the planner asks for it
- ask only when the next move is to mutate maintained scenario coverage, such
  as adding, removing, or updating entries in `evals/cautilus/scenarios.json`

## Rationale

- `scenario_review` is part of proof, not a separate operator decision
- asking before every high-leverage prompt change creates too much friction and
  makes `adaptive` feel close to `ask`
- the real expensive/semantic follow-up is maintained scenario-registry
  mutation, not the checked-in scenario-review note in
  `charness-artifacts/cautilus/latest.md`

## Planner Contract

- `must_ask_before_running` should only be true for `run_mode: ask`
- planner should surface whether maintained scenario coverage needs review as a
  follow-up, not as a pre-run block
- planner notes should remind the agent to ask before mutating
  `evals/cautilus/scenarios.json` when that follow-up becomes real

## Non-Goals

- auto-mutating the maintained scenario registry
- collapsing `scenario review` and maintained scenario coverage into one concept
- removing the `ask` mode for repos that still want every cautilus run gated
