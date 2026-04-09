---
name: ideation
description: Use when the user is still shaping a product, system, or workflow concept and needs discovery before `spec` or implementation. Build the concept through conversation because the user may not know the full shape yet: maintain a living world model, separate verified facts from assumptions, test demand/status quo/wedge/moat early, think about feedback and expansion from the start, and treat agents, APIs, CLI, and interface choices as first-class design constraints.
---

# Ideation

Use this when the request is still under-shaped and the goal is to turn vague
intent into a sharper, more defensible concept.

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

If the repo already contains a design or concept doc, preserve it and sharpen it
instead of starting a parallel artifact by default.

If the concept keeps evolving across turns, update the working documents
incrementally instead of leaving the model only in chat.

## Workflow

1. Establish a living concept model.
   - restate what the user seems to want
   - record verified facts, assumptions, open questions, and candidate direction
   - keep updating this model as the conversation evolves because neither the
     user nor the agent can rely on perfect working memory
   - when the idea has durable structure, update the working document or docs at
     each meaningful step
2. Choose the shaping lenses that fit.
   - `truth lens`: pain, customer, status quo, demand evidence
   - `world lens`: durable entities, relationships, constraints
   - `stage lens`: chronology, checkpoints, state transitions
   - `edge lens`: wedge, moat, hard part worth doing, easy experiment worth trying first
   - `feedback lens`: early feedback loops, distribution posture, viral hooks when relevant, expansion surfaces
   - `agent-human lens`: agent-first surfaces, API/CLI/skill priority, interface importance, human cognition and social behavior
3. Ask the smallest set of high-leverage questions.
   - ask one question at a time when real tradeoffs remain
   - prefer precise questions over broad brainstorming prompts
   - skip questions the repo, docs, or prior answers already resolved
   - stop once the concept is sharp enough to move forward
4. Surface weak concepts early.
   - contradictions
   - hidden assumptions
   - solution-in-search-of-problem patterns
   - no real customer pain or no concrete actor
   - no wedge, no moat hypothesis, or no feedback path
   - stage confusion where durable structure and chronology are mixed together
   - agent-native claims that collapse when the interface or runtime is examined
5. Keep the concept cumulative.
   - rewrite obsolete parts instead of preserving contradictory models
   - if entity/stage separation clarifies the design, maintain both views
   - if a hard direction is promising, name why it creates edge
   - if a simple experiment is better, name what it should validate first
   - if the product posture changes, rewrite the world model to match the new posture instead of layering both
6. End with a sharper execution frame.
   - recommended next step
   - whether the work should stay in `ideation`, move to `spec`, or run a quick validation loop first
   - which files, artifacts, or references now matter most

## Output Shape

The final synthesis should usually include:

- `Concept`
- `Product Posture`
- `Verified Facts`
- `Assumptions`
- `Open Questions`
- `World Model`
- `Truth Tests`
- `Edge and Expansion`
- `Agent/Human Fit`
- `Next Step`

If entity/stage separation materially clarifies the idea, also include:

- `Entities`
- `Stages`

Use that split as a thinking aid, not as mandatory ceremony.

## Guardrails

- Do not jump into implementation while the concept is still unstable.
- Do not ask questions the repo, docs, or provided context can already answer.
- If the user already has a formed plan, still challenge demand, wedge, moat,
  feedback path, and agent/human fit before handing off to `spec`.
- Do not leave the durable concept model stale when the discussion materially
  changed it.
- Demand, status quo, wedge, moat, and feedback questions matter whenever the
  concept implies a real product, workflow, or operational bet.
- Ask about product posture before pushing hard on viral or distribution logic.
  A startup, internal tool, research system, and legacy-feature addition do not
  need the same growth questions.
- Entity/stage separation is optional and should appear only when it improves
  clarity.
- Agent-first does not mean interface-agnostic. CLI, skills, and APIs may come
  first, but interface design still matters because humans and agents both shape
  adoption.
- Keep the result decisive. `Ideation` should reduce ambiguity, not narrate an
  endless discovery session.

## References

- `references/concept-architecture.md`
- `references/truth-and-edge.md`
- `references/world-modeling.md`
- `references/agent-human-lens.md`
- `references/spec-boundary.md`
