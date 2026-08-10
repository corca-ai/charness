# Spec: the closeout floor × classification matrix

Date: 2026-08-10
Issue: `#586`
Status: ready to build — decided by operator ruling on 2026-08-10 after three
disconfirming probes; no further design decision is owed before implementation.

## Why this and not a scanner

`#586` ranked three candidate guards. All three mechanizable ones were measured on
2026-08-10 and every one has near-zero current findings:

| candidate | findings today | instances it would cover |
| --- | --- | --- |
| vocabulary parity across classification enumerations | **0** — all six values present in all five carriers | 1, 6 |
| declared-but-unread (name-reference scan) | 9 of 5,493 top-level functions (0.16%); the one read end to end was a superseded helper, not an inert check | 3 |
| fail-open optional guard (a `None`-default parameter gating a refusal, never passed in production) | **0** | 4, 5 |

Building any of them now means validating a guard against its own fixtures, which is
the failure the goal that filed `#586` recorded twice.

The one shape that keeps producing live findings is instance 2's: **a floor that
exists, is correct, and is wired to one carrier but not to the one the disposition
requires.** It recurred on 2026-08-10 at the policy layer, and a bounded review — not
a gate — caught it.

## The live finding this starts from

`evaluate_close_comment_floor` (`skills/public/issue/scripts/issue_close_comment_floor.py:105-115`)
composes six sub-checks: source preservation, behavioral verdict, HOTL dispositions,
AI-provenance, resolution critique, consolidation readback. **Each one's applicability
rule lives in a different module, and no surface states them together.**

The consequence, confirmed while closing `#514`/`#515`/`#518`: the `consolidated`
classification — the disposition built for won't-do closes — skips four of the six.
`issue_resolution_critique.CRITIQUE_REQUIRED_CLASSIFICATIONS` is
`("bug", "feature", "deferred-work")`, and `issue_verify_closeout_body.py:126,137-145`
states the skip in an **advisory that never blocks**. Reading five modules is currently
the only way to learn this.

Whether that skip is right is NOT this spec's question. That it is invisible is.

## What to build

### 1. The declared matrix

One artifact. Rows are floor ids; columns are `(classification, carrier)` pairs. Every
cell carries one of:

- `fires` — the floor contributes to the verdict for this pair;
- `skipped-by-design: <reason>` — deliberately not applied, with the reason that makes
  it deliberate;
- `not-applicable: <reason>` — the floor's own input cannot exist for this pair.

An empty or absent cell is a refusal, not a default.

Floors: `source_preservation`, `behavioral_verdict`, `hotl_dispositions`,
`ai_provenance`, `resolution_critique`, `consolidation_readback`, and the closeout
authorization probe. Classifications: the six in `issue_verify_closeout.CLASSIFICATIONS`.
Carriers: at minimum `commit-msg`, `close-with-comment`, `pr-body`, `direct-commit`,
`manual-fallback`, and the release family.

### 2. The validator, which must be BEHAVIORAL

**Do not grep.** For each `(floor, classification, carrier)`, call the real floor with
a fixture body constructed to fail that floor, and observe whether the failure reaches
the verdict. Compare the observation to the declaration; disagreement in either
direction refuses.

This is the load-bearing constraint of the whole slice. A grep- or import-based matrix
would itself be a check that never fires on the wired path — it would assert what the
code *says* rather than what the caller *gets*, which is the exact class `#586` names.
A matrix built the cheap way makes this issue worse, not better.

### 3. Exhaustiveness

The matrix must be total over `CLASSIFICATIONS × carriers`. A pair with no row refuses.

This is where the cheapest candidate returns as a side effect: adding a value to one
enumeration without adding its matrix rows fails, which is instance 1 and instance 6
without a bespoke parity scanner.

## Slice plan

1. **Declare, from observation.** Run each `(classification, carrier)` pair through the
   real floor with a deliberately-failing body and record which floors bit. Write the
   matrix from what was observed, not from reading the modules — reading is how the
   current five-module scatter stayed invisible.
2. **Build the validator** against that matrix. Expect it to refuse at first; the
   declaration written in step 1 is a measurement, and any disagreement is either a
   fixture bug or a real finding.
3. **Disposition each `skipped-by-design` cell.** The `consolidated` skips need a
   written reason or they need to change. This is where a real repair may fall out, and
   it is a separate decision from the matrix.
4. **Wire the validator into the quality run** and into `.agents/surfaces.json` as an
   owned surface with a real verify command.

## Fresh-eye obligation

This slice changes verdict logic on a proof surface, so it owes **two** bounded review
rounds — the second reading the repairs. Round 2 has caught a blocker on every measured
slice of this class in this repo, including twice on 2026-08-10.

## Non-goals and non-claims

- This does not cover `#586` instances 4 and 5 (a parameter default disarming a check
  on the wired path). Those measure 0 today; if the shape recurs, re-measure before
  building for it. `#586` therefore stays open after this slice.
- The matrix says where a floor RUNS. It says nothing about whether the floor is
  correct, and it must not be read as evidence that a running floor is a sufficient
  one.
- No consumer repo has been inspected. Every number above is from this tree on
  2026-08-10 and the scans behind them are heuristics whose limits are recorded in the
  `#586` comment of that date.

AI-provenance: authored by an agent session.
