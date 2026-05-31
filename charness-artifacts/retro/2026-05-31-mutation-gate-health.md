# Retro: Mutation-gate health goal
Date: 2026-05-31
Mode: session

## Context

Active achieve goal `charness-artifacts/goals/2026-05-31-mutation-gate-health.md`: align slice closeout with commit hooks (#266), prove current next-run mutation changed-line health, close #267 host-hook debt, and verify #262/#219 cluster closure while leaving #261 open for #265.

## Evidence Summary

- Goal artifact slice log and verification commands.
- Fresh changed-line mutation gates over `6d85aec..HEAD` and `9ee91ff..HEAD`.
- Bounded fresh-eye reviews for slices 1-3 and final closeout.
- Targeted pytest/ruff/length/doc gates and final slice closeout.

## Waste

- The goal artifact kept stale intermediate SHA wording (`0707515`, `a77f49b`) after later amendments, and fresh-eye reviewers had to catch it twice. The code work was sound, but the narrative current-state pointer lagged the real git state.
- Hand-mutant probing briefly hit the wrong return site before the exact gate-reported line was mutated; this was caught by inspecting the diff, but it cost an avoidable mini-loop.

## Critical Decisions

- Treating slice 1 as first-class work was correct: the real staged predict-commit gate caught length and attention-state obligations that prior aggregate closeout missed.
- Reframing slice 2 from `dad2d01` to current `HEAD` was necessary once slice 1 advanced the unpushed branch; preserving the original SHA would have been a false proof.
- Keeping #261 open was correct because this goal verified bounded hardening and did not complete the exhaustive survivor triage tracked by #265.

## Expert Counterfactuals

- Gary Klein lens: define the live operational picture at every phase boundary. The changed-line base is stable, but the head moves; every artifact sentence naming a head SHA should be treated as a stale-risk marker after each commit/amend.
- Daniel Kahneman lens: resist anchoring on the original plan-critique range. A small checklist item after each commit (`does the artifact still name the right HEAD?`) would have caught the stale range before final review.

## Next Improvements

1. Workflow: when an achieve goal names a mutable HEAD SHA, update or generalize the phrase immediately after each commit/amend; prefer `HEAD` plus the current proof command unless the exact immutable SHA is the proof target.
2. Workflow: for hand-mutant proof, mutate the exact gate-reported line after displaying that numbered line; if nearby code has similar returns/branches, include the line number in the test note.

## Sibling Search

- Stale mutable-SHA wording plausibly affects other active goal artifacts and handoffs that name `HEAD`-relative ranges. Sibling scan used `rg "HEAD=|HEAD is|\.\.HEAD|dad2d01|0707515|a77f49b" charness-artifacts/goals docs/handoff.md`; only this active goal needed correction in the current work.
- Wrong-nearby-line mutant probing is narrowly local to manual targeted-kill proof; no repo-wide code change is warranted.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-31-mutation-gate-health.md`
