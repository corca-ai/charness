# Skill Ergonomics

When a repo authors skills, `quality` should review their ergonomics explicitly,
not only their syntax, metadata, or link validity.

Use this lens to keep public/support skills aligned with:

- less is more
- progressive disclosure
- the model is smart, so defaults and inference should beat user-facing mode
  proliferation when the distinction is not safety-critical

## Review Questions

Stable review topics emitted by `inventory_skill_ergonomics.py`:

- `helper_owned_workflow_packet`
- `concept_split_references`

- Is `SKILL.md` core still concise enough to be a trigger contract and decision
  skeleton rather than a second reference manual?
- Does the core own selection and sequencing, while `references/` and
  `scripts/` deepen the chosen move instead of forking the workflow?
- When code already knows the workflow, should a planner/report packet tell the
  agent what to read and run next instead of preserving gate order as prose?
- Did a compression move create one large mixed-purpose reference, or did it
  separate concepts so each reference teaches one thing?
- Are explicit modes, flags, or options doing real safety work, or are they
  compensating for weak defaults?
- Would a cold reader know when to use this skill instead of a nearby one, or
  is there trigger overlap / undertrigger risk?
- If this is a support skill hidden from the public list, can `find-skills`
  surface it from workflow language, file shapes, syntax, report names, or
  runtime commands without the user naming the support skill directly?
- Does the skill still rely on repeated prose ritual where a helper script or
  validator should own the behavior?
- Do validators pin exact prose because it is truly load-bearing classifier
  input, or because no one wrote a reference-aware or behavior-level assertion?
- Do issue anchors, dated incidents, or host-surface references document stable
  portable behavior, or are they leaking repo-local history and host policy into
  the package?
- Are reference files discoverable from `SKILL.md` when a cold reader follows
  progressive disclosure?

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
- concrete issue anchors anywhere in a public/support skill package, which can
  leak repo-local history into portable skill bundles
- dated incident or history-coupled wording anywhere in a public/support skill
  package
- host-surface references that need review before treating the package as host
  portable
- reference files that are not listed from `SKILL.md`, which makes the package
  hard to operate under line-budget pressure
- deterministic-helper pressure: a skill that lists many helper/gate commands in
  prose may need a planner/report packet, not another paragraph
- concept-mixed references: a large reference that carries several independent
  ideas may need a Raskin-style split before the core is compressed further

Treat these as prompts, not automatic failures.

Inventory status must separate scope from quality judgment:

- `scope_status=scanned` means at least one skill was inspected.
- `scope_status=unconfigured_no_skill_surface`, `configured_scope_empty`, or
  `empty_requested_scope` means the inventory did not inspect a meaningful
  skill surface; do not summarize that as "no issues."
- `finding_status=zero_heuristic_findings` means the current heuristics found
  no structural pressure, not that the skills are healthy. Prose review remains
  required for trigger boundaries, progressive-disclosure honesty, and
  judgment-only risks.
- `finding_status=heuristics_present` means the inventory has concrete prompts
  for a human quality pass.

Fail-closed now:

- oversized `SKILL.md` core
- public `## Bootstrap` with 3+ fenced examples and no repo-owned helper script

Advisory only unless the repo explicitly opts in:

- long core body
- mode/option pressure terms
- progressive-disclosure risk
- repeated bootstrap fences without a helper script
- installed-bundle helper-path ambiguity review
- package-level concrete issue-anchor review
- package-level dated incident/history review
- package-level host-surface reference review
- reference discoverability review
- trigger overlap / undertrigger review
- broader progressive-disclosure judgment
- planner/report-packet opportunity review
- concept separation review for references

When a repo opts into `skill_ergonomics_gate_rules`, keep the rule values valid
and machine-readable. `bootstrap_adapter.py` will refuse to rewrite an adapter
that sets invalid ergonomics rules, because silently clearing them would hide
operator intent.

Package-level concrete issue anchors and dated incidents are clean enough in the
current corpus to be default blocking rules. Host-surface references and
reference discoverability remain opt-in review signals until their exception
model and false-positive posture are narrower.

When a repo has discoverable skills but `skill_ergonomics_gate_rules: []`, the
validator should still return success, but it must emit a structured warning.
An empty rule list means the inventory is advisory-only and no skill structure
heuristic is enforced. The standing quality runner should surface that warning
even on a passing phase.
