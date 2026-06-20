# Retro — North-Star Overhaul Sweep (2026-06-20)

Mode: session. Goal: `charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md`.
Window: S0 (concept spec) → S1 (R2) → S2 (R1) → S3 (WS-B) → S4 (closeout).

## What Happened

Four slices against the per-unit-disposition consolidation + skill-redesign goal:

- **S0** authored + locked the shared rung-1/rung-2 concept spec; a fresh-eye
  critique returned PASS-WITH-CONDITIONS and caught an under-counted clone surface.
- **S1 (R2)** closed the primary escape: the standalone issue/PR-close path
  greened `status: verified` on `CLOSED`+form only. Wired a rung-1
  block-the-silent behavioral-verdict floor + an AI-provenance presence floor +
  the rung-2 observer, without adding a terminal-green gate.
- **S2 (R1)** collapsed the cloned rung-1 grammar (`parse_created_date` ×5,
  `is_floor_in_scope`, `section_span`/`section_body`) into one substrate; the
  strict→permissive swap was a tested deliberate behavior change.
- **S3 (WS-B)** grafted `unit-test-quality.md` + one lossless named-heuristic cure
  (find-skills); deeper body redesign deferred with cause after verification
  showed the cuts blocked or lossy.

## What Created Waste (and what caught it)

1. **Same-proxy re-read produced a false "pre-existing" confirmation (the #386
   trap, self-inflicted).** In S1 I "confirmed" the `validate_attention_state_visibility`
   failure was pre-existing by stash-testing with the *wrong* gate invocation
   (missing `--scan-root skills --scan-root-map`). Both stashed and unstashed runs
   failed identically — for the wrong reason — masking that my change added a real
   new violation. The fresh-eye reviewer caught it by running the gate the way the
   enforcement path runs it (a distinct channel). The overhaul's own doctrine
   validated itself on the overhaul.

2. **Shaving a capped body to dodge the cap (operator-caught).** In S3 I first
   compressed debug's bootstrap in place and lossily "de-duped" quality's catalog
   — the exact P2 anti-pattern the goal forbids ("fewer lines is not success").
   The operator caught it ("why did you compress?"). Both were reverted; one body
   was then cured properly (find-skills named-heuristic, lossless).

3. **The planning audits over-identified cuts.** The reference-absorption note's
   "flagship bloat case" (quality Load-Bearing Anchors) turned out to be a
   contract-pinned consumer/validator surface (11 tests), not extractable bloat;
   Agent-3's collapse candidates (impl critique bullets) were distinct rules, one
   CORE-pinned. The bodies are concept-dense — the Phase-0 back-test was right.

## Decisions That Mattered

- **Concept-first gating (S0 before any impl)** paid off: the rung-1/rung-2 split
  is the reusable abstraction that dissolved the R2 "judgment-only vs
  terminal-green" dichotomy and is now coded.
- **Distinct-channel verification of subagent claims** (re-grepping the clone
  counts; running gates the enforcement way) caught two real errors a same-proxy
  re-read would have shipped.
- **Reverting rather than forcing** the blocked body cuts kept the slice honest;
  delivering the clean graft + one verified cure + a documented deferral beats
  shipping shaves.

## Named-Lens Counterfactual

**Ousterhout (complexity):** the capped bodies' length is mostly *genuine concept
size*, not removable complexity — the right move was to stop cutting once
verification showed the concept was load-bearing, not to chase a line target.
A "deletion is the cure" reflex would have broken 11 tests; the lens that asks
"is this complexity essential?" said keep it.

## Next Improvements

- **Gate-failure triage must use the exact enforcement invocation.** A
  hand-rolled approximation of a gate command can false-confirm "pre-existing"
  and mask a real regression. (Transferable; recurs class: same-proxy re-read.)
- **A skill-body cut needs a pre-cut lossless+contract-safe check:** every
  removed phrase has a reference home AND no test/CORE-contract pins it, verified
  *before* cutting. WS-B instrument gap.
- **Bloat diagnoses are hypotheses to verify per-body, not mandates to cut** —
  carry this into the deferred follow-on body redesign.

## Sibling Search

The deferred body redesign (impl/debug/quality/achieve) is the transferable
follow-on: each needs per-body lossless+contract verification before any cut.
