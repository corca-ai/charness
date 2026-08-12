# Issue 584 Planner Read Cost Debug
Date: 2026-08-12

## Problem

Run-plan `required_reads` disclose a path and rationale but no byte cost, even
though planners can resolve the file before instructing an agent to read it.

## Correct Behavior

Given a planner emits a readable local file, when it includes that file in
`required_reads`, then the item carries a measured byte count or an explicit
unavailable state. Consumers can assess cumulative read cost without guessing.

## Observed Facts

- #584 records #532's live defect: gate packets require `cost_tier`, whereas
  `skills/shared/scripts/run_plan_envelope.py` requires only path and why.
- `ENVELOPE.read()` is shared by debug, handoff, retro, and other planners but
  has no repository root or skill root to resolve a relative path.
- `plan_quality_run.py` builds required reads from catalog entries without a
  path-existence or size measurement, so merely adding an optional envelope
  field would leave the reported quality-plan reads unpriced.
- `tests/test_run_plan_envelope.py` only proves optional metadata propagation;
  no planner contract asserts a byte value or unavailable disclosure.

## Reproduction

- Run `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`:
  every `required_reads` item lacks a size/cost field although its source file
  is locally resolvable.

## Candidate Causes

- The common constructor cannot resolve base-relative paths.
- Each planner treats required reading as free contextual metadata.
- The envelope validator protects shape but lacks a measurement contract.

## Hypothesis

- The defect requires a shared read-measurement helper plus planner-specific
  root resolution, not a quality-only display field; disconfirmer: a single
  shared constructor can determine every current planner path without knowing
  its declared base or changing any caller.

## Verification

- Result: confirmed by static inspection of `run_plan_envelope.py`, the quality
  planner's catalog projection, and all planner call sites. No repair is made:
  this shared contract needs a scoped implementation/spec decision first.

## Root Cause

The shared envelope models read entries as prose instructions rather than
measured local work, and it deliberately lacks the path-resolution context
needed to compute the missing fact.

## Invariant Proof

- Invariant: when a planner produces a required local read, the consuming agent
  must receive its measured byte cost or an explicit unavailable state.
- Producer Proof: quality planner produces catalog-backed required reads.
- Final-Consumer Proof: plan JSON read by the agent lacks any cost signal.
- Interface-Shape Sibling Scan: debug, handoff, and retro use the same envelope
  helper; their base-relative resolution differs.
- Non-Claims: no universal remediation has been designed or tested.

## Detection Gap

- Run-plan envelope tests | optional-field propagation did not require measured
  facts | add cross-planner fixture tests once the measurement contract exists.

## Sibling Search

- Mental model: a planner's required read is documentation, not executable work
  with a measurable cost.
- same layer: all `ENVELOPE.read` callers | decision: same class, diagnostic-only
  for this slice | proof: static scan only.
- abstraction up: planner protocol | decision: valid follow-up outside the
  slice | proof: static scan only | follow-up: deferred docs/handoff.md#next-session
- cross-file: `skills/public/quality/scripts/plan_quality_run.py` | decision:
  intentional first consumer | proof: local payload proof.

## Seam Risk

- Interrupt ID: issue-584-read-cost-contract
- Risk Class: repeated-symptom
- Seam: planner-specific path bases to shared envelope to agent read workload.
- Disproving Observation: all current planners share a single resolvable path root.
- What Local Reasoning Cannot Prove: a portable read-cost schema that remains
  honest for installed-plugin and consumer-repo layouts.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Critique Scope: shared planner read-cost schema and path-owner boundary.
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/planner-required-read-cost-contract.md

## Prevention

Do not add a quality-only label. Define one portable measurement/disclosure
contract with fixture proof for each path base before changing the envelope.
