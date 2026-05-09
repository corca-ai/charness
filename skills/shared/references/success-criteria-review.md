# Success Criteria Review

Use this when a concept, contract, skill change, release, or first-touch
narrative needs sharper success criteria before implementation or closeout.
The review uses a future successful outcome as evidence pressure, then
translates that outcome back into checkable criteria.

This is the shared home for preparade-style thinking, but the public trigger is
success criteria: what would make the work count as successful, what would prove
that, and what early signal would show the success path is not materializing.

## Core Move

Ask the success case first:

- If this worked better than expected, what became true?
- Which actor took the intended next action without extra explanation?
- Which early choice, default, proof, or artifact made that success likely?
- Which success claim would be misleading unless it had a concrete check?

Then translate the answer into:

- `Success Criteria`: stable outcomes, not aspirations
- `Acceptance Checks`: executable, reviewable, or artifact-backed proof
- `Tripwires`: early signals that the success path is failing
- `Deliberately Not Doing`: attractive success stories outside this slice

## Review Weight

Use the lightest honest reviewer path.

- Routine low-risk shaping may run inline.
- Non-trivial public skill, prompt, first-touch doc, release, or workflow
  changes should use one bounded fresh-eye subagent focused on overstated
  success and missing proof.
- Broad or high-risk decisions should pair this review with `critique`:
  success criteria review owns the success path; `critique` owns failure
  angles and counterweight triage.

When this review uses a subagent, follow
[fresh-eye-subagent-review.md](./fresh-eye-subagent-review.md) before reporting
the canonical reviewer path as blocked.

## Guardrails

- Do not keep a happy-path story that does not become criteria, checks, or
  tripwires.
- Do not use the success case to expand scope unless the current slice's
  success would otherwise be fake.
- Do not treat stakeholder enthusiasm, cleaner prose, or local command success
  as proof without naming the actor behavior or artifact boundary it changes.
- Do not duplicate `critique`: this review sharpens what success means, while
  `critique` tests why the decision might fail.
