---
name: spec
description: Use when the concept is coherent enough to turn into an implementation contract. Consume ideation documents or an existing concept summary, reduce only the remaining ambiguity, define success criteria and constraints, and produce a spec that `impl` can execute without rediscovering the problem.
---

# Spec

Use this when the concept is stable enough that the next job is to define what
should be built and how success will be judged.

## Bootstrap

Read the current concept artifacts before inventing new structure.

```bash
# 1. current concept and adjacent context
rg --files docs skills
sed -n '1,220p' docs/handoff.md
sed -n '1,220p' skills/public/ideation/SKILL.md

# 2. existing concept/spec/design docs
rg -n "concept|spec|requirements|success criteria|acceptance|entity|stage|constraint" .

# 3. implementation-side neighbors
sed -n '1,220p' skills/public/create-skill/SKILL.md
```

If an ideation document already exists, refine it into a spec. Do not restate
the entire discovery history from scratch.

## Workflow

1. Ingest the current concept.
   - identify the source artifact or source summary
   - restate the stable idea in implementation terms
   - separate what is already decided from what is still ambiguous
2. Reduce only the ambiguity that blocks implementation.
   - ask targeted questions only for choices that change build scope,
     acceptance, sequencing, or risk
   - if a reasonable default is clear, recommend it with reasons instead of
     opening broad option trees
3. Define the execution contract.
   - scope
   - non-goals
   - constraints
   - success criteria
   - acceptance checks
   - open risks or deferred decisions
4. Make the spec implementation-ready.
   - enough detail for `impl` to act without rediscovering the concept
   - explicit enough that success and failure are testable
   - narrow enough that it does not silently expand back into ideation
5. End with the next handoff.
   - whether the spec is ready for `impl`
   - what the first implementation slice should be
   - which artifact should be the canonical reference during implementation

## Output Shape

The final spec should usually include:

- `Problem`
- `Scope`
- `Non-Goals`
- `Constraints`
- `Success Criteria`
- `Acceptance Checks`
- `Open Questions`
- `First Implementation Slice`

If the idea depends on durable structure or flow, reuse ideation outputs such as
`Entities` or `Stages` instead of recreating them under new names.

## Guardrails

- Do not reopen broad concept exploration that belongs in `ideation`.
- Do not leave success criteria as vague aspirations.
- Do not silently assume implementation details when they materially change scope.
- If the concept artifact is still unstable, send the work back to `ideation`
  rather than writing a fake spec.
- A good spec refines an existing concept artifact; it does not discard it.
- Keep host-specific file locations or template choices outside the core skill
  body; use repo documents or adapters where needed.

## References

- `references/ingest-and-refine.md`
- `references/success-criteria.md`
- `references/ambiguity-rules.md`
- `references/ideation-boundary.md`
- `references/document-seams.md`
