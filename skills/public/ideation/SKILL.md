---
name: ideation
description: Use when the user is still shaping a product, system, or workflow concept and needs discovery before `spec` or implementation. Merges `interview`-style clarification with stronger concept formation: separate verified facts from assumptions, ask the smallest set of high-leverage questions, test demand/status quo/wedge when relevant, and use durable entities vs chronological stages when that makes the design clearer.
---

# Ideation

Use this when the request is still under-shaped and the goal is to turn vague
intent into a sharper concept.

## Bootstrap

Read only the context that reduces uncertainty for the current idea.

```bash
# 1. repo and adjacent design context
rg --files docs skills
sed -n '1,220p' docs/handoff.md

# 2. existing concept or design files when they exist
rg -n "idea|concept|design|entity|stage|workflow|user|customer|problem" .

# 3. adjacent charness skill boundaries
sed -n '1,220p' skills/public/create-skill/SKILL.md
sed -n '1,220p' skills/public/retro/SKILL.md
```

If the repo already contains a design doc, preserve it and sharpen it instead of
starting a parallel artifact by default.

## Workflow

1. Restate the concept in concrete terms.
   - what the user seems to want
   - who it is for
   - what is still ambiguous
2. Separate the working state.
   - verified facts
   - assumptions
   - open questions
3. Choose the shaping lens that fits.
   - `problem lens`: pain, status quo, demand reality, wedge
   - `system lens`: durable entities, relationships, constraints
   - `stage lens`: chronological flow, state transitions, checkpoints
   - use more than one lens only when it reduces confusion
4. Ask the smallest set of high-leverage questions.
   - ask one question at a time when real tradeoffs remain
   - prefer precise questions over broad brainstorming prompts
   - stop asking once the concept is strong enough to move forward
5. Surface weak concepts early.
   - contradictions
   - hidden assumptions
   - solution-in-search-of-problem patterns
   - stage confusion where durable structure and chronology are mixed together
6. End with a sharper execution frame.
   - recommended next step
   - whether the work is ready for `spec`
   - which files, artifacts, or references now matter most

## Output Shape

The final synthesis should usually include:

- `Concept`
- `Verified Facts`
- `Open Questions`
- `Design Shape`
- `Next Step`

If entity/stage separation materially clarifies the idea, also include:

- `Entities`
- `Stages`

Use that split as a thinking aid, not as mandatory ceremony.

## Guardrails

- Do not jump into implementation while the concept is still unstable.
- Do not ask questions the repo, docs, or provided context can already answer.
- If the user already has a formed plan, challenge the premise and alternatives
  briefly, then hand off to `spec`.
- Demand/status-quo/wedge questions are useful only when the concept has a real
  product or user-facing bet.
- Entity/stage separation is optional and should appear only when it improves
  clarity.
- Keep the result decisive. `Ideation` should reduce ambiguity, not narrate an
  endless discovery session.

## References

- `references/problem-framing.md`
- `references/entity-stage-lens.md`
- `references/interview-migration.md`
- `references/spec-boundary.md`
