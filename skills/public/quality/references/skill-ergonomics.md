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

Use `$SKILL_DIR/scripts/inventory_skill_ergonomics.py` when skills are in scope.

The helper stays advisory on purpose. It does not claim to prove good taste or
correct trigger boundaries. It only inventories signals that deserve a human
quality pass:

- core line count pressure
- progressive-disclosure risk when a large core has no references or scripts
- repeated `mode` / `option` language that may signal unnecessary user-facing
  branching
- multiple code fences without helper scripts, which can signal prose ritual
- prose helper-path ambiguity where bare `<repo-root>/scripts/...` or source-tree file paths
  can be misread as runtime instructions outside the source checkout

Treat these as prompts, not automatic failures.

Fail-closed now:

- oversized `SKILL.md` core
- public `## Bootstrap` with 3+ fenced examples and no repo-owned helper script

Advisory only unless the repo explicitly opts in:

- mode/option pressure terms
- progressive-disclosure risk
- installed-bundle helper-path ambiguity review
- trigger overlap / undertrigger review
- broader progressive-disclosure judgment

When a repo opts into `skill_ergonomics_gate_rules`, keep the rule values valid
and machine-readable. `bootstrap_adapter.py` will refuse to rewrite an adapter
that sets invalid ergonomics rules, because silently clearing them would hide
operator intent.
