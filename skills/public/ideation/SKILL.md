---
name: ideation
description: "Use when the user is still shaping a product, system, or workflow concept and needs discovery before `spec` or implementation. Build the concept through conversation because the user may not know the full shape yet: maintain a living world model, separate verified facts from assumptions, test demand/status quo/wedge/moat early, think about feedback and expansion from the start, and treat agents, APIs, CLI, and interface choices as first-class design constraints."
---

# Ideation

Use this when the request is still under-shaped and the goal is to turn vague
intent into a sharper, more defensible concept.

Use Daniel Jackson-style concept discipline when the question is whether the
current idea is one clear user-facing concept, whether boundaries are honest,
and which ambiguities are upstream enough that they should be decided first.
Keep Christopher Alexander-style sequence discipline in the background:
resolve the upstream question that most changes the rest of the design before
hardening downstream detail; use `../../shared/references/generative-sequence.md`
only when order changes correctness, uncertainty, or downstream unlocks. When uncertainty is high and the next move should
start from available means, affordable loss, or early stakeholder commitment,
borrow Saras Sarasvathy-style effectuation. When the concept is really a system
of actors, feedback loops, or leverage
points, borrow Donella Meadows-style systems thinking so the design pressure is
traced to structure instead of dissolving into a feature wish list. See
`references/sequence-discipline.md` and `references/effectuation.md`.

When the user asks a design or workflow decision-shaped question such as "what
do we need to decide?", "what decision issues are still open?", "뭘 결정해야
하죠?", or "결정할 쟁점은?", answer with a decision frame before implementation:
the core decision, 2-4 options, tradeoffs, one recommendation, why, and the next
step. See `references/decision-question-response.md`.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`. Read only
the context that reduces uncertainty for the current idea. Before asking
clarification questions, inspect the current repo reality first so existing
code, tests, and operator docs can retire fake ambiguity early.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. repo and adjacent design context
git status --short
rg --files . | sed -n '1,200p'
sed -n '1,220p' README.md 2>/dev/null || true
sed -n '1,220p' AGENTS.md 2>/dev/null || true
sed -n '1,220p' docs/handoff.md 2>/dev/null || true

# 2. existing concept, design, and acceptance signals when they exist
rg -n "idea|concept|design|entity|stage|workflow|user|customer|problem|acceptance|constraint|success criteria" .

# 3. adjacent charness skill boundaries
sed -n '1,220p' "$SKILL_DIR/../create-skill/SKILL.md" 2>/dev/null || true
sed -n '1,220p' "$SKILL_DIR/../retro/SKILL.md" 2>/dev/null || true

# 4. scaffold the ideation record to write (validator-passing skeleton)
python3 "$SKILL_DIR/scripts/scaffold_ideation_artifact.py" --repo-root . --json
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
   - `concept lens`: use Daniel Jackson-style discipline to test whether the
     concept is one clear user-facing unit with honest boundaries
   - `capability lens`: name the actor, the capability or capability failure,
     the current workaround, and the threshold where a feature actually improves
     what the actor can do
   - `truth lens`: pain, customer, status quo, demand evidence
   - `world lens`: durable entities, relationships, constraints
   - `stage lens`: chronology, checkpoints, state transitions
   - `decision lens`: sort ambiguities by downstream impact and dependency
     order so the highest-leverage upstream choice is handled first
   - before introducing a new user-facing mode, kind, strategy, profile, or
     target, run the `spec` taxonomy-axis checkpoint so objective, evidence,
     trigger, policy, and internal presets do not collapse into one enum
   - `effectuation lens`: available means, affordable loss, stakeholder
     commitments, and useful contingencies when the idea is still highly
     uncertain
   - `edge lens`: wedge, moat, hard part worth doing, easy experiment worth trying first
   - `feedback lens`: early feedback loops, distribution posture, viral hooks when relevant, expansion surfaces
   - `agent-human lens`: agent-first surfaces, API/CLI/skill priority, interface importance, human cognition and social behavior
   - `success criteria lens`: use future-success review to turn a promising
     idea into criteria, checks, tripwires, and the first probe
3. Ask the smallest set of high-leverage questions.
   - check the current repo surfaces first and treat existing code, tests, and
     operator docs as evidence rather than reopening them as chat-only questions
   - when multiple decisions are open, start with the upstream one that most
     changes the rest of the design while preserving later paths
   - ask one question at a time when real tradeoffs remain
   - prefer precise questions over broad brainstorming prompts
   - skip questions the repo, docs, or prior answers already resolved
   - stop once the concept is sharp enough to move forward
4. Surface weak concepts early.
   - contradictions
   - hidden assumptions
   - solution-in-search-of-problem patterns
   - feature lists that never name the new capability or failed capability
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
- `Capability or Capability Failure`
- `Product Posture`
- `Verified Facts`
- `Assumptions`
- `Open Questions`
- `Decision Candidates`
- `Dependency Order`
- `Recommended Current Decision`
- `Alternatives and Tradeoffs`
- `World Model`
- `Truth Tests`
- `Edge and Expansion`
- `Agent/Human Fit`
- `Next Step`

If entity/stage separation materially clarifies the idea, also include:

- `Entities`
- `Stages`

Use that split as a thinking aid, not as mandatory ceremony.

When the open questions are ones a downstream skill (`spec` or `impl`) must act
on, emit an opt-in `## Structured Questions` section that classifies each item
by `urgency`, `depends-on`, and `action` so the next skill does not re-triage
prose bullets. The schema, enums, and the section-gated validator are owned by
`references/structured-questions.md`. Prose-only output stays valid.

## Guardrails

- Do not jump into implementation while the concept is still unstable.
- Do not flatten several upstream decisions into one vague brainstorming blob.
- Do not leave the current recommended decision implicit when tradeoffs are real.
- Do not ask questions the repo, code, tests, docs, or provided context can
  already answer.
- If the user already has a formed plan, still challenge demand, wedge, moat,
  feedback path, and agent/human fit before handing off to `spec`.
- Do not leave the durable concept model stale when the discussion materially
  changed it.
- Apply the lens-specific cautions at their reference home: product posture gates
  which growth questions apply (`references/truth-and-edge.md`), entity/stage
  separation is optional and only when it clarifies (`references/world-modeling.md`),
  and agent-first is not interface-agnostic — interface design still shapes
  adoption (`references/agent-human-lens.md`).
- Keep the result decisive. `Ideation` should reduce ambiguity, not narrate an
  endless discovery session.

## References

- `references/concept-architecture.md`
- `references/truth-and-edge.md`
- `references/world-modeling.md`
- `references/agent-human-lens.md`
- `references/effectuation.md`
- `references/sequence-discipline.md`
- `references/spec-boundary.md`
- `references/decision-question-response.md`
- `references/structured-questions.md`
- `../spec/references/taxonomy-axis-checkpoint.md`
- `../../shared/references/success-criteria-review.md`
