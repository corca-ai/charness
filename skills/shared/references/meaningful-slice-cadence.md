# Meaningful-Slice Cadence

A slice is a **reviewable intent unit**, not merely a small diff. Review,
broad proof, and artifact updates are paced by that unit and its risk — never
by commit count. This reference owns the slice-unit definition and the proof
cadence; critique-specific escalation stays in the critique cadence
reference, and goal-run mechanics stay in the achieve lifecycle.

## What Makes A Slice Meaningful

A meaningful slice is one coherent:

- behavior surface (a user-visible or agent-visible behavior changes as one
  unit),
- support pattern (one helper/contract family lands together with its
  consumers),
- operator workflow (one operator-facing path becomes usable end to end), or
- hotspot family (one named cluster of related findings is dispositioned
  together),

with a **named proof intent** (what evidence will show it worked) and a
**useful verification boundary** (the cheapest gate set that honestly covers
it). A helper-only extraction, a rename, or an artifact touch-up is part of a
slice; it is not a slice by itself unless the artifact is the deliverable.

When candidate work keeps splitting into tiny moves, that is a signal the
candidate set is not structurally settled yet — go back to selection (for
structural quality cleanup, the quality signal scorecard) instead of
shipping the next micro-diff.

## Review Cadence

- Fresh-eye review runs per meaningful unit and risk boundary, not per
  commit. Several cheap commits may land inside one slice before one bounded
  review.
- A later commit inside the same slice re-triggers review only when it moves
  the risk boundary (new public surface, validator family, export path,
  release/closeout carrier, irreversible migration).
- Per-slice review used as reassurance — when the design did not change — is
  cadence waste, not rigor.
- **Premortem is inside this cadence, not an exception to it.** Mandatory
  premortem fires once per slice-intent boundary (the meaningful unit), and
  further commits within one unchanged intent re-fire it only when the risk
  boundary moves. A task-completing *change* is the slice; each commit inside it
  is not its own premortem. This is the single resolution of the
  "premortem per task-completing change" vs "critique is slice-level" tension —
  `critique/references/cadence.md` and the `achieve` lifecycle defer here.

## Proof Cadence

- Inner loop: focused tests and the surface validators the slice actually
  touched.
- Slice boundary: the owning gate families for the changed surfaces, plus
  fresh-eye review when the risk boundary calls for it.
- Bundle/final boundary: broad standing gates, pre-push, and
  coverage-producing runs are **final-bundle proof by default**. Starting
  them per inner-loop move pays the most expensive gates for the least
  settled state; reserve earlier broad runs for a runtime-affecting slice
  that genuinely needs them.

## Artifact Cadence

- Record artifacts and current-pointer updates ride the commits of the work
  they describe; updating them is not its own repeated slice unless the
  artifact is the deliverable.
- Learn an artifact's template contract before drafting into it, and keep
  current-pointer refreshes separate from record-artifact drafting so
  pointer churn never masquerades as progress.
- A history of frequent artifact-only commits is process churn made visible;
  prefer folding artifact updates into the meaningful unit they support.
  `run_slice_closeout.py` surfaces a non-blocking advisory when a run of
  consecutive `charness-artifacts/`-only commits crosses the threshold
  (`CHARNESS_OVERSLICE_ARTIFACT_RUN`, default 3), so the churn is visible at
  closeout instead of only in hindsight.
