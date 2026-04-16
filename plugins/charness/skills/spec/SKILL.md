---
name: spec
description: "Use when a concept needs to become a living implementation contract. Refine ideation artifacts or existing design docs into the current build contract, decide what must be fixed now versus probed during implementation, define testable success criteria, and keep the contract synchronized as `impl` learns new facts."
---

# Spec

Use this when the next job is to make the build contract explicit enough that
implementation can move without rediscovering the problem.

`spec` is not only a document-writing phase before `impl`. It is the skill for
managing the current implementation contract. Sometimes that contract is mostly
settled up front. Sometimes it becomes sharper while implementation proceeds.

## Bootstrap

Read the current concept artifacts before inventing new structure.

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
# 1. current concept and adjacent context
rg --files docs skills
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
sed -n '1,220p' "$SKILL_DIR/../ideation/SKILL.md" 2>/dev/null || true

# 2. existing concept/spec/design docs
rg -n "concept|spec|requirements|success criteria|acceptance|entity|stage|constraint" .

# 3. implementation-side neighbors
sed -n '1,220p' "$SKILL_DIR/../create-skill/SKILL.md" 2>/dev/null || true
sed -n '1,220p' "$SKILL_DIR/../impl/SKILL.md" 2>/dev/null || true
```

If an ideation document already exists, refine it into a spec. Do not restate
the entire discovery history from scratch.
If the repo already has executable acceptance artifacts, treat them as part of
the spec surface rather than as a separate world.
When the repo uses executable specs, inspect whether they stay at the
acceptance boundary or whether they have started duplicating low-level test
detail and runtime cost.
Borrow Ward Cunningham-style executable-spec discipline when the repo uses
tools such as `specdown`: executable acceptance artifacts should make the
contract concrete at the boundary, not replace the unit suite or hide low-level
test detail.
Keep Christopher Alexander-style sequence discipline in the contract: order
`Fixed Decisions`, `Probe Questions`, and `Deferred Decisions` so upstream
commitments land before downstream detail hardens. When the slice is still
noisy, borrow Kent Beck for thin feedback-bearing slices and John Ousterhout
for simpler interfaces and deeper seams. See
`references/sequence-discipline.md` and `references/design-lenses.md`.

## Contract Shaping

Choose the lightest honest contract shape.
When implementation churn would be expensive, reduce ambiguity earlier and make
the slice more explicit before coding starts.
If some answers will emerge only while building, keep the contract
probe-friendly and visible instead of inventing a user-facing mode choice.

If the repo already treats executable checks as contract artifacts, push
acceptance into those checks instead of managing a separate prose-only branch.

If those executable checks are materially expensive, shape the contract so the
standing acceptance bar stays honest about cost. Keep executable examples at
the boundary and push duplicated unit-detail coverage downward instead of
celebrating broad slow coverage.

Before locking the contract, run one bounded premortem. Ask what a fresh
five-minute implementer, reviewer, or operator would most likely misread, and
tighten only the lines that create real ambiguity. If the runtime supports
subagents and the session explicitly allows them, use one fresh-eye subagent
with a contrasting lens; otherwise do the challenge pass yourself. See
`references/premortem-loop.md`. When the decision is non-trivial, use the
standalone `premortem` skill as the subroutine rather than reinventing angle
selection and triage inline.

## Workflow

1. Ingest the current artifact.
   - identify the source artifact or source summary
   - restate the stable idea in implementation terms
   - separate what is already decided from what is still ambiguous
2. Classify the remaining uncertainty.
   - `Fixed Decisions`: must be decided before this slice starts
   - `Probe Questions`: should be answered through a small implementation slice,
     spike, or executable check
   - `Deferred Decisions`: visible decisions that can safely wait
   - order these lists by dependency pressure, not prose convenience
3. Reduce only the ambiguity that blocks this slice.
   - ask targeted questions only for choices that change build scope,
     user-visible behavior, acceptance, sequencing, dependency choice, or risk
   - if a reasonable default is clear, recommend it with reasons instead of
     opening broad option trees
4. Define the current execution contract.
   - current slice
   - non-goals
   - deliberately not doing or rejected alternatives when future readers are
     likely to reopen the same branch
   - constraints
   - success criteria
   - acceptance checks
   - open risks, probe questions, or deferred decisions
5. Tie the contract to verification.
   - every important success criterion should imply at least one acceptance
     check
   - add negative cases when failure would matter to users or operators
   - if the repo already uses executable specs or tests as contract artifacts,
     prefer promoting acceptance checks into that form
   - if executable specs already exist, keep them at acceptance level and move
     repeated low-level detail into unit tests, source guards, or more direct
     adapters
   - when one acceptance path is materially slower than the rest, document why
     that cost is justified and which cheaper layers should absorb the detail
6. Keep the contract alive during implementation.
   - stabilize the contract earlier when churn would otherwise be expensive
   - keep unresolved items visible as probes when answers should emerge through
     implementation
   - keep prose and executable checks synchronized when the repo already uses
     executable contract artifacts
   - if implementation discovers a fact that changes scope or acceptance, update
     the spec instead of leaving chat-only drift
7. Run a bounded premortem before finalizing.
   - ask what a fresh five-minute reader would most likely implement or approve
     incorrectly from this contract
   - focus on missing invariants, overloaded examples, hidden sequencing, and
     acceptance checks that look stronger than they really are
   - if subagents are available and explicitly allowed, use one fresh-eye
     subagent or contrasting reviewer lens; otherwise do the same pass locally
   - keep future re-litigation low by writing the important rejected paths into
     the spec itself instead of leaving them in chat-only memory
   - tighten only the lines that change the likely next action; do not reopen
     broad ideation
8. End with the next execution state.
   - whether the current contract is ready for `impl`
   - what the first or next implementation slice should be
   - which artifact is canonical during implementation

## Output Shape

The final spec should usually include:

- `Problem`
- `Current Slice`
- `Fixed Decisions`
- `Probe Questions`
- `Deferred Decisions`
- `Non-Goals`
- `Deliberately Not Doing`
- `Constraints`
- `Success Criteria`
- `Acceptance Checks`
- `Premortem`
- `Canonical Artifact`
- `First Implementation Slice`

If the idea depends on durable structure or flow, reuse ideation outputs such as
`Entities` or `Stages` instead of recreating them under new names.

## Guardrails

- Do not reopen broad concept exploration that belongs in `ideation`.
- Do not treat `spec` as mandatory upfront completeness. A thin honest contract
  is better than a fake complete one.
- Do not leave success criteria as vague aspirations.
- Do not allow an important success criterion without at least one acceptance
  check.
- Do not skip the bounded premortem on a risky or cross-surface contract just
  because the document reads clearly to the current author.
- Do not leave important rejected alternatives only in chat when the same
  branch is likely to be reopened by the next maintainer.
- Do not let acceptance checks become a second copy of the unit suite just
  because the repo already has executable specs.
- Do not silently assume implementation details when they materially change
  scope or user-visible behavior.
- Do not keep broad shell-driven executable checks in the contract when a
  cheaper deterministic lower layer would prove the same behavior honestly.
- If the concept artifact is still unstable in a concept-defining way, send the
  work back to `ideation` rather than writing a fake spec.
- A good spec refines an existing concept artifact and stays synchronized with
  implementation. It does not discard the artifact or leave it stale.
- Keep host-specific file locations or template choices outside the core skill
  body; use repo documents or adapters where needed.

## References

- `references/contract-modes.md`
- `references/fixed-probe-defer.md`
- `references/ingest-and-refine.md`
- `references/success-criteria.md`
- `references/acceptance-checks.md`
- `references/executable-spec-cost.md`
- `references/premortem-loop.md`
- `references/rejected-alternatives.md`
- `references/design-lenses.md`
- `references/sequence-discipline.md`
- `references/ambiguity-rules.md`
- `references/impl-loop.md`
- `references/ideation-boundary.md`
- `references/document-seams.md`
