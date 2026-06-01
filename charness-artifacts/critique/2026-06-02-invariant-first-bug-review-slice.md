# Invariant-First Bug Review Slice Critique

Date: 2026-06-02

## Execution

Fresh-eye slice critique ran after Slice 3 implementation and before commit.
The review unit was the workflow-review goal's invariant-first bug review
slice, including source skills, plugin mirrors, debug artifact validation,
scaffold output, dogfood evidence, tests, and the slice packet.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice-packet.md`

## Target

Code/workflow critique for a prompt-surface and validator slice.

## Change

Slice 3 adds a general invariant-first review contract for workflow-boundary
bugs. `debug` now owns `references/invariant-first-review.md`, current debug
artifacts include `## Invariant Proof`, the scaffold emits the proof fields,
and bug-class `issue` causal review consumes the invariant substrate cite-only.

## Angles

- Invariant/proof correctness: checked producer plus final-consumer proof,
  interface-shape sibling scan, non-claims, and overfitting risk.
- Workflow/export consistency: checked source/plugin mirrors, active goal
  state, packet completeness, and handoff timing.
- Deterministic enforcement and dogfood: checked whether tests prove the
  consumer path rather than only freezing wording.
- Counterweight: separated real blockers from over-worry after folded fixes.

## Findings

### Act Before Ship

- Standalone `debug` originally had only reference prose and no final consumer
  in the debug artifact path. Folded by adding `## Invariant Proof` to current
  debug artifact validation, scaffold output, `debug` output shape, focused
  tests, and plugin mirrors.
- The first tests leaned too much on whole-file string checks and line-break
  phrasing. Folded by scoping assertions to markdown sections and by adding
  validator/scaffold tests that exercise the real debug artifact consumer path.
- The first packet only had changed surfaces and non-goals. Folded by adding a
  `Slice Review Contract` section with intent, invariant, proof, non-claims,
  out-of-scope lines, and reviewer questions.
- Active goal and handoff still needed closeout updates before commit. Folded
  in the slice closeout edits.

### Bundle Anyway

- Cleaned dogfood review dates for changed public skill evidence.
- Kept the new source reference, plugin mirror, and packet in the commit.
- Tightened stale packet wording so the proof line reflects checks that passed
  after folded edits.

### Valid But Defer

- The validator only requires non-empty invariant proof fields and allows
  scaffolded `n/a` defaults for non-workflow bugs. This is intentional for
  Slice 3; stricter misuse detection should wait for dogfood evidence.
- Maintained Cautilus scenarios were reviewed but not changed:
  `debug-adapter-bootstrap` still owns debug routing/bootstrap, while
  `issue-sibling-search-concept-fixtures` and `representative-skill-contracts`
  still own issue routing and sibling-search concepts. The new invariant proof
  behavior is deterministic artifact-consumer coverage, not a routing scenario
  change.
- The broad sibling-pattern audit and disposition matrix remain Slice 4.

### Over-Worry

- The implementation is not overfit to #275/#276: the reference is framed
  around producer, signal, final consumer, interface shape, and non-claims.
- Source/plugin mirror drift was not present after sync.
- The remaining reference-string tests are acceptable contract pins because
  the real proof path now runs through the scaffold and validator.

## Counterweight Triage

- `Act Before Ship`: update active-goal state and include new files.
- `Bundle Anyway`: refresh packet proof wording and handoff closeout language.
- `Valid but Defer`: future stricter semantic detection for `n/a` misuse, and
  Slice 4 sibling-pattern disposition.
- `Over-Worry`: blocking on exact-prose guard concerns after the validator and
  scaffold consumer path were added.

## Deliberately Not Doing

- Not adding a provider/runtime proof claim; this slice is local deterministic
  skill and artifact validation.
- Not changing the root startup `find-skills` rule.
- Not filing new issues or closing additional GitHub issues.
- Not completing the broad sibling-pattern audit in this slice.

## Next Move

Complete Slice 3 closeout with the focused and slice-level validators, then
commit and push. Continue the active goal with Slice 4 sibling-pattern scan and
disposition findings.
