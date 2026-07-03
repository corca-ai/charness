# Rationale-Accuracy Audit — INLINE-ref spec rationales (2026-07-04)

Serves [intent.md](./intent.md) §"the reference is meaningfully used" and the handoff
Next Session **1b**. Question audited: for every `classTag: INLINE` ref, does its
`referenceEngagement[<ref>].rationale` in `evals/cautilus/<skill>-claim-fidelity/spec.json`
**accurately** describe what the SKILL.md body *actually* inlines vs. what stays doc-only?
The defect class was proven last session on `spec/success-criteria.md` (rationale claimed the
body inlines "heart of the spec / observable / bounded" — grep said no).

## Method

Grep-verify, not proxy metric. A 15-way auditor fan-out (one per INLINE ref) decomposed each
rationale into content + location claims and checked them against the authoritative
`skills/public/<skill>/SKILL.md` body (concept-level, not literal-string); every flagged
mismatch was then hit by an **independent adversarial skeptic** (default: auditor is wrong,
hunt the concept under other words) before any edit. All confirmed fixes were re-verified by
hand against source, then a fresh-eye bounded critique re-checked the rewrites and the
no-change calls. Population = 15 INLINE refs; one auditor (`spec/fixed-probe-defer.md`) died on
the StructuredOutput cap and was audited by hand.

## Result: 4 fixed · 1 flagged-but-refuted · 10 accurate

**Fixed (rationale over-/mis-claimed; body verified):**
- `achieve/coordination.md` — framed an INLINE ref as a "required-for-understanding" forced-open
  doc and anchored evidence on a **sibling** ref (`lifecycle.md` 317-328); never stated the gist
  is inlined in the body. Rewritten to the real body anchors (`## Coordination` 128-137,
  `## Coordination Cues` 151-154) + doc-only depth. (The spec's own `_comment` already stated the
  correct demotion basis — the per-ref rationale was the drifted surface.)
- `announcement/adapter-contract.md` — step-4 enumeration listed `in_progress_sources` (a **step-2**
  field, line 85) and dropped `public_body_shape` (a real step-4 field). Relocated.
- `impl/review-gate.md` — listed "contract re-read" as doc-only / stronger-gate-gated depth, but the
  body already inlines it at **step 5** (134-136) and the doc's `## Contract Re-read` is a standalone
  section, not nested under `## Stronger Gate`; also mislocated the contract-honesty lens to step 6.
- `spec/fixed-probe-defer.md` — said "step 2 names this 'the core discipline for spec'"; that phrase
  is the **doc's** line 3, not step-2 body text, and "verbatim" overstated a faithful gist. Conclusion
  (INLINE) was right; tightened for same-pass consistency (fresh-eye critique caught the miss).

**Refuted (flagged, then adversarially cleared — no change):**
- `create-skill/adapter-contract.md` — the 5-term parenthetical is explicitly attributed to the doc
  ("that adapter-contract.md defines"); step 4 says "topology vocabulary … shared implementation vs
  intentional fork" and 4/5 terms are verbatim in the body. Rationale stands.

**Accurate (10):** create-skill `binary-preflight`/`preset-conventions`, `critique/counterweight-triage`,
`debug/five-steps`, `find-skills/session-start-routing`, impl `contract-consumption`/`design-lenses`/
`sequence-discipline`, `narrative/adapter-contract`, and the control `spec/success-criteria` (last
session's fix holds).

## Lesson

The over-claim class is narrow and mostly closed: only ~27% of INLINE rationales drifted, and the
drift is **locator/attribution** (wrong step, sibling-ref anchor, phrase attributed to body that
lives in the doc), not fabricated gist — the census's INLINE calls themselves were all sound
(0/15 mislabeled the inline-vs-doc-only boundary). `validate_claim_fidelity_specs.py` cannot see this
class (it checks structure, not whether the prose matches the body), so accuracy stays a
judgment audit. A cheap future guard: a locator lint that flags rationale step/line cites whose named
step title or line range does not contain the claimed token.
