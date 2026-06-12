# Retro: quality cadence duplicate followup

## Mode

session

## Context

This retro covers the active goal `quality-cadence-duplicate-followup`, spanning
three committed slices after `b300c8bf`: goal-closeout stub authoring, explicit
slice-vs-bundle validation cadence, and one focused adapter scalar helper
duplicate cleanup.

## Evidence Summary

- Goal artifact: `charness-artifacts/goals/2026-06-12-quality-cadence-duplicate-followup.md`.
- Slice commits: `ac7d37ea`, `21bd45e5`, and `75eed2fb`.
- Fresh-eye critique artifacts: `charness-artifacts/critique/2026-06-12-goal-closeout-stub-roundtrip-critique.md`, `charness-artifacts/critique/2026-06-12-validation-cadence-critique.md`, and `charness-artifacts/critique/2026-06-12-adapter-scalar-duplicate-cleanup-critique.md`.
- Final verification lock: `python3 scripts/run_slice_closeout.py --repo-root . --base b300c8bf --verification-lock --ack-cautilus-skill-review --refresh-broad-pytest-proof`.
- Host log probe: `charness-artifacts/probe/2026-06-12-quality-cadence-duplicate-followup-host-log-probe.json`.

## Waste

- The final closeout first used `origin/main` as the base, which pulled unrelated older local commits into the proof range and created avoidable Cautilus/public-skill review noise. The correct goal base was `b300c8bf`.
- Slice 2 briefly created superseded critique packet files before the final stable packet slug was regenerated. That did not affect committed state, but it added cleanup work.
- Slice 3 initially wrote a critique artifact that said no counterweight was spawned. The repo contract required the counterweight, so the artifact had to be corrected after spawning it.

## Critical Decisions

- Broad pytest was held until the final verification lock. That prevented the repeated broad-gate churn the goal was created to reduce.
- The `goal-closeout --emit-stub` proof tested the dispatcher output directly, not only the helper, which made the authoring path real.
- The duplicate cleanup chose a scalar helper-shaped adapter family with a repo-owned extraction boundary, not the larger portable skill-local bootstrap families reported by `nose`.
- The final proof was scoped to `b300c8bf..HEAD`, matching this goal's commits instead of the whole local branch divergence from `origin/main`.

## Expert Counterfactuals

- Gary Klein would have named the base-range decision as a pre-flight checkpoint before running final closeout: "what exactly is the mutation set I am proving?"
- Daniel Kahneman would have treated the `nose` numbers as a proxy with anchoring risk. The goal avoided over-claiming by naming the selected family and the remaining blind spots.

## Next Improvements

- Before final/bundle closeout on a multi-goal branch, record the intended proof base in the goal artifact before running `run_slice_closeout.py --base`.
- For advisory duplicate cleanup, keep using a family label that names the shape and owner surface, such as "adapter scalar helper-shaped", instead of a narrow function-name label.

## Sibling Search

The proof-base issue is transferable to any active goal closed on a branch that is already ahead of `origin/main`. Existing `run_slice_closeout.py --base` support is sufficient; the missing piece was operator discipline in the goal closeout sequence, not a missing command surface. The duplicate-family naming issue is already handled locally by this goal's slice log and critique artifact, and no sibling code/document surface needs a new guard.

## Persisted

yes - `charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md`
