# Spec: Generalize author-time shape-preflight + de-launder the disposition escape

Status: approved (Slice-1 fresh-eye critique returned SHIP-WITH-CHANGES; all
must-fix findings folded below — see `## Slice-1 critique resolution`)
Created: 2026-06-08
Goal: `charness-artifacts/goals/2026-06-08-authoring-preflight-and-disposition-delaunder.md`

This is the design contract the goal's Slice 1 must produce and a fresh-eye
critique must SHIP before any Slice-2/4 code. It resolves the two open design
fronts — the preflight generalization shape and the de-launder mechanism — and
records how each respects its hard guardrail.

## Problem (the recurrence engine)

The loop #284 → #308 → #325 → #329 → #332 → #334 keeps re-filing the same
"authoring-preflight skip" class. Two structural causes:

1. **Author-time shape is not reached at the author boundary.** The
   `check_skill_surface_preflight.py` preflight covers *skill-surface* edits only.
   The artifact-shape validator family (`validate_critique_artifacts`,
   goal closeout-evidence, `validate_retro_artifact`, `validate_debug_artifact`,
   `validate_ideation_artifact`, `validate_quality_artifact`,
   `validate_handoff_artifact`) runs **only in the broad gate / surface-match**,
   never at the commit boundary (verified: none of the 7 appear in
   `staged_commit_gate_plan.py`). So a hand-author's *first* shape signal is a
   late broad-gate failure (#334: hand-wrote a critique, omitted
   `## Reviewer Tier Evidence`, cost a second ~45s gate run). Note: six surfaces
   *do* have a `scaffold_*_artifact.py` (critique's round-trip-passes its
   validator today) — but the scaffolds are **uncited** in the skills' authoring
   paths, so hand-authors never reach them. The gap is *reach at the author
   boundary*, not total absence of a shape source.
2. **`issue #N` is the cheapest disposition.** The disposition floor accepts
   `applied:` / `issue #N` / `none — <reason>` by *form*. Re-filing a recurring
   finding as a fresh narrow issue is well-formed, so each recurrence laundered
   itself into a new closed issue while the general fix never landed.

## Hard guardrails (Non-Goals these must not violate)

- **G1 — no content classifier in the deterministic floor.** Achieve's own
  cardinal rule: the deterministic floor proves a *review ran* / a *field is
  present*; the reviewer/human judges *substance*. The de-launder must not make
  the floor decide whether a finding "is really recurring."
- **G2 — non-discretionary, not another doc.** #332 already proved discoverable
  docs + memory do not stop the skip. Workstream-1's fix must be auto-run
  behavior at the author boundary; a doc may accompany it but is not it.
- **G3 — behavior-preserving (precise).** No validator's pass/fail *judgment* on
  any artifact changes, and no new shape requirement is added. The commit-boundary
  gate only **relocates an existing validator's verdict earlier**; the dispatcher
  reads shape from the validators/scaffolds and never re-declares it. (A commit
  that the broad gate would have failed may now fail earlier — that is relocation,
  not a verdict change.)

## Design A — generalize the author-time shape preflight (workstream 1)

### A1. A general dispatcher with a family registry

New `scripts/check_artifact_surface_preflight.py`. Its core is a `REGISTRY`
mapping each hand-authored artifact surface to its owning validator invocation
and its scaffold script (where one exists). The registry IS the generalization:
one place that knows the artifact-authoring family, instead of N disconnected
validators. Initial members (the in-class family, from `run-quality.sh`):

Each row declares a **shape source** the dispatcher delegates to — either a
`scaffold` script (stub-by-construction) or `validator-constants` (read the
validator's declared required-shape constants; for goal-closeout the goal
*template* already seeds the `## Final Verification` block, so shape is present by
construction without a scaffold script). The dispatcher handles both kinds; the
registry never promises a scaffold a row does not have.

| Surface | Validator | Shape source |
| --- | --- | --- |
| `charness-artifacts/critique/*.md` | `validate_critique_artifacts.py` | scaffold: `scaffold_critique_artifact.py` |
| goal `## Final Verification` closeout-evidence | `check_goal_artifact.py` (closeout-evidence) | validator-constants (`CLOSEOUT_EVIDENCE_NAMES`, `DISPOSITION_REVIEW_EVIDENCE`, `NARRATION_REQUIRED_SECTIONS`) + goal template seeds the block — **no scaffold script** |
| `charness-artifacts/retro/*.md` | `validate_retro_artifact.py` | scaffold: `scaffold_retro_artifact.py` |
| debug artifact (adapter-scoped) | `validate_debug_artifact.py` | scaffold: `scaffold_debug_artifact.py` |
| `charness-artifacts/ideation/*.md` | `validate_ideation_artifact.py` | scaffold: `scaffold_ideation_artifact.py` |
| quality artifact (adapter-scoped) | `validate_quality_artifact.py` | scaffold: `scaffold_quality_artifact.py` |
| handoff artifact (adapter-scoped) | `validate_handoff_artifact.py` | scaffold: `scaffold_handoff_artifact.py` |

### A2. Shape is READ, never re-declared (zero drift, respects G3)

The dispatcher never re-states required sections/fields. It surfaces shape from
the row's declared shape source:

- **`--path <artifact>` / `--type <kind>`**: print the required shape from the
  row's shape source — a scaffold's stub headings (scaffold rows) or the
  validator's declared shape constants (validator-constants rows) — and/or run the
  owning validator against the file to surface concrete missing-section gaps. The
  output is the validator's/scaffold's own words.
- **`--emit-stub`**: for scaffold rows, delegate to the owning scaffold to write a
  starter stub so the required shape is present *by construction*. For the
  goal-closeout row there is no scaffold script; the goal template already seeds
  the `## Final Verification` block, so `--emit-stub` is a no-op there and the
  dispatcher says so explicitly rather than implying a stub it cannot write.

If a scaffold or validator changes its required shape, the dispatcher's output
changes with it — no second declaration to drift. (Scaffold↔validator round-trip
— scaffold output passes its validator — is asserted by a test in Slice 2;
critique's already passes today.)

### A3. Non-discretionary wiring — TWO arms (respects G2)

The critique (SC-1) proved a single exit-0 advisory is doc-equivalent — the exact
G2 trap (#332). The real `check_skill_surface_preflight.py` precedent is a
*blocking* `STRUCTURAL_SWEEP_LABELS` member in `staged_commit_gate_plan.py`,
fail-fast and enforced by `.githooks/pre-commit`. So G2 is carried by TWO arms,
deliberately, not by an ignorable advisory:

- **Arm 1 — blocking commit-boundary relocation (`--changed-artifacts <paths…>`):**
  for each changed `charness-artifacts/**` artifact, the dispatcher uses the
  registry to find the owning validator and runs it *early*. This is wired as a
  **blocking structural-sweep member** (a new label in `STRUCTURAL_SWEEP_LABELS`,
  the same tier as `check-skill-core-headroom (staged)`), so it fails fast at the
  commit boundary / `run_slice_closeout.py --predict-commit`. It runs the *same*
  validator with the *same* verdict — only earlier (G3-precise: relocation, not a
  new requirement). The author sees "critique artifact missing
  `## Reviewer Tier Evidence`" at the cheap commit step, not at broad-pytest
  minute 6.
- **Arm 2 — shape-by-construction at create time:** cite/route
  `scaffold_critique_artifact.py` from the `critique` skill's documented authoring
  path (it exists but is uncited — the #334 root cause), so a fresh critique
  artifact starts shape-correct. For the goal-closeout proving instance, shape is
  already seeded by the goal template; the dispatcher's `--type goal-closeout`
  surfaces the closeout-evidence constants so the author sees the required
  evidence names before authoring.

Docs (`authoring-preflight.md`) are updated to point at the dispatcher, but the
doc is the accompaniment; the **blocking commit-boundary gate + shape-by-
construction** are the fix.

### A4. Behavior-preserving under the precise G3

The dispatcher and the new commit-boundary member add **no new shape requirement**
and change **no validator's pass/fail judgment** on any artifact. Arm 1 blocks a
commit only when the owning validator would *already* fail that artifact in the
broad gate — it relocates that existing verdict earlier. The dispatcher reads
shape from the registry's shape sources and never re-declares it, so there is no
second source to drift. Proof obligations: a before/after verdict-equality check
on a corpus of existing artifacts (Slice 2/3) and the touched validators' own
tests.

## Design B — de-launder the disposition escape (workstream 2)

### B1. Mechanism: presence-only lineage field (rung 1d) + rung-2 substance

Chosen from the axis {presence-only lineage field / strengthen rung-2 /
filing-time dedup in `issue` / combination}: **presence-only field + rung-2**.
Rejected as *primary*: filing-time dedup in `issue` (heavier, needs a recurrence
index, and "does this match a recurring class" at filing time is again a
substance call better left to the reviewer — recorded as a deferred follow-up).

- **Rung 1d (deterministic, presence/enum only):** every `## Auto-Retro`
  disposition whose form is `issue #N` must additionally carry a
  **recurrence-lineage marker** — one of `recurs:` / `recurrence:` / `lineage:` /
  `novel:` followed by non-empty content. Examples:
  - `issue #335 (novel: searched #284/#308 lineage — distinct class, no match)`
  - `issue #335 (recurs: #284 → #308 → #325 → #329 → #332 → #334)`

  **G1 boundary, stated explicitly (per critique Q1):** the floor checks exactly
  `marker ∈ {recurs, recurrence, lineage, novel} AND value-after-separator
  non-empty`, full stop. It never inspects the value's *correctness* — it does not
  check that a `recurs:` lineage resolves to real issue numbers or that a `novel:`
  claim was actually searched. Any such correctness check is rung-2's and must
  never migrate into the floor. This is identical in kind to rung 1c (the form
  floor) and to `issue/validate_proposal_fields.py`'s `Destination` enum — a
  presence/enum check, not a classifier (respects G1).
- **Rung 2 (fresh-eye reviewer, substance):** the disposition reviewer is
  instructed to FALSIFY a `novel:` assertion — search the recurrence lineage and
  decide whether the disposition is actually a re-file of a known recurring class.
  Substance judgment lives here, where it is allowed.

The split is the resolution of G1: **deterministic presence (the marker exists)
vs fresh-eye substance (the marker is true)**.

**Honest division of value (per critique SC-4/Q3).** The floor cannot catch the
real laundering case — a *false* `novel:` — only rung 2 can. The marker's only job
is to force the author to commit to a single *falsifiable* claim type that rung 2
then audits; it is a forcing function, not a filter. It is required uniformly on
every `issue #N` disposition (never on `applied:`/`none —`); uniformity is
deliberate, because deciding *which* issue dispositions "look recurring" would be
the classifier G1 forbids. Some rote `novel: first-time` boilerplate is the
accepted cost. If boilerplate ever becomes the failure mode, the response is to
strengthen rung 2's falsify instruction — **never** to enrich the floor.

### B2. Where it lives (scoping, respects G3)

- The lineage-marker grammar (`has_recurrence_lineage(value) -> bool`,
  presence/enum only) is added to the shared `scripts/disposition_form.py` so the
  grammar has one source.
- It is *called* only from a new `apply_recurrence_lineage_floor` rung in
  `skills/public/achieve/scripts/goal_artifact_disposition.py`, scoped to the
  goal `## Auto-Retro`. The retro validator keeps calling the shared module's
  existing `is_form_enforced`/`invalid_dispositions` only (verified:
  `validate_retro_artifact.py` imports just those), and the new function is purely
  additive, so **existing retro verdicts are unchanged by construction**. Slice 4
  adds a regression test asserting retro verdicts on a fixed corpus are
  byte-identical after the shared-module addition (insurance: the function now
  lives in a file retro imports).
- **Known open escape (named) — RESOLVED in Slice 6.** Scoping B to achieve
  `## Auto-Retro` first left a partial gap: a recurring finding could launder
  through a standalone retro's `## Next Improvements` `issue #N` line. The
  done-early continuation (Slice 6) closed it: `validate_retro_artifact.py` now
  calls the shared `has_recurrence_lineage` via `validate_recurrence_lineage`,
  enforce-from 2026-06-09 (every existing retro is dated on/before the landing day,
  so all are grandfathered and the broad gate stays green). The shared-grammar
  design made this the one-line follow-on it was predicted to be.

### B3. Grandfather + dogfood

- New `RECURRENCE_LINEAGE_RULE_DATE = 2026-06-08`. Goals Created on/after it are
  in scope; earlier goals are grandfathered; an undatable goal fails closed —
  mirroring every existing rung exactly.
- This goal is Created 2026-06-08, so it is **in scope**: its own Auto-Retro
  `issue` dispositions must carry lineage markers and pass rung 1d, and its
  disposition review must falsify any `novel:` claim. If this goal's closeout
  cannot pass under the new rule, the rule is wrong (mandatory dogfood).

## Success criteria (what Slices 2–5 must prove)

- Authoring the #334 surfaces (critique artifact, goal closeout-evidence)
  surfaces/stubs required shape at author time, pre-gate (Design A).
- A sibling-coverage report enumerates the family with before/after author-time
  coverage and fixed/out-of-class status (Slice 3).
- A contrived "re-file a known recurring class as a fresh narrow issue" is caught
  by rung 1d (missing lineage marker) and/or rung 2 (falsified `novel:`), with
  the deterministic floor provably NOT classifying content (Design B; Slice 4).
- This goal's own closeout passes under rung 1d (dogfood).
- Existing gate verdicts unchanged; mirror byte-synced; touched validators'
  tests green.

## Slice-1 critique resolution

A fresh-eye reviewer (different agent context, read-only) returned
**SHIP-WITH-CHANGES**. All must-fix findings are folded above; the open questions
are resolved:

- **Q1 (G1 / self-classify):** Not a classifier — the floor checks marker presence
  + non-empty value only, never correctness. The explicit G1 boundary is now
  stated in B1. The caveat (never check value correctness in the floor) is
  recorded as a hard line.
- **Q2 (A3 non-discretionary vs doc):** The original exit-0 advisory WAS
  doc-equivalent. Fixed: A3 now carries G2 with TWO arms — a *blocking*
  structural-sweep commit-boundary member (the real skill-preflight precedent
  tier) + shape-by-construction (cite the scaffold). Both, not an advisory.
- **Q3 (rote `novel:` boilerplate):** Accepted cost; the floor is a forcing
  function for a falsifiable claim, all substantive value is rung 2, escalation
  strengthens rung 2 never the floor. Stated in B1 "Honest division of value."
- **Q4 (achieve-only scope):** Correct minimal blast radius; the standalone-retro
  laundering path is now named as a known-open escape (B2) and a deferred
  decision, not silent.
- **Q5 (new value vs 5-min-earlier):** Genuinely new — the artifact validators are
  NOT at the commit boundary today, so the author's first signal moves from a late
  broad-gate failure to the cheap commit step. Stated in the Problem section.

Verified-safe by the reviewer (no action needed beyond the noted tests): the
critique scaffold round-trip-passes its validator today; retro isolation holds by
construction (Slice-4 regression test is insurance); the registry reads shape and
never re-declares it.

### Factual corrections applied

- Problem §1 no longer claims "no author-time shape help"; it states the accurate
  gap (no commit-boundary reach + uncited scaffolds).
- A3 no longer claims the advisory is wired "exactly where" the skill preflight is
  with the same effect — it now matches the real *blocking* tier.
- The registry no longer implies every row has a scaffold; goal-closeout is marked
  validator-constants + template, no scaffold script.
- G3 restated precisely (relocation of an existing verdict, no new requirement).
