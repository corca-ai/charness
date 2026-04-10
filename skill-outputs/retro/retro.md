## Mode
- `session`

## Context
- User correctly pointed out that `impl` lacks an explicit premortem even though adjacent workflow surfaces now use bounded premortem loops.
- The miss matters because the current review of named-person anchors and premortem philosophy was treating that behavior as already present in `impl` when it is not.

## Waste
- I inferred pattern consistency from nearby skills instead of verifying the `impl` body directly before speaking.
- I checked `handoff` and adjacent references first, then generalized too early.

## Critical Decisions
- Treat this as a workflow miss, not a wording nit.
- Add a direct body-level audit of target skills before claiming parity across skills.

## Expert Counterfactuals
- Gary Klein: run a quick premortem on my own claim first: "What is the most likely place this pattern is missing despite my expectation?" That would have sent me straight to `impl/SKILL.md` before asserting consistency.
- Daniel Jackson: inspect the actual concept boundary in each public skill body instead of assuming that a nearby reference or migration note means the user-facing concept contract already carries it.

## Next Improvements
- `workflow`: before claiming a pattern exists across multiple skills, verify each target `SKILL.md` body explicitly.
- `memory`: persist this miss in the session retro artifact so future sessions can see the failure mode.
- `capability`: when users ask for cross-skill concept alignment, do a small matrix audit rather than spot-checking one exemplar.

## Persisted
- yes `skill-outputs/retro/retro.md`
