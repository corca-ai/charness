# Debug Review
Date: 2026-08-04

## Problem

Across one goal, guards and references repeatedly attached to an observed form
(transport, type, equality, status spelling, or count) instead of the semantic
invariant or claim the reader needed. The existing review process found the
mistakes after implementation, but the next author still lacked a portable
question that made the intended fact explicit before choosing a surface.

## Correct Behavior

When a guard, reference, or verdict surface is proposed, the authoring packet
must name the semantic fact or invariant, its owning boundary, a recorded
instance that the control must catch, and a counterexample that varies the
actual axis while preserving the observed form. A reviewer then judges that
question. No semantic meta-gate should guess the invariant.

## Observed Facts

- The gathered primary record reports five #499 proxy-form instances and three
  #491 shipped-reference/code mismatches (`charness-artifacts/gather/2026-08-04-goal-issue-sources.md:23-33`).
- #499 is now CLOSED and #491 is OPEN; the older handoff state was stale
  (`charness-artifacts/gather/2026-08-04-goal-issue-sources.md:23-33,58-62`).
- The goal's Slice A decision selects a reviewer question for both records and
  requires invariant, owner, instance, and axis-varying counterexample
  (`charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md:259-267`).
- Current inventory has no `reference-claims` or claims-manifest surface; `rg`
  found no such path or token in the tree.

## Reproduction

- Start from any of the five #499 rows in the gathered record and ask what the
  guard proves about the outcome rather than what syntax it matches. The
  guard's observed-form predicate can be restated without naming an outcome.
- Repeat with the three #491 mismatches: a reference can look locally plausible
  while disagreeing with the shipped code because no owner or claim is named.

## Candidate Causes

- Transport/proxy convenience makes the observed representation look like the
  invariant.
- No single owning surface carries the semantic fact across authoring and
  review boundaries.
- Existing reviewer packets ask for tests and non-claims but not an invariant,
  recorded instance, and axis-varying counterexample.
- Scope and cost pressure favor a local predicate or literal edit over naming
  the reader's actual decision.
- Stale handoff/issue context can make an apparently settled record look open.

## Hypothesis

- The primary cause is a missing authoring-boundary question, not insufficient
  test volume. Falsifier: a current packet consumer already requires the four
  semantic fields and demonstrably rejects or routes the five #499 / three #491
  shapes. disconfirmer: `rg` inventory plus inspection of the goal's packet
  contract; result: confirmed — no such requirement was found.

## Verification

- confirmed — the gathered issue record supplies the repeated symptom, and the
  current packet contract names intent, proof, and non-claims but not this
  semantic four-part question (`...goal...md:24-26`).

## Root Cause

The portable reviewer-packet contract did not force the author to state the
semantic fact, owner, recorded instance, and axis-varying counterexample before
selecting a guard, reference, or surface. Reviewers could recover the intent,
but only after a proxy had already been designed.

## Invariant Proof

- Invariant: n/a — this is an authoring/review judgment boundary, not a
  producer-to-final-consumer diagnostic propagation bug.
- Producer Proof: n/a — no runtime signal is being transported.
- Final-Consumer Proof: n/a — no workflow success consumer is being changed.
- Interface-Shape Sibling Scan: reviewer packet and issue-shaping surfaces;
  see Sibling Search.
- Non-Claims: this does not prove a future host's reviewer UI renders the
  question, nor that a reviewer will make the right judgment.

## Detection Gap

- Existing bounded critique | caught proxy choices only after implementation or
  repair | add the four-part question to the packet before implementation.
- Broad pytest and static gates | do not judge whether a predicate names the
  semantic outcome or whether a reference has an owner | prove the question by
  applying it to a recorded #499 or #491 instance.
- Human review | was the only realistic detector for judgment-bound intent, but
  the packet did not make the needed evidence explicit | make the reviewer
  question portable and falsifiable.

## Sibling Search

- Mental model: choosing an observable proxy before naming the fact a reader or
  control must carry.
- same layer: `charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md:24-26` | decision: same class, diagnostic-only for this slice | proof: static scan only; packet fields were inspected.
- abstraction up: `skills/shared/references/` and public skill packet guidance | decision: same bug, fix now | proof: static scan only; the shared contract is the portable owner.
- specialization down: #499 guard rows and #491 reference mismatches | decision: same class, diagnostic-only for this slice | proof: local gathered payload proof; exact issue repairs are out of scope for B.
- cross-file: `skills/shared/references/meaningful-slice-cadence.md` and public achieve/impl packet guidance

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: a packet consumer already enforces the four fields
- What Local Reasoning Cannot Prove: host-specific rendering or reviewer uptake
- Generalization Pressure: monitor
- Keep the question portable; do not encode issue-specific nouns or a semantic
  meta-gate.

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- The Slice B contract change will receive bounded fresh-eye review before
  closeout.
- Next Step: impl
- Handoff Artifact: this dated record and the refreshed debug current pointer

## Prevention

Add the four-part reviewer question to the canonical portable packet contract:
semantic fact/invariant, owning boundary, recorded instance, and axis-varying
counterexample. Keep the selector per issue: reviewer question for #499/#491,
surface fixes for the other issue families, and no semantic meta-gate. Prove
the question bites against a recorded issue row before claiming Slice B.
