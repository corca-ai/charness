# Debug Review: #294 Abstraction-Up Diagnostic Disposition
Date: 2026-06-04
Issue: #294

## Problem

Bug-class RCA sibling search can record an abstraction-up same-class finding as
`diagnostic-only` even when the text also describes unresolved repo-level work,
leaving no bundled fix, intentional boundary, proof that no action is needed, or
durable follow-up identifier.

## Correct Behavior

Given a bug-class RCA sibling search that uses the abstraction-up axis, when it
identifies a same-class sibling or broader structural class not fixed in the
current slice, then closeout records exactly one disposition: bundled fix,
intentional boundary with reason, diagnostic-only with proof that no action is
needed, or valid follow-up outside the slice with an issue URL or handoff
anchor. Ordinary same-layer diagnostic-only entries remain valid when bounded
and not describing deferred structural work.

## Observed Facts

- GitHub issue #294 is open and asks for a deterministic floor for
  abstraction-up `diagnostic-only` entries.
- The triggering instance was `corca-ai/ceal#245`, where a lunch-match-specific
  fix named broader messenger side-effect durability siblings but initially
  left the broader class diagnostic-only.
- `debug` already requires sibling-search output to classify decisions and proof
  separately, and to persist valid follow-ups outside the slice with a
  `follow-up:` identifier.
- `issue` causal-review closeout consumes debug sibling-search output and carries
  sibling decisions into the close ledger.
- The current gap is not that `diagnostic-only` exists; the gap is that
  abstraction-up unresolved structural work can look like diagnostic context
  instead of owned work.

## Reproduction

A bug-class debug artifact can state a sibling on the abstraction-up axis as
`same class, diagnostic-only for this slice` while also describing deferred or
unresolved repo-level work, and the current closeout validation does not require
proof/no-action reasoning or a `follow-up:` identifier for that unresolved work.

## Candidate Causes

- Taxonomy ambiguity: `diagnostic-only` covers both "inspected, no action
  needed" and "not fixing this broader class now."
- Axis ambiguity: same-layer diagnostic notes and abstraction-up structural
  findings are validated with the same floor.
- Closeout consumption gap: `issue` closeout preserves sibling text but does not
  force unresolved abstraction-up work into a carrier, non-goal, or durable
  follow-up.
- Validator gap: artifact validators check section shape more strongly than
  sibling-disposition semantics.

## Hypothesis

If sibling-search guidance and validators distinguish abstraction-up unresolved
structural work from ordinary diagnostic-only notes, then diagnostic-only remains
available for bounded no-action findings while broader unresolved work must gain
proof, an intentional boundary, or a follow-up owner.

## Verification

Planned focused proof:

- Unit tests for invalid abstraction-up `diagnostic-only` unresolved structural
  work without proof or follow-up.
- Unit tests for valid ordinary same-layer diagnostic-only findings.
- Unit tests for valid abstraction-up entries with proof/no-action reasoning,
  intentional boundary, bundled fix, or `follow-up:` issue/handoff anchor.
- Debug artifact validator run against this artifact and affected fixtures.

## Root Cause

The sibling-search taxonomy exposed a useful diagnostic-only label before the
closeout contract distinguished proof-backed no-action findings from unresolved
abstraction-up structural work. A broader class could therefore be noticed but
not converted into a current fix, explicit boundary, or durable follow-up.

## Invariant Proof

- Invariant: abstraction-up same-class findings that describe unresolved
  structural work must have an owner or a proof-backed no-action disposition.
- Producer Proof: debug sibling-search guidance and artifact examples should
  state the disposition options and require `follow-up:` for deferred structural
  work.
- Final-Consumer Proof: validators and issue closeout checks should reject the
  narrow unresolved abstraction-up diagnostic-only pattern while preserving
  ordinary bounded diagnostic-only entries.
- Interface-Shape Sibling Scan: scan debug artifacts, issue causal-review
  references, closeout-discipline text, and validators for places that treat
  diagnostic-only as a final disposition without proof/follow-up.
- Non-Claims: this RCA does not decide whether every historical debug artifact
  must be rewritten; historical records may remain legacy memory unless touched
  by current validation.

## Detection Gap

- debug sibling-search guidance | did not distinguish diagnostic-only no-action
  proof from deferred abstraction-up structural work | add explicit disposition
  contract.
- issue closeout consumption | close ledger can inherit sibling text without
  owner/follow-up enforcement | bind closeout wording and validation to the
  disposition contract.
- artifact validation | no narrow semantic floor for abstraction-up unresolved
  work | add tests and validator logic for the exact pattern.

## Sibling Search

- Mental model: naming the broader class in RCA was treated as sufficient
  ownership.
- same-layer diagnostic axis: ordinary bounded diagnostic-only findings remain
  intentional boundary; decision: preserve, proof: contract review.
- abstraction-up axis: unresolved structural classes require owner/proof;
  decision: same bug, fix now for #294, proof: issue body plus current RCA.
- issue closeout axis: close comments and commit ledgers can repeat sibling
  findings without binding a disposition; decision: inspect and update if in
  scope, proof: static contract review.
- validator axis: shape-only validators may miss semantic sibling drift;
  decision: add narrow hard floor, proof: planned focused tests.

## Seam Risk

- Interrupt ID: issue-294-abstraction-up-diagnostic-disposition
- Risk Class: closeout-discipline
- Seam: debug RCA sibling-search text to issue closeout and validators.
- Disproving Observation: a broader class was recorded as diagnostic context
  until the operator challenged the missing owner.
- What Local Reasoning Cannot Prove: every legacy artifact's intended
  disposition without re-reading its originating incident.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl after issue causal review confirms the substrate.
- Handoff Artifact: charness-artifacts/goals/2026-06-04-issue-294-298.md

## Prevention

Make diagnostic-only a proof-backed no-action disposition for abstraction-up
work, not a hiding place for deferred structural ownership.
