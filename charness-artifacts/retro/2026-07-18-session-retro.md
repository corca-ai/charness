# Session Retro
Date: 2026-07-18

## Mode

session

## Context

Three related autonomous-improvement rounds exposed the same structural lesson. First, a broad gate showed that evidence-marker validity was coupled to physical Markdown lines. Then the YAML migration had covered only dispatch-marked inventories even though the operator intended every legacy inventory, and fresh-eye review found the new “compact” claim was not bounded everywhere. Finally, the first v2.1.0 release attempt showed that green per-slice proof did not cover the full unreleased range.

## Evidence Summary

- `charness-artifacts/debug/2026-07-18-debug-review.md` records the earlier citation-line coupling root cause.
- `charness-artifacts/critique/2026-07-18-coupling-critique.md` records the earlier sibling review.
- `charness-artifacts/critique/2026-07-18-complete-inventory-yaml-contract-and-v2-1-0-release.md` records two new angles, counterweight triage, fixes, and independent PASS rechecks.
- The all-inventory contract now discovers every `inventory_*.py`, runs source semantic parity, and byte-matches packaged commands.
- The release helper stopped before commit, tag, or push on nine cumulative changed-line coverage gaps; 159 in-process tests now cover those seams over the real `v2.0.0..HEAD` range.
- Packet Consumed: `charness-artifacts/retro/2026-07-18-052559-packet.md`; the current continuation used the planner's existing-artifact route.

## Waste

The first YAML slice optimized the visible dispatch list instead of first naming the complete capability population. That left two undispatched inventories and several partially migrated commands for a second pass. Later, separate CLI invocations compared a live pytest-temp footprint and created a flaky semantic test. The release attempt then paid the entire unreleased-range coverage debt at the latest possible reversible boundary. The rework came from defining contracts by current prose examples and isolated slice diffs rather than by the producer population, its volatile evidence seams, and the next irreversible consumer's full range.

## Critical Decisions

- Define the population structurally: every `inventory_*.py` plus every canonical dispatch command, not a hand-maintained migrated subset.
- Keep one shared selector/renderer and one bounded-list projection helper; individual scripts own only domain-specific summary fields.
- Execute semantic parity once on canonical source and prove packaged plugin commands by exact-copy equality, preserving the boundary while cutting the contract module from 19.34s to about 12.4s.
- Isolate volatile measurement input in contract tests instead of weakening equality assertions.
- Keep hidden JSON for programmatic compatibility while removing it from agent-facing docs, help, and ownership-verifier commands.
- Before release execution, run the release-range changed-line consumer against the last public tag; slice-local proof remains necessary but is not evidence for a cumulative publish boundary.

## Expert Counterfactuals

- Engelbart's system-improving lens treats method, language, and tool as one unit: “all inventories are YAML-first” should have shipped together with automatic population discovery and boundedness proof, not as prose plus a remembered migration list.
- Ousterhout's ownership lens asks which layer owns variability. Full evidence belongs to each producer, selection/rendering belongs to the shared helper, generated copies belong to sync, and volatile runtime footprint belongs behind an isolated test seam.

## Sibling Search

- same layer: all quality `inventory_*.py` scripts | decision: same waste, fix now | proof: all 20 are discovered and semantically probed
- abstraction up: dispatch/catalog/`.agents/surfaces.json` agent instructions | decision: same waste, fix now | proof: summary/detail YAML is taught and the lingering verifier `--json` call became `--detail`
- specialization down: Markdown recommendation output and mutation/write flags | decision: same waste, fix now | proof: incompatible Markdown/structured modes reject; execution and write flags remain explicit
- mental-model siblings: other programmatic JSON artifact seams | decision: intentional boundary | proof: hidden compatibility and persisted JSON files are machine consumers, not first-read agent interfaces

## Next Improvements

- workflow: before a cross-command migration, enumerate the producer population from the filesystem and the consumer population from routing/ownership declarations before selecting files.
- workflow: before an irreversible cumulative operation, compute and prove the exact cumulative range that the boundary will consume; do not assume individually closed slices compose automatically.
- capability: keep structural population discovery, semantic source probes, exact generated-copy proof, bounded-list helpers, and volatile-input isolation in the existing YAML contract test rather than adding another gate.
- memory: preserve this population-first migration rule and the earlier seam-first failure rule in `recent-lessons.md`, and reflect them in the next-session handoff only when they change the next move.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-18-session-retro.md
