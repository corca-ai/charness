# Spec Critique

Critique a spec, design contract, or implementation plan before `impl`
starts. The substrate (multi-angle review with one counterweight pass and
four-bin triage) is shared with other `critique` targets; this reference
shapes the angle distribution and output for *pre-impl spec lock-in*.

## When This Lens Fires

Pick this reference when the pending change is a spec or design contract
about to gate implementation. Trigger phrases:

- `spec critique`, `spec premortem`, pre-impl review
- before `impl` consumes a current-slice contract
- when a Fixed Decision / Probe Question / Deferred Decision split is
  about to lock the next slice's scope
- when the spec adds Success Criteria or Acceptance Checks that downstream
  validators will be expected to enforce

If the change is already code, route to `code-critique.md`. If the change
is a release artifact, route to `release-critique.md`. If the change is a
rename plan inside the spec, route to `rename-critique.md` for the rename
slice.

## Anchor Angle Distribution

For spec lock-in, anchor weighting emphasizes structure, framing, and
hidden coupling:

- **Barbara Minto (structure / communication)** — strong default. Do
  Problem → Current Slice → Fixed Decisions → Probe Questions → Deferred
  → Non-Goals → Constraints → Success Criteria → Acceptance Checks form a
  legible chain, or does the contract leak rationale into chat?
- **Michael Jackson (problem framing)** — strong default. Is the spec
  framed against the user's actual problem, or against the most
  convenient implementation slice? Hidden scope creep often hides in the
  Current Slice section.
- **Gerald Weinberg (diagnostic)** — moderate. Is the *real* problem in
  the layer the spec targets, or somewhere else? Pulls back from
  "interesting design" to "is this where the pain lives".
- **Atul Gawande (checklist / operational)** — moderate. Will the
  Acceptance Checks actually run? Are they validator-shaped or prose-only?
  What operator-visible step does the slice add?
- **Jef Raskin (humane interface / first-time-use)** — light unless the
  spec changes operator-facing surface, capability discovery, or first-
  reader narrative.

Default slate: Minto + Jackson + Weinberg. Swap in Gawande when the
spec's Acceptance Checks are weak or prose-only. Swap in Raskin when the
spec changes operator-facing surface.

## Counterweight Bins

The four bins from `counterweight-triage.md` apply directly. Spec-
specific tightening:

- **Act Before Ship** — concerns that require tightening the spec before
  `impl` consumes it: an Acceptance Check that cannot be enforced, a
  Fixed Decision that hides a real Probe Question, a Success Criterion
  that is not falsifiable, a Deferred Decision that should actually be
  Fixed.
- **Bundle Anyway** — cheap fixes touchable in the same lock-in: a
  Probe Question made explicit, a Non-Goal line that prevents a known
  scope-creep direction, a Constraint added so a downstream gate has a
  rationale anchor.
- **Over-Worry** — concerns about imagined slices that may never run,
  speculative consumers, or aesthetic concerns about wording when the
  contract semantics are clear.
- **Valid but Defer** — concerns that are real but belong in a later
  slice and should be recorded as Deferred Decisions or Open Items in the
  spec rather than expanded into Fixed Decisions.

## Fixed/Probe/Defer Coherence

Every spec critique records a coherence check across Fixed Decisions,
Probe Questions, and Deferred Decisions:

- a Fixed Decision must not name an unresolved unknown that would force
  `impl` to invent the contract inline
- a Probe Question must be answerable inside the slice it gates and must
  name where its answer will be written back
- a Deferred Decision must name the trigger that would reopen it, not
  just "later"

A coherence violation routes the concern to `Act Before Ship` unless the
reviewer can show the slice is honestly small enough to absorb the
ambiguity.

## Acceptance Check Coverage

Every spec critique records whether each Success Criterion has a matching
Acceptance Check:

- a Success Criterion without a matching check is a folklore criterion
  and routes to `Act Before Ship` until a check is named or the criterion
  is removed
- an Acceptance Check that is prose-only (no validator, no script, no
  deterministic gate) routes to `Bundle Anyway` if a cheap deterministic
  check exists, `Valid but Defer` if writing the check requires its own
  slice
- when the spec adds new validators, a smoke run of the validator on the
  current repo state belongs in the same slice as the validator's
  introduction

## Output Shape

In addition to the substrate `Output Shape` from `SKILL.md`, spec critique
records:

- `Spec Path` — canonical artifact path
- `Fixed/Probe/Defer Coherence Result` — pass/fail per section with the
  concrete violations
- `Acceptance Check Coverage Result` — per Success Criterion, the matching
  Acceptance Check or the gap
- `Pre-Impl Action` — for each `Act Before Ship` concern, the concrete
  spec edit required before `impl` consumes the contract
