# Decision-Question Response

Use this when the user asks a decision-shaped question instead of a broad
brainstorm or a direct implementation request.

Typical design or workflow decision prompts include:

- "what do we need to decide?"
- "what decision issues are still open?"
- "which direction is better?"
- "뭘 결정해야 하죠?"
- "결정할 쟁점은?"
- "어떤 방향이 나아?"

## Response Frame

Answer with the decision frame first:

1. the core decision to make
2. 2-4 realistic options
3. the tradeoffs for each option
4. one recommended option
5. why that option is recommended
6. what happens next if that option is chosen

Keep the options realistic, not exhaustive. If the best answer is obvious from
repo context, recommend it and say why instead of opening a large choice menu.

## Routing Boundary

Use `ideation` when the question is still shaping the concept or work direction.
Use `spec` when the decision locks build scope, acceptance, sequencing, or
public contract vocabulary.

Do not route an ordinary decision-shaped prompt through `find-skills` just
because several skills are nearby. `find-skills` is still correct when the user
explicitly asks which skill, support capability, helper, or integration should
handle the task.

If "issues" means bug findings, PR review comments, CI failures, release
blockers, validation findings, or GitHub issues, use the workflow for that
concrete surface instead of forcing this decision frame.

## Guardrails

- Do not jump into implementation before the decision frame is legible.
- Do not make the frame mandatory ceremony for a concrete implementation request
  whose next step is already clear.
- Do not present more than four options unless the user asks for an exhaustive
  map.
- Do not leave the recommendation implicit when tradeoffs are real.
