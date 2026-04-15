# Retro Section Guide

The core retro stays small and repeatable.

## Context

State:

- what unit of work is under review
- why it mattered
- which evidence sources are trustworthy for this retro
- when conclusions mix hard local proof with weaker judgment, tag the claim
  strength inline as `strong`, `moderate`, `weak`, or `contested`

Do not repeat the entire session transcript.

## Waste

Identify where effort was lost:

- unnecessary backtracking
- hidden assumptions
- missing verification
- repeated reconstruction
- slow approval loops

Prefer causal explanation over complaint.

## Critical Decisions

Capture the decisions that changed outcome.

For each important decision:

- what was chosen
- what alternatives were skipped
- why the choice was made
- what it constrained later

This section explains the past. It is not the place for tool shopping.

## Weekly Additions

For `weekly`, add three bounded sections when they are supported by real
evidence:

- `Window`: the time span being reviewed
- `Evidence Summary`: which artifacts or commands were actually used
- `Trends vs Last Retro`: current delta versus the last durable weekly retro

If there is no prior weekly retro, say so plainly and skip the comparison
section instead of inventing trend data.

## Expert Counterfactuals

Ask:

- what would a strong expert in this domain have done differently?
- what question would they have forced earlier?
- what evidence would they have demanded before acting?
- where would they downgrade a confident story because the available evidence
  is only anecdotal or authority-based?

Prefer named experts with distinct lenses.

## Next Improvements

Every retro needs concrete future changes. Group them by type:

- `workflow`: process or sequencing change
- `capability`: skill, tool, adapter, preset, or automation change
- `memory`: durable note, handoff, checklist, or artifact update

This is where self-growing and self-healing live. Capability recommendations
belong here because they are future improvements, not past decisions.

## Snapshot

If the adapter defines `snapshot_path`, persist a compact machine-readable
snapshot for weekly mode. Keep it small:

- mode
- window
- evidence sources used
- real metrics or deltas actually cited

Do not invent a hidden snapshot format when no explicit path was configured.
