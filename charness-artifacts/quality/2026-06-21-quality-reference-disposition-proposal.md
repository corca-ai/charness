# Quality reference disposition — DRAFT PROPOSAL (2026-06-21)

**STATUS: draft for critique. Critique this before executing any disposition.**
Next session starts by critiquing this map (adversarial fresh-eye), then executes
only the approved items. Nothing here has been applied; the tree is clean.

## Why this exists

Operator reframe: routing/test-pin is only a SIGNAL, not a value verdict. A
test-pin does not make content valuable; an orphan is not worthless. Judge each
reference on MERIT against the skill's current purpose, then: route the good
un-routed ones, fold duplicates, delete only the truly meaningless.

## The quality skill's current purpose (judged against)

`quality` = understand and improve the repo's CURRENT quality posture (not one
narrow bug/test): detect the gate+source surface (via inventory-dispatch.md) →
run existing gates → inspect 4 lenses (concept / behavior / security /
operability) → classify by enforcement tier + posture → propose concrete next
gates/cleanups (delete/merge/split/extract/narrow over prose) → fresh-eye review
→ honest posture summary; also reviews authored skills. Metric = concept clarity
+ closed escapes, never line count. A reference serves the purpose if it is the
deep, consultable detail behind a lens, a gate contract/economics, the dispatch
routing, an Output-Shape section, skill-review, or adapter policy — detail the
body correctly keeps out but a judge needs on demand.

## Method

Read-only fan-out: one agent per .md reference (41 total). Routing status passed
as an input signal only; each agent re-checked REAL consumers (incl. eval
scripts, docs, sibling refs) and judged merit by content. Full per-ref
assessments: workflow `quality-ref-merit` (run 2026-06-21).

## Headline — nothing is meaningless

| disposition | count | meaning |
|---|---|---|
| keep-as-is | 34 | high/medium merit, reachable, non-duplicated |
| route-it | 5 | valuable but un-routed → add a pointer (Raskin discoverability fix) |
| merge | 2 | valuable-but-overlapping → fold unique bit into a routed owner, retire |
| **delete** | **0** | **no reference is truly meaningless** |

**Meta-finding (vindicates the reframe):** the routing heuristic over-flagged
badly. Many "orphan/test-only" refs had real consumers it missed — e.g.
`bootstrap-posture` (eval registry), `automation-promotion` /
`adapter-gate-review` (advisory-interpretation-contract, deferred-decisions),
`cli-ergonomics-smells` / `entrypoint-docs-ergonomics` (dispatch script-routes).
Merit + consumer-check is the right method; un-routed ≠ worthless, test-pin ≠
valuable. The real defect is a **discoverability gap**, not bloat.

## Actionable items (the only proposed changes)

### route-it (5) — add a pointer so a judge can reach valuable un-routed detail
1. **operability-signals** (high) — the operability LENS detail (92 lines), only
   in the flat References list. Route from the body's operability lens (step 4)
   and/or the dispatch operability entry. *(target to confirm in critique.)*
2. **executable-spec-economics** (medium) — owns executable-spec runtime/dup
   economics, shell-adapter escape hatch, stale changed-file-router trap. Route
   from inventory-dispatch.md "Runtime And Test Economics" (≈L70–119), secondary
   from quality-lenses.md L53.
3. **brittle-source-guards** (medium) — three-tier brittle_count taxonomy + fix
   order + policy-without-tool rule (script is routed, the prose is not). Route
   from inventory-dispatch.md Source Hygiene (L160–161 / rollup 216–217).
4. **adapter-gate-review** (medium) — the only doc defining the 5 finding_class /
   3 enforcement_tier labels `inventory_adapter_gate_design.py` emits + the
   Template-First doctrine (deferred-decisions D28). Route from inventory-dispatch.md
   "Language And Adapter Policy" adapter/gate-design entry (L235–243).
5. **dual-implementation-parity** (high) — concept-integrity lens; script+test
   back it but the prose is un-routed. Route from the concept lens. *(target to
   confirm in critique.)*

### merge (2) — fold the unique bit into a routed owner, retire the file
6. **startup-probes** (medium) → fold the unique probe defaults + "doctor is not
   fast startup" guardrail into `adapter-contract.md`'s startup_probes block
   (which already owns the schema; ~half the file duplicates it). Retire + de-list.
7. **sample-presets** (low) → fold the preset names + the unique vulture/knip
   keep-advisory-until-low-noise policy into `adapter-contract.md` (owns
   preset_id/lineage/coverage_floor/specdown defaults). Rest duplicates
   adapter-contract / coverage-floor-policy. Retire + de-list. (Not a delete —
   the vulture/knip sentence is load-bearing and unduplicated.)

### keep-as-is (34)
adapter-contract, agent-production-runtime, automation-promotion, behavior-testing,
bootstrap-escalations, bootstrap-posture, boundary-bypass-ratchet, cautilus-on-demand,
ci-recoverable-gate-triage, cli-ergonomics-smells, coverage-floor-policy, dup-ratchet,
entrypoint-docs-ergonomics, gate-classification, installable-cli-probes, inventory-dispatch,
lint-ignore-discipline, maintainer-local-enforcement, mutation-testing, prompt-asset-policy,
proposal-flow, public-spec-layering, quality-lenses, quality-signal-scorecard, security-npm,
security-overview, security-pnpm, security-uv, skill-ergonomics, skill-quality,
standing-doc-provenance, standing-gate-verbosity, testability-and-selection, unit-test-quality.

## What the next-session critique should adversarially probe

- **Keep-bias.** 34/41 kept, 0 deletes — did per-ref agents rubber-stamp? Spot-check
  the weakest keeps (e.g. quality-lenses: un-routed + test-pinned; is the test
  over-fitting?) and the security trio (per-manager near-dups).
- **No holistic dedup.** Agents judged each ref in isolation — re-check cross-ref
  duplication the per-ref view can miss (the skill-quality ↔ skill-ergonomics
  checklist overlap from the prior audit is NOT in this list; reconcile).
- **Merge target bloat.** Folding startup-probes + sample-presets into
  adapter-contract.md (already the largest ref) — does that over-grow one file?
- **Route targets.** Confirm the 5 route targets are the right anchor (and won't
  trip the body headroom ratchet if routed from the body vs the dispatch).
- **Apply discipline (the load-bearing lesson):** every route/merge edits SKILL.md
  References + dispatch + possibly tests; run validate_skills + check_skill_contracts
  + the quality docs tests + doc-links + dup-ratchet, and adversarially verify each,
  exactly as the pin sweep did. A "route-it" that moves a test-pinned phrase must
  move its test too.
