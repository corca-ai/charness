# Session Retro
Date: 2026-07-18

## Mode

session

## Context

Five related autonomous-improvement rounds exposed the same structural lesson. First, a broad gate showed that evidence-marker validity was coupled to physical Markdown lines. Then the YAML migration had covered only dispatch-marked inventories even though the operator intended every legacy inventory, and fresh-eye review found the new “compact” claim was not bounded everywhere. The first v2.1.0 release attempt showed that green per-slice proof did not cover the full unreleased range. The follow-on quality slice then found the immediate cause: coverage production generated an authoritative consumer command but closeout never executed it or rendered an explicit non-claim. The v2.1.2 slice found the same ownership error inside a small parser: one permissive token splitter mixed Python rule identifiers, named ESLint/Pylint rules, and human rationale, while a lazy token generator escaped the exception boundary intended to protect it.

## Evidence Summary

- `charness-artifacts/debug/2026-07-18-debug-review.md` records the earlier citation-line coupling root cause.
- `charness-artifacts/critique/2026-07-18-coupling-critique.md` records the earlier sibling review.
- `charness-artifacts/critique/2026-07-18-complete-inventory-yaml-contract-and-v2-1-0-release.md` records two new angles, counterweight triage, fixes, and independent PASS rechecks.
- The all-inventory contract now discovers every `inventory_*.py`, runs source semantic parity, and byte-matches packaged commands.
- The release helper stopped before commit, tag, or push on nine cumulative changed-line coverage gaps; 159 in-process tests now cover those seams over the real `v2.0.0..HEAD` range.
- `charness-artifacts/critique/2026-07-18-quality-infrastructure-correctness-and-v2-1-1-release.md` records the producer/consumer, untracked-file, operator-visibility, export-sync, and counterweight review.
- The final quality gate passed 81/81 in 56.5s; pytest was 36.1s. Module-scoped seeds remove repeated construction, but timing stayed at the recent median, so the slice makes no speedup claim.
- Nose transport moved to one 85-line owner; the two former consumers fell from 334/331 to 313/310 code lines while retaining schema ownership.
- Packet Consumed: `charness-artifacts/retro/2026-07-18-052559-packet.md`; the current continuation used the planner's existing-artifact route.
- `inventory_lint_ignores.py --summary` reproduced rationale words inside the
  structured `codes` field; after repair, focused tests passed 40/40 and the
  structural-waste inventory moved its repeated stable-file reads from 2 to 0.
- Packet Consumed: `charness-artifacts/retro/2026-07-18-111102-packet.md` for
  the v2.1.2 continuation.

## Waste

The first YAML slice optimized the visible dispatch list instead of first naming the complete capability population. That left two undispatched inventories and several partially migrated commands for a second pass. Later, separate CLI invocations compared a live pytest-temp footprint and created a flaky semantic test. The release attempt then paid the entire unreleased-range coverage debt at the latest possible reversible boundary. Its producer emitted the exact consumer command, but the workflow treated producer exit zero as completion; the command was data nobody consumed. The first repair also missed untracked files, accepted `{}` as a verdict, and hid `not_checked` in normal text until fresh-eye review. In the latest slice, the initial parser fix still trusted a `try` around generator construction even though `TokenError` occurs during iteration; a named fresh-eye angle and counterweight caught it before lock. The first locked run then spent 36.4 seconds reaching a durability failure that the repo already knew how to detect, because repo-Markdown surface routing omitted the existing validator. The rework came from defining contracts by current prose examples, shared string shapes, intermediate success, and broad-gate ownership rather than by the complete population, final consumer, semantic grammar, cheapest owning route, volatile seams, and irreversible range.

## Critical Decisions

- Define the population structurally: every `inventory_*.py` plus every canonical dispatch command, not a hand-maintained migrated subset.
- Keep one shared selector/renderer and one bounded-list projection helper; individual scripts own only domain-specific summary fields.
- Execute semantic parity once on canonical source and prove packaged plugin commands by exact-copy equality, preserving the boundary while cutting the contract module from 19.34s to about 12.4s.
- Isolate volatile measurement input in contract tests instead of weakening equality assertions.
- Keep hidden JSON for programmatic compatibility while removing it from agent-facing docs, help, and ownership-verifier commands.
- Before release execution, run the release-range changed-line consumer against the last public tag; slice-local proof remains necessary but is not evidence for a cumulative publish boundary.
- Treat a generated verifier command as an executable handoff, not documentation: run it when the range is honest, otherwise render `NOT CHECKED` with the excluded population and exact next command.
- Validate the consumer's own minimum verdict and range identity before translating it into a parent status; process exit and parseable JSON are transport facts, not proof.
- Reuse immutable test seeds only behind per-test clones and an explicit contamination test; report eliminated setup work separately from measured wall-clock change.
- Give each external directive family its own grammar owner; sharing transport or rendering does not justify sharing a permissive semantic parser.
- Put lazy iteration inside the exception boundary and make fallback atomic, so a late failure cannot mix partial primary results with fallback results.
- Route an existing deterministic check through the changed surface that can
  trigger it; a gate that exists only in the broad suite is late feedback, not
  an author-time capability.

## Expert Counterfactuals

- Engelbart's system-improving lens treats method, language, and tool as one unit: “all inventories are YAML-first” should have shipped together with automatic population discovery and boundedness proof, not as prose plus a remembered migration list.
- The same Engelbart lens applies to coverage closeout: the method says final-consumer proof, the language needs an explicit `not_checked` state, and the tool must execute or visibly defer the generated consumer. Any one without the other recreates terminal green.
- Ousterhout's ownership lens asks which layer owns variability. Full evidence belongs to each producer, selection/rendering belongs to the shared helper, generated copies belong to sync, and volatile runtime footprint belongs behind an isolated test seam.
- Engelbart's method/language/tool unit applies at parser scale too: the method
  says “brief the judge accurately,” the language distinguishes rule identifiers
  from rationale, and the tool needs syntax-specific parsers plus executable
  malformed-input proof. A generic splitter made all three look simpler while
  weakening the actual capability.

## Sibling Search

- same layer: all quality `inventory_*.py` scripts | decision: same waste, fix now | proof: all 20 are discovered and semantically probed
- abstraction up: dispatch/catalog/`.agents/surfaces.json` agent instructions | decision: same waste, fix now | proof: summary/detail YAML is taught and the lingering verifier `--json` call became `--detail`
- specialization down: Markdown recommendation output and mutation/write flags | decision: same waste, fix now | proof: incompatible Markdown/structured modes reject; execution and write flags remain explicit
- mental-model siblings: other programmatic JSON artifact seams | decision: intentional boundary | proof: hidden compatibility and persisted JSON files are machine consumers, not first-read agent interfaces
- same layer: producer commands that emit follow-up verifier commands | decision: same waste, fix now for mutation coverage | proof: closeout consumes the command or renders a visible range non-claim
- abstraction up: generic Nose subprocess/version handling | decision: same ownership smell, fix now | proof: `nose_tool_lib.py` owns transport while domain schemas stay with callers
- specialization down: immutable test seed caches | decision: safe only with clone isolation | proof: one clone mutation cannot change the module seed or a later clone
- same layer: lint directive parsers | decision: same waste, fix now | proof: repo scan found one shared parser site; it now separates Python identifiers from named rules
- abstraction up: YAML inventory renderer | decision: intentional boundary | proof: raw snippets retain rationale while producer-owned `codes` stays semantic
- specialization down: lazy tokenization fallback | decision: same waste, fix now | proof: tokens materialize before findings; malformed EOF yields exactly one fallback result
- mental-model siblings: Nose token normalization | decision: intentional boundary | proof: its caller already catches iteration-time `TokenError` and falls back atomically
- abstraction up: repo-Markdown surface obligations | decision: same waste, fix now | proof: the existing evidence-durability validator now runs before broad pytest for changed Markdown

## Next Improvements

- workflow: before a cross-command migration, enumerate the producer population from the filesystem and the consumer population from routing/ownership declarations before selecting files.
- workflow: before an irreversible cumulative operation, compute and prove the exact cumulative range that the boundary will consume; do not assume individually closed slices compose automatically.
- workflow: when one phase emits a verifier command for the next, bind the closeout to the final consumer's verdict or an operator-visible non-claim; never let the intermediate producer's green become terminal.
- capability: when optimizing fixture setup, pair immutable shared seeds with private clones and isolation proof, and separate structural work reduction from noisy wall-clock claims.
- capability: keep structural population discovery, semantic source probes, exact generated-copy proof, bounded-list helpers, and volatile-input isolation in the existing YAML contract test rather than adding another gate.
- capability: model directive grammars separately and put lazy iteration inside
  the exception boundary; use one malformed-input test to prove fallback
  atomicity instead of another prose rule or gate.
- workflow: when a broad gate catches a cheap deterministic defect on a changed
  surface, first repair that surface's existing-validator routing; do not create
  a duplicate floor or rely on memory.
- memory: preserve this population-first migration rule and the earlier seam-first failure rule in `recent-lessons.md`, and reflect them in the next-session handoff only when they change the next move.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-18-session-retro.md
