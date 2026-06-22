# Early Close Report — cautilus-skill-usage-validation-harness

## Why early closeout was chosen

This is an under-budget completion, not an abandonment. All 8 planned slices
landed and the empirical proof — one real cautilus `evaluate skill-experiment`
verdict (`discard`, honest zero source-coverage delta) from two real `claude -p`
captures — is recorded, roughly 2h into the 6h timebox. The goal's defined scope
is fully met. The `Done-early policy: continue_next_improvement` points at the
ranked backlog (#396 / the full multi-scenario sweep), but the Non-Goals
explicitly forbid absorbing those adjacent items into this goal, so the right move
is to close here and hand the next item to the next session via the handoff
rather than scope-creep within this artifact.

## What user decisions are needed

Two operator-only decisions are parked in `## Operator Decision Queue`, neither
blocking safe local progress: (1) whether to run the FULL multi-scenario
baseline-vs-variant Cautilus A/B sweep (a separate paid decision beyond the one
authorized proof run); (2) whether to define `reviewer_tiers.high-leverage` in
the quality adapter (optional proposal #5, not required for the single run). A
second cautilus scorer run of any kind re-enters this queue.

## Waste and retro

Waste observed: ~15 min lost to transient API 529 overload retrying sonnet
captures before switching to haiku (which captured cleanly); two capture-design
passes before the honest zero-delta result (a name-hinted task let the agent reach
refs by filename in both arms). The deeper lesson — source-coverage measures
file-set, not pointer-directness, so the eval task must make the measured signal
causally require the intervention — is recorded in the bound retro
`charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md`
and in `charness-artifacts/cautilus/latest.md` Follow-ups, and dispositioned in
the goal's `## Auto-Retro`.
