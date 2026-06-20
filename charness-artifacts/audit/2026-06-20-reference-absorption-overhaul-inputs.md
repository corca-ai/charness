# Reference Absorption — North-Star Overhaul Inputs (2026-06-20)

Read-only mining of **../matt-skills** (Pocock skills + `writing-great-skills`)
and **../craken** + **../craken-agents** (specdown/Alloy, mutation-testing,
quality-exceptions) for patterns the north-star overhaul should absorb. Baseline
discipline (the lychee lesson): only a genuine net improvement over charness's
*existing* surface counts; convergent confirmation is a citation at most.

Source run: dynamic workflow `wf_48b104e0-56d` (5 miners + synthesis). Extends
the craken-agents pass-1 note (`2026-06-20-craken-agents-absorption-pass-1.md`)
and feeds the Phase-2/3 design alongside the
[Phase-0 back-test](./2026-06-20-north-star-phase0-diagnosis-backtest.md) and the
cluster-survey (`wf_f03ba5fe-62d`).

**Bottom line:** mostly convergent (charness already holds the doctrine at
equal-or-better), with a small sharp net-new core. The honest risk is
over-importing matt's full authoring glossary — graft the tests, skip the
vocabulary.

Baseline checks (verified, not asserted): 8 of 21 public SKILL.md bodies sit at
197-200 lines, median ~190, against a 200 cap treated as a target.
`portable-authoring.md` Named Anchor Rule (L139-172) is strictly real-person-only.
`mutation-testing.md` operates at score/blocking-signal altitude only.
`lint-ignore-discipline.md` already has reviewed-date + per-finding justification
(so `Last audited:` is convergent, not net-new). `issue/SKILL.md` has no
AI-provenance marker on posted comments. North-star P4 already owns
distinct-channel + distinct-observer at irreversible boundaries.

## Net-new adoptions (do these)

1. **No-Op deletion test** (P2) — model-relative, sentence-by-sentence: "does
   this line change behaviour vs the model's default? if not, delete the whole
   sentence (do not reword); settle by running the skill, not debating." The
   operational missing half of P2. → Phase 3 audit + skill-ergonomics Review
   Questions.
2. **Three length-causes** (P2) — sediment (prune) / duplication (single source
   of truth) / sprawl (disclose-split). Diagnosis-before-cure step in the Phase 3
   audit. Also the R1 rung-1 de-dup diagnostic (de-dup = the duplication cure).
3. **Leading Word Rule** (P3) — generalize Named Anchor (person-only) to: one
   repeated pretrained token (tracer bullet, tight, red) over a restated phrase or
   a do-not list; person-name is one species; a coined word recruits no priors.
   Primary P3 compression + do-not-list reducer.
4. **Survivor disposition trichotomy** (P5) — `mutation-testing.md` gains a
   ~10-line subsection: each survivor ends killed / equivalent-because-X (one-line
   proof) / defer-because-Y, never tautological-kill or silent-tolerate; one
   stack-neutral worked case (count(*)/coalesce always returns one row → the
   row-undefined optional-chaining mutant is unreachable → record equivalent).
5. **Re-audit-by-removal** (P4) — lint/dup/boundary exemption contracts gain:
   toggle the exclusion off, re-run, record the real surfaced count; keep only
   with that proven number, delete in the same pass if zero or a real owner now
   absorbs it. Executes the standing *claim* through a different channel.

## Phase 3 style deltas (matt structure / terseness / example)

- **Body altitude**: 200 is a ceiling not a target; 195-200 is a bloat signal to
  audit. Ask "smallest body that equips the judge", not "under 200".
- **Named heuristic over enumerated do-nots**: impl 21 / quality 15 /
  create-skill ~30 / hitl 18 / handoff 17 negative bullets. Collapse 3+ that
  restate one principle into one named heuristic; success = negative-directive
  count falling.
- **Load-Bearing Anchors is the flagship bloat case**: quality's section fuses
  routing decisions with 10+-script comma-lists; split into one-sentence move +
  roster-in-reference. Convention: an anchor needing commas for >3 nouns is a
  catalog, belongs in a reference.
- **Show one instance**: cores carry only bootstrap bash; spend reclaimed budget
  on one worked instance (sample falsifiable hypothesis, sample closeout) before
  another guardrail. `portable-authoring` already does this for "Agent failure
  modes" — extend it.
- **_Avoid_ line** sparingly on coined load-bearing terms (north-star's
  irreversible/reversible) as duplication prevention.
- Optionally consolidate items 1-3 into one short `authoring-vocabulary`
  reference IF it stays well under cap; else graft directly.

## R1/R2 consolidation deltas

- **R2 net-new wire**: AI-provenance marker on the body of any agent-posted
  GitHub comment/issue — the irreversible external write must be legible to the
  distinct observer P4/#386 require. (craken's done/failed external-visible
  disposition is convergent reinforcement of the R2 shape.) Reproduce-first-before-fix
  is a lighter add to issue's causal review, not the distinct-channel wire.
- **R1**: three length-causes is the de-dup diagnostic; classify by cause so
  de-dup hits real duplication and does not strip sprawl/sediment.
- Keep formal-model / survivor-disposition / remove-and-count OFF the R1/R2 scope
  (they land on quality references).

## Convergent confirmation only (doctrine citation at most, no change)

- matt router + context/cognitive-load: charness public/support split +
  find-skills already ARE this at repo scale.
- matt grilling / handoff / teach: charness ideation/handoff/info-hierarchy
  strictly stronger.
- craken label lifecycle / few-cases-long-scenarios / fail-loud gate /
  skill-creator: charness issue / specdown-quality / standing-gate-verbosity /
  create-skill already equal-or-better.
- craken inline retrospective: charness deliberately routes lessons to a wired
  `recent-lessons` digest; inline accretion re-introduces the rot charness escaped.
- matt completion two-axes at irreversible boundaries: P4/P5 already stronger.

## Deferred / low-priority

- craken Alloy formal/exhaustive-within-scope layer for public-spec-layering:
  genuinely net-new as a non-execution P4 channel, but opt-in and niche (most
  charness repos never need it). Park as a deferred decision; flag only if a repo
  keeps a large invariant/state-machine surface.
- matt reversible-step completion-criterion clarity/demand vocabulary: graft only
  if Phase 3 finds reversible-step skills with fuzzy bounds; do not import the
  full vocabulary.

## Addendum — bug-hunt + better-UT arrived (2026-06-20)

The craken-pass-1 "pending share" external skills (`bug-hunt`, `better-ut`)
arrived from the operator (creator's own caveat: not carefully made). Evaluated
per-surface under the same baseline discipline (two read-only agents).

- **bug-hunt → MOSTLY-CONVERGENT, no absorption.** charness `debug` holds the
  same workflow at higher resolution (falsifiable-hypothesis-first, durable debug
  artifact, RCA ledger, detection-gap, sibling-search, P4/P5 provisional-success);
  what bug-hunt lacks (durable memory, prevention) is exactly charness's
  differentiator. One thin optional candidate — a "no band-aid / symptom-patch"
  line in `debug/references/anti-patterns.md` — is held back under P3 (the
  five-whys *principle* over an enumerated don't-list). Net: confirmation.
- **better-UT → MOSTLY-CONVERGENT + one genuine narrow gap.** charness has **no
  standalone per-test-body unit-test-quality authoring doctrine**; its test
  surface is suite-level (economics / mutation / dup-ratchet /
  testability-and-selection). Charness is equal-or-better on ~6 of ~9 clusters
  (refactor-for-testability, DSL/fixture discipline, external-API mocking,
  don't-chase-coverage, smallest-surface, workflow scaffold — SKIP all). The gap
  is a missing *layer*. **Adopt:** one new
  `skills/public/quality/references/unit-test-quality.md` grafting only patterns
  (1) determinism harness (clock/random/tz/locale/ids/ordering; fake timers over
  sleep; in-memory/temp isolation; order-independence), (2) properties/invariants
  *in the test* (idempotence, round-trips, normalization, immutability /
  no-mutation-of-caller-owned-data, preservation of unrelated fields), (3)
  observable-contract-over-private-mechanics + one-reason-to-fail + explicit
  assertions over snapshots, (4) real-collaborators-by-default for *in-process*
  code (charness only states this for external provider APIs), (5)
  map-behavior-before-testing + negative/edge-case menu, and (6) **fixture/DSL
  *authoring* principles** — plain-literals-until-repetition-hides-intent;
  defaults valid/minimal/visible (override only scenario-relevant fields); avoid
  fluent chains that obscure cause/effect; small named helpers over a clever
  grammar. Constraints: under cap, P3 principle-over-rulebook, one worked example
  per pattern, **not** better-UT's do-not lists / glossary / workflow; route from
  the Behavior lens in `quality-lenses.md`, sit *below*
  `testability-and-selection.md` (avoid the dup-ratchet two-references-one-concept
  trap). Lands in overhaul **WS-B**.
  - *Pattern 6 boundary (operator-surfaced, verified):* charness's
    `testability-and-selection.md:121-170` already owns the test-DSL **review**
    lens (is the DSL hiding untestable structure? are assertions still visible at
    the `.test` site?) and is *stronger* there — keep that convergent/SKIP. The
    gap the eval over-merged is the stack-neutral **authoring** principles, which
    `:168-170` explicitly declines ("`quality` does not author a stack-specific
    DSL; consumer repos build their own"). Graft only the *principles*; charness
    still ships no stack-specific DSL implementation, so the existing boundary
    holds.

## Operator clarification (2026-06-20)

Progressive disclosure is the operator's **own core philosophy** — the wariness
is reference **sprawl/sediment** (too many, too bloated), not disclosure itself.
So the P2 framing is: disclosure is *endorsed* (push reference behind a
branch-reliable pointer); the guard is to apply the no-op test + the
three-length-causes **to references too**, and watch reference count/size — not
to keep overflow inline. This aligns matt's "context pointer wording decides
reach" with charness's "displaced overflow goes unread": both fail on sprawl, not
on disclosure.
