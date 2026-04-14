# Skill Ergonomics

When a repo authors skills, `quality` should review their ergonomics explicitly,
not only their syntax, metadata, or link validity.

Use this lens to keep public/support skills aligned with:

- less is more
- progressive disclosure
- the model is smart, so defaults and inference should beat user-facing mode
  proliferation when the distinction is not safety-critical

## Review Questions

- Is `SKILL.md` core still concise enough to be a trigger contract and decision
  skeleton rather than a second reference manual?
- Does the core own selection and sequencing, while `references/` and
  `scripts/` deepen the chosen move instead of forking the workflow?
- Are explicit modes, flags, or options doing real safety work, or are they
  compensating for weak defaults?
- Would a cold reader know when to use this skill instead of a nearby one, or
  is there trigger overlap / undertrigger risk?
- Does the skill still rely on repeated prose ritual where a helper script or
  validator should own the behavior?

## Advisory Inventory

Use `scripts/inventory_skill_ergonomics.py` when skills are in scope.

The helper stays advisory on purpose. It does not claim to prove good taste or
correct trigger boundaries. It only inventories signals that deserve a human
quality pass:

- core line count pressure
- progressive-disclosure risk when a large core has no references or scripts
- repeated `mode` / `option` language that may signal unnecessary user-facing
  branching
- multiple code fences without helper scripts, which can signal prose ritual

Treat these as prompts, not automatic failures.
Some repos may still promote the lowest-noise cases into standing validation,
for example an oversized `SKILL.md` core or a public skill that accumulates
multiple fenced examples without any repo-owned helper script.
Higher-noise rules such as mode/option pressure should stay advisory unless the
repo explicitly opts in through `skill_ergonomics_gate_rules`.
