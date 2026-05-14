---
name: spec
description: "Use when a concept needs to become a living implementation contract. Refine ideation artifacts or existing design docs into the current build contract, decide what must be fixed now versus probed during implementation, define testable success criteria, and keep the contract synchronized as `impl` learns new facts."
---

# Spec

Use this when the next job is to make the build contract explicit enough that implementation can move without rediscovering the problem. `spec` manages the current implementation contract, whether it is mostly settled up front or becomes sharper while implementation proceeds.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`. Read the
current concept artifacts before inventing new structure.
Before drafting a contract or asking follow-up questions, inspect the current implementation and acceptance reality so the spec starts from repo truth, not from an abstract restatement.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. current concept and adjacent context
git status --short
rg --files . | sed -n '1,200p'
sed -n '1,220p' README.md 2>/dev/null || true
sed -n '1,220p' AGENTS.md 2>/dev/null || true
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
sed -n '1,220p' "$SKILL_DIR/../ideation/SKILL.md" 2>/dev/null || true

# 2. existing concept/spec/design docs
rg -n "concept|spec|requirements|success criteria|acceptance|entity|stage|constraint" .
python3 "$SKILL_DIR/../../../scripts/plan_risk_interrupt.py" --repo-root . --json 2>/dev/null || true

# 3. implementation-side neighbors and current acceptance reality
rg -n "test|spec|fixture|scenario|acceptance|success criteria|operator|takeover|smoke|integration" .
sed -n '1,220p' "$SKILL_DIR/../create-skill/SKILL.md" 2>/dev/null || true
sed -n '1,220p' "$SKILL_DIR/../impl/SKILL.md" 2>/dev/null || true
```

If an ideation document already exists, refine it instead of restating the full
discovery history. If executable acceptance artifacts already exist, treat them
as part of the spec surface and keep them at the acceptance boundary. Distinguish
`public executable contract` from `maintenance lint / implementation guard`.
Use `references/public-executable-contracts.md`, `references/sequence-discipline.md`,
and `references/design-lenses.md` for the detailed shaping rules.

## Worktree Readiness

Before mutating spec/design docs in a worktree, run `command -v charness >/dev/null 2>&1 && charness worktree doctor --json || true`. If JSON status is not `pass`, surface `charness worktree prepare` as next action and have the operator confirm before continuing.

## Contract Shaping

Choose the lightest honest contract shape.
When implementation churn would be expensive, reduce ambiguity earlier and make the slice more explicit before coding starts. If some answers will emerge only while building, keep the contract probe-friendly and visible instead of inventing a user-facing mode choice. Before adding public mode/kind/strategy/profile/target vocabulary, run `references/taxonomy-axis-checkpoint.md`.

If the repo already treats executable checks as contract artifacts, push acceptance into those checks instead of managing a separate prose-only branch. For public executable pages, keep current-state claims and bounded proof only; move future-state planning, source inventory, and low-level implementation guards down a layer. If the repo wants the latest on-demand validation visible to readers, project the checked artifact into a viewer-style executable page instead of rebuilding the evaluator logic inline or promoting source guards into the public spec.

If executable checks are materially expensive, keep the standing acceptance bar
honest about cost and push duplicated unit-detail coverage downward.

Before locking the contract, run success criteria review so future-success claims
become criteria, checks, and tripwires. Routine use may be inline; it does not
replace the bounded critique required before finalizing a task-completing contract; call `critique` for non-trivial contract decisions. Focuses: likely implementer misread, overstated acceptance, hidden sequencing.

## Workflow

1. Ingest the current artifact.
   - identify the source artifact or source summary
   - restate the stable idea in implementation terms
   - separate what is already decided from what is still ambiguous
   - note the current implementation, test, and operator-facing surfaces that
     already constrain the contract
2. Classify the remaining uncertainty.
   - `Fixed Decisions`: must be decided before this slice starts
   - `Probe Questions`: should be answered through a small implementation slice,
     spike, or executable check
   - `Deferred Decisions`: visible decisions that can safely wait
   - order these lists by dependency pressure, not prose convenience
3. Reduce only the ambiguity that blocks this slice.
   - check whether the repo already answered the question in code, tests, or
     existing docs before opening a new clarification branch
   - ask targeted questions only for choices that change build scope,
     user-visible behavior, acceptance, sequencing, dependency choice, or risk
   - if a reasonable default is clear, recommend it with reasons instead of
     opening broad branch trees
   - check taxonomy-axis consistency before adding public enum vocabulary
4. Define the current execution contract.
   - current slice, non-goals, constraints, success criteria, and acceptance checks
   - deliberately not doing or rejected alternatives when future readers may reopen the branch
   - apply `../../shared/references/source-bound-records.md` for multi-source external writes
   - open risks, probe questions, or deferred decisions
   - when the risk interrupt planner reports a forced debug interrupt, consume
     it explicitly in `Critique` with
     `Interrupt Source`, `Seam Summary`, `Chosen Next Step`, `Impl Status`,
     `Impl Status Reason`, and `What Disproving Observation Is Resolved`
5. Tie the contract to verification.
   - every important success criterion should imply at least one acceptance
     check
   - add negative cases when failure would matter to users or operators
   - if the repo already uses executable specs or tests as contract artifacts,
     prefer promoting acceptance checks into that form
   - cite proof from checked-in durable evidence; treat generated or ignored
     paths as reproduction sources only. See `references/evidence-durability.md`
   - if the contract edits repo-owned instruction or prompt surfaces that steer
     agent behavior, define whether the intended claim is `preserve` or
     `improve`, leave the matching Cautilus proof path visible, and let adapter
     policy decide whether proof asks first, auto-runs low-cost checks, or adapts
     by proof kind and cost
   - for reader-facing reasoning-shape or reader-fit changes, plan a short
     scenario review instead of equating preserve-proof with semantic success
6. Keep the contract alive during implementation.
   - stabilize the contract earlier when churn would otherwise be expensive
   - keep unresolved items visible as probes when answers should emerge through
     implementation
   - keep prose and executable checks synchronized when the repo already uses
     executable contract artifacts
   - if implementation discovers a fact that changes scope or acceptance, update
     the spec instead of leaving chat-only drift
7. Run bounded critique before finalizing.
   - call `critique` for task-completing contracts and non-trivial contract
     decisions
   - use `../../shared/references/fresh-eye-subagent-review.md` before reporting blocked
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
- `Critique`
- `Canonical Artifact`
- `First Implementation Slice`

If the idea depends on durable structure or flow, reuse ideation outputs such
as `Entities` or `Stages` instead of recreating them under new names.

## Guardrails

- Do not reopen broad concept exploration that belongs in `ideation`, treat
  `spec` as mandatory upfront completeness, or leave success criteria vague.
- Do not allow an important success criterion without at least one acceptance
  check.
- Do not clear a forced debug interrupt with generic spec churn; if the planner
  surfaced one, the spec must explicitly consume that interrupt in
  `Critique`.
- Do not skip the bounded critique before finalizing a task-completing
  contract just because the document reads clearly to the current author.
- Do not leave important rejected alternatives only in chat when the same
  branch is likely to be reopened by the next maintainer.
- Do not let acceptance checks become a second copy of the unit suite just
  because the repo already has executable specs.
- Do not cite generated or gitignored output paths as durable proof. Either
  check in a selected proof artifact with the cited fields, or declare the
  proof as reproduction-only. See `references/evidence-durability.md`.
- Do not silently assume implementation details or ignore current code, tests,
  or operator docs when they materially affect the contract.
- Do not keep broad shell-driven executable checks in the contract when a
  cheaper deterministic lower layer would prove the same behavior honestly.
- If the concept artifact is still unstable in a concept-defining way, send the
  work back to `ideation` rather than writing a fake spec.
- A good spec refines an existing concept artifact and stays synchronized with implementation.
- Keep host-specific file locations or template choices outside the core skill body.

## References

- `references/contract-modes.md`
- `references/fixed-probe-defer.md`
- `references/ingest-and-refine.md`
- `references/success-criteria.md`
- `references/acceptance-checks.md`
- `references/evidence-durability.md`
- `references/public-executable-contracts.md`
- `references/executable-spec-cost.md`
- `references/rejected-alternatives.md`
- `references/design-lenses.md`
- `references/sequence-discipline.md`
- `references/ambiguity-rules.md`
- `references/impl-loop.md`
- `references/ideation-boundary.md`
- `references/document-seams.md`
- `references/taxonomy-axis-checkpoint.md`
- `../../shared/references/agent-assessment-invariant.md`
- `../../shared/references/success-criteria-review.md`
- `../../shared/references/source-bound-records.md`
- `../../shared/references/fresh-eye-subagent-review.md`
