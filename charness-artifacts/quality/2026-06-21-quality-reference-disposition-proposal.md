# Quality reference disposition — DRAFT PROPOSAL (2026-06-21)

**STATUS: EXECUTED 2026-06-21.** The draft below is preserved as the pre-critique
map. The adversarial fresh-eye critique ran and the approved (corrected)
disposition was applied — see `## EXECUTED` at the end for the critique outcome,
the corrections it forced, and the verification. Next step is the empirical
Cautilus validation in the LOCKED plan, not re-applying this draft.

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

## LOCKED next-session plan (operator-agreed 2026-06-21)

Sequencing: **fix the wrong parts first, then empirically validate** — do NOT
restructure on theory.

1. **Execute only the approved disposition fixes** (5 route-it + 2 merge above),
   each under the pin-sweep apply-discipline (validate_skills + check_skill_contracts
   + quality docs tests + doc-links + dup-ratchet; adversarial verify each; a moved
   test-pinned phrase moves its test). Critique this proposal first.
2. **Then run the empirical "does the skill actually operate as intended" test** on
   the post-fix skill.

### Rejected / settled
- **Do NOT move bootstrap refs to `setup`.** quality's bootstrap = resolving its
  OWN adapter/artifact/evaluator; `setup` = repo operating-surface bootstrap.
  Same name, different concept — moving it creates cross-skill coupling (routing
  maze) and is count-chasing relocation, not improvement. (Audit already found
  quality↔setup boundary crisp, split=0.)
- **The lever for "operate as intended" is ROUTING quality, not ref count.** A
  healthy run loads body+dispatch then lazy-pulls ~3–5 in-scope refs, never all
  41. The 5 route-it fixes directly improve this. "Fewer refs" is NOT the goal.

### Empirical validation design (corrected — Cautilus DOES evaluate process)
Verified against cautilus 0.15.4 / `../cautilus`: `cautilus evaluate skill-experiment`
takes `sourceCoverageObligations` (id, ref, required) + `rubricPhrases` and the
baseline/variant `sourceRefs`, and emits `source_coverage_delta` + `rubric_match`
+ `baseline_vs_variant_delta` + `promotion_recommendation` (promote/revise/discard).
So Cautilus CAN score whether a run meaningfully used the required references.

- **Instrument:** Cautilus does NOT run/trace the skill itself — a host runner
  executes baseline + variant and supplies each run's `sourceRefs` (captured from
  the run's actual reference reads / output citations). Cautilus scores coverage +
  rubric against obligations. So transcript ref-capture and Cautilus are
  complementary (transcript = input; Cautilus = the structured verdict).
- **Scenarios, not one run:** a few BLIND runs ("아무 말 없이" — no leading context)
  spanning the lenses (concept-heavy / CLI-shipping / security-heavy / skill-authoring
  repo). Per scenario, `sourceCoverageObligations` lists only the refs that SHOULD
  be in scope for THAT task — NOT all 41 (all-refs-in-one-run is an anti-goal; a run
  that pulls everything is a scoping red flag).
- **A/B:** use baseline (current 41-ref skill) vs a variant (post-fix, or a
  deliberately leaner ref set) to get `baseline_vs_variant_delta` + promote/revise/discard.
- **Honor eval-only:** ask-before-run; consult `plan_cautilus_proof.py`; refuse on
  `next_action: none`; route via `run_cautilus_eval.py`, never bare `cautilus evaluate`.
- **Decision rule (the load-bearing lesson, 3rd time):** a ref unused/uncovered must
  be unused ACROSS the relevant scenarios before it is even a candidate — and then it
  gets the SAME disciplined verification, never auto-delete. "Unused in one run" ≠ dead,
  exactly like "un-routed" ≠ dead and "test-pinned" ≠ valuable.

## EXECUTED (2026-06-21) — adversarial critique outcome + applied disposition

The LOCKED plan's step-1 critique ran as an adversarial fresh-eye dynamic
workflow (10 independent skeptics — 7 item-verifiers + the 3 named probes — →
synthesis). Verdict: **all 7 items sound on merit (4 approve, 3 revise; 0
rejected, 0 deletes confirmed).** The reframe held — every flagged ref earned
keep/route on content; the defect was discoverability, not bloat.

### Corrections the critique forced (all applied)
- **operability-signals** — the proposal's alternate "dispatch operability entry"
  does NOT exist (inventory-dispatch.md has no operability section). Routed ONLY
  from the body operability lens (SKILL.md step 4 operability bullet).
- **dual-implementation-parity** — the proposal's "concept lens" anchor routes
  zero per-detail refs and risks the body-headroom ratchet. Routed from
  inventory-dispatch.md Source Hygiene (beside `inventory_dual_implementation.py`).
- **startup-probes / sample-presets merges** — both REDIRECTED off the
  already-largest adapter-contract.md (503 lines). startup-probes' schema half is
  already verbatim in adapter-contract.md L229-240 and its defaults+guardrail in
  installable-cli-probes.md; only the standing-vs-release rationale survived
  (folded as a one-line `class`-field note) plus the doctor≠fast-startup guardrail
  (folded into installable-cli-probes.md). sample-presets' only unique survivor —
  the knip advisory-gating policy — folded into inventory-dispatch.md's dead-code
  prose (vulture is already in `presets/python-quality.md`). Both files DELETED +
  de-listed ("not a delete" was true of content only — the file is gone, the
  sentence relocates).
- **NEW 6th route-it: quality-lenses** — keep-bias probe found it flat-list-only
  with the identical discoverability defect the proposal already flagged. Routed
  from SKILL.md step 4.
- **7th route-it (consistency): lint-ignore-discipline** — the identical-state
  Source Hygiene sibling to brittle-source-guards (script routed, prose un-routed);
  routed beside its script in the same dispatch edit so the section stays consistent.

### Proposal-map honesty fixes (no skill mutation)
- **skill-quality ↔ skill-ergonomics:** dangling "reconcile" resolved as KEEP BOTH
  (load-bearing divergence: ergonomics owns the `inventory_skill_ergonomics.py`
  advisory contract; skill-quality owns the deterministic-gates/manual-findings
  lens; ~15 test files; merge is high-risk for zero concept gain). Routing need is
  already met — inventory-dispatch.md L62-64 carries a compact third copy of the
  review-question checklist.
- **security trio (npm/pnpm/uv):** drop "un-routed" — they ARE conditionally
  routed from inventory-dispatch.md ("plus the relevant package-manager reference").
  0-delete keep confirmed (genuine per-manager nuance; collapsing to one table
  forces loading all managers — the proposal's own anti-goal).

### Final applied tally
route-it **7** (5 original + quality-lenses + lint-ignore) · merge/retire **2**
(both retargeted, files deleted) · delete **0**.

### Verification — full pin sweep, green
validate_skills ✓ · check_skill_contracts ✓ · quality_gates pytest **2283 passed** ✓
· doc-links ✓ · dup-ratchet ✓ (no re-baseline — edited files are not scanned
clone-members) · plugin mirror synced.

### Residual (deferred, not blocking)
- operability-signals.md ↔ quality-lenses.md `## Operability` overlap is genuine
  lens-detail-vs-summary, not duplication; a future dedup pass could reconcile.
- Next per the LOCKED plan: empirical validation via `cautilus evaluate
  skill-experiment` (ask-before-run; consult `plan_cautilus_proof.py` first).
