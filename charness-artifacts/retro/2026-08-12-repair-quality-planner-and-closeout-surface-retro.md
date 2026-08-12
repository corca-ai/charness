# Goal Retro: Repair quality planner and closeout surface
Goal: charness-artifacts/goals/2026-08-12-repair-quality-planner-and-closeout-surface.md
Date: 2026-08-12

## Context

The user grouped issues #603, #604, #581, #594, and #593 into one ordered active goal: repair local quality-planning and issue-closeout truth surfaces, then close only what the separate tracker protocol can honestly support.

## Evidence Summary

- Five semantic implementation commits: `470aae9a`, `09aac7e0`, `b5ed4b5b`, `b4e0ea69`, and `41a73c4d`.
- Focused proof passed per slice (87, 99, 35, 107, and 35 tests respectively); each slice also passed the complete pre-commit gate.
- The final local verification lock passed at `41a73c4dd48be8c2047f52d1ae80ba3692078804`; it is local evidence only, not a push, hosted-CI, consumer-runtime, or GitHub-close claim.
- Tracker rereads confirm all five selected issues are still `OPEN` with `comments_read: true`; the fixes are ten commits ahead of `origin/main` and have not been published.

## Waste

The proof-surface two-round rule found real repairs in #603, #604, #594, and #593. That cost review cycles, but it prevented each slice's first model of the surface from becoming the terminal claim. The only avoidable rework was needing direct-consumer regressions after helper-only evidence; future proof-surface plans should name the actual carrier up front.

## Critical Decisions

- #604 recognizes the Charness-owned direct runner invocation but does not require the runner for consumers; that restores the shipped form without converting an advisory absence into enforcement.
- #594 and #593 thread caller-known issue identity into shared closeout floors instead of widening generic parsing; this preserves the narrow carrier boundary.
- Keep GitHub closure separate: a local commit and local gate cannot stand in for a published implementation or a tracker readback.

## North Star Alignment

P4/P5 held: proof-surface changes received fresh-eye rounds and direct carrier evidence instead of treating a green unit suite as terminal. P1 held for reversible local edits by keeping each fix narrow. The process would have misapplied the north star if it closed tracker issues from local commits alone; the unpushed state is therefore recorded as a boundary, not papered over.

## Expert Counterfactuals

- Engelbart counterfactual: if each repaired floor had been accepted from its own helper test, the next operator would inherit a polished but incorrect closeout path. The direct carrier tests and reviewer rounds changed the next move.

## Sibling Search

- n/a — the observed waste was already bounded to the five selected owners; no plausible transferable sibling remained after direct-carrier regressions and source/plugin parity checks.

## Next Improvements

- workflow: applied: Final goal claims now distinguish a frozen local verification lock from the separately authorized publish and tracker-close phases.
- capability: applied: Proof-surface repairs now include direct-consumer regressions when the shared helper depends on caller-owned identity.
- memory: applied: The slice logs and this retro preserve the direct-loader, command-position, and target-binding lessons for later issue selection.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-12-repair-quality-planner-and-closeout-surface-retro.md
