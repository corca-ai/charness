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

When the slice changes a guard, reference, claim, or verdict surface, its
review packet also carries the [semantic question](./reviewer-packet-semantic-question.md):
the semantic fact or invariant, owning boundary, recorded instance, and an
axis-varying counterexample. This is reviewer evidence, not a new semantic
meta-gate.

When candidate work keeps splitting into tiny moves, that is a signal the
candidate set is not structurally settled yet — go back to selection (for
structural quality cleanup, the quality signal scorecard) instead of
shipping the next micro-diff.

## Review Cadence

- Fresh-eye review belongs to explicitly selected `critique` work and to true
  irreversible or proof boundaries when their owner requires it. A meaningful
  slice does not create a review obligation for ordinary reversible work.
- When `critique` is selected, use the meaningful intent and risk boundary as
  the review unit, not the commit. Several cheap commits may land inside one
  slice before one bounded review; a later commit needs another pass only when
  it moves the risk boundary (new public surface, validator family, export
  path, release/closeout carrier, or irreversible migration).
- Review used as reassurance when the design did not change is cadence waste,
  not rigor.
- A premortem is an explicitly selected `critique` target, not a mandatory
  per-slice step. When selected, keep it to one coherent risk boundary and
  revisit it only when that boundary moves.

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
