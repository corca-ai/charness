# Session Retro
Date: 2026-08-06

Disposition review for goal
[2026-08-06-make-a-verdict-state-the-scope-it-measured.md](../goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md).
This is the rung-1b closeout artifact: it CHECKS the dispositions the goal
recorded, so `tracked issue` and `applied` are verified rather than asserted.

## Context

The goal's `## Auto-Retro` records three improvement dispositions and the run
produced four residual findings. A disposition is a claim about what happened to
a finding; this reviews each against the tree.

## Evidence Summary

- 3 improvement dispositions checked; 1 was tightened (see Critical Decisions).
- 4 residual findings checked for a durable home: #491, #492, #493, #494 filed.
- `tests/quality_gates/test_quality_policy_merge_import.py` exists and runs both
  import orders in a subprocess — the `applied` half of disposition 2.
- `scripts/quality_bootstrap_lib.py` carries the `mutation_testing` coarseness
  note at the call site, not only in the goal artifact.

## Waste

None attributable to this review. It found one overclaim before it shipped, which
is the review paying for itself rather than creating rework.

## Critical Decisions

- **Disposition 2 was split rather than labelled `applied`.** The guard covers
  one module pair, not the class. `applied` for the pair plus issue #492 for the
  generalization is what the evidence supports; a bare `applied` would have
  claimed a repo-wide property from a two-module test.
- **Every `intentional` dup-review note was checked against its own family.** An
  earlier version named both partners in both notes; a reviewer caught it and the
  notes now name each family's own partner. An `intentional` label that
  misdescribes its family is a false record on a proof surface.

## North Star Alignment

P1/P3: this artifact exists because a disposition is a verdict about a finding,
and the standard says a verdict owes a different observer at an irreversible
boundary. Closing an issue is that boundary. The check held: it caught one
overclaim (disposition 2) before the flip.

Not mis-applied here. The facet this review cannot supply is independence — it is
written by the same agent that recorded the dispositions. The independent check
is the delegated resolution critique, which is a separate artifact and did refuse
two of four closes.

## Expert Counterfactuals

Direct: "would a reader who only had the label know what actually happened?" For
disposition 2, `applied` alone would have said yes to a question the evidence
answers with "for one pair". That question is what split it.

## Sibling Search

- axis: a disposition label claiming more than its evidence | decision: fixed
  in-place, not deferred | proof: disposition 2 split into its applied and
  tracked halves before the flip | follow-up: none — the split is the fix

## Next Improvements

- workflow: none — the disposition-review step worked as intended this run.
- capability: none surfaced by this review beyond the four already filed.
- memory: none — the four residuals each have a tracked issue, so nothing here
  relies on prose memory.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-disposition-review.md
