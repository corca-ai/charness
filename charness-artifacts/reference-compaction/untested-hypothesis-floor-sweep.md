# Untested HYPOTHESIS-floor sweep — census-anchored worklist (2026-07-02)

Design output for the reference-compaction Slice-7 chunk "correctness sweep of the
untested HYPOTHESIS floors" (#410 / handoff Next-Session). Produced with **zero
captures** — census-first, the method the reconciliation locked
(`slice7-census-reconciliation.md`: census bucket first, capture to VERIFY, never
decide a floor from a capture alone).

## Scope: the 7 never-captured default floors

The reconciliation's 13-floor pass covered the INLINE/DUP contested floors of the
already-swept skills (hotl, critique, gather, setup, handoff). This chunk covers a
DIFFERENT set: the `fan_out_fit: no` skills whose default `spec.json` floor has
**no capture bundle at all** (`charness-artifacts/cautilus/` has none), so the RCF
doc-open floor is an untested HYPOTHESIS. Deterministically enumerated:
`announcement, create-skill, find-skills, ideation, narrative, release, spec`.
(The other 8 `fan_out_fit: no` skills — achieve, create-cli, debug, hitl, hotl,
impl, quality, retro — have ≥1 capture and are out of this chunk.)

## Census-anchored verdicts (RCF ref → census bucket)

| skill | RCF (current spec.json) | census bucket(s) | class | designed action |
|---|---|---|---|---|
| announcement | `draft-shape.md` | INLINE | REFUTED-class | retire the doc-open; floor on an emitted-token RSF or substance |
| ideation | `concept-architecture.md` | DUP | REFUTED-class | retire; floor on RSF/substance |
| narrative | `brief-shape.md` | INLINE | REFUTED-class | retire; floor on RSF/substance |
| create-skill | `portable-authoring`, `adapter-pattern`, `integration-seams`, `runtime-capabilities` | INLINE, INLINE, **DEPTH**, INLINE | MIXED | retire the 3 INLINE; keep/verify `integration-seams.md` (DEPTH) as the floor |
| release | `version-policy`, `critique-boundary`, `publication-boundary` | **DEPTH**, INLINE, **DEPTH** | MIXED (+`coverage_floor_risk: True`) | retire `critique-boundary.md` (INLINE); keep the 2 DEPTH; investigate the census-flagged coverage-floor risk |
| spec | `design-lenses`, `evidence-durability` | **DEPTH**, INLINE | MIXED | retire `evidence-durability.md` (INLINE); keep/verify `design-lenses.md` (DEPTH) |
| find-skills | `discovery-order.md` | DEPTH | genuine DEPTH | design already correct; **verify-only** capture (no spec edit expected) |

## Honest caveats — this is a first pass, not a verdict lock

Per the reconciliation's METHOD CORRECTION, a census cross-check is a **starting
point**, not the final floor decision. Two failure modes still need per-skill work
before any spec flip:

1. **Missing-scenario mis-read (gather's lesson).** For a script/condition-driven
   skill, "the census says INLINE / the run opens 0 docs" can mean a *missing
   scenario*, not a dead floor. Before retiring a REFUTED-class RCF, trace the
   skill's routing (planner/adviser) for a condition that genuinely forces the doc
   under some scenario — if one exists, design that scenario (gather's private-SaaS
   pattern), do not retire.
2. **Census may under-count DEPTH (MIXED, step-4).** An INLINE-bucketed ref can carry
   a genuine on-demand DEPTH slice absent from SKILL.md (hotl/ledger pattern). Verify
   the gist is actually inlined before retiring; if a real DEPTH slice remains, keep a
   doc-open floor on that slice.

## Batched ask-before-run capture queue

Each floor move is **capture-before-pin** — no RCF flip / RSF pin ships before its
verifying capture (`claim_fidelity_lib` also forbids DUP/INLINE-tagging a live RCF
floor, so the tag/RCF flip is coupled to the proven replacement). Accumulate and run
in ONE authorized ask-before-run Cautilus session (`scripts/run_cautilus_eval.py`,
never bare `cautilus evaluate`; gate via `scripts/plan_cautilus_proof.py`):

- **gather (public-URL, #411 remainder)** — READY: substance floor shipped
  (`outcome-assertions.json`, commit `3b650cb6`). Capture-session steps: inline the
  Access-Modes enum into gather SKILL.md (**also resolve the `mode_option_pressure_terms`
  ergonomics gate the enum trips** — 2 terms pass, 3 fail), drop the INLINE RCF
  (`source-priority.md`, `capability-contract.md`), capture to prove the substance floor.
- **REFUTED-class (announcement, ideation, narrative)** — after the missing-scenario
  trace: retire the RCF, pin an OBSERVED RSF token or add an `outcome-assertions.json`;
  capture to prove the replacement (token OBSERVED, never assumed).
- **MIXED (create-skill, release, spec)** — inline the INLINE gist, retire that RCF
  member, keep the DEPTH member; capture to prove the DEPTH is genuinely opened.
- **find-skills** — verify-only capture that `discovery-order.md` is opened.

## Provenance

- Enumeration: registry `fan_out_fit: no` ∩ (no `charness-artifacts/cautilus/*` bundle).
- Buckets: `census.json` `per_skill[].references[].bucket` (the audit of record).
- Method: `slice7-census-reconciliation.md`, `gather-fixture-redesign.md`.
