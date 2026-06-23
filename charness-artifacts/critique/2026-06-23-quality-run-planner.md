# Critique Review
Date: 2026-06-23

Packet Consumed: current working diff for quality run planner
Decision Path:
charness-artifacts/goals/2026-06-23-skill-claim-fidelity-doc-philosophy.md

## Decision Under Review

Add a small `quality` helper, `plan_quality_run.py`, and wire it into the
public `quality` workflow so a run starts with scope detection,
`required_primer_refs`, `gate_plan: report_first`, and `next_action:
read_primer_refs` before broad gates or fixes.

## Failure Angles

- Fresh-eye reviewer found the direction sound: the planner fixes ordering
  without replacing quality judgment and keeps skill references conditional.
- Medium finding: the first `on_demand_trigger_map` listed only common triggers,
  which could weaken the three-way classification if the planner became the
  next-action authority.
- Low finding: skill scope detection handled root `skills/public` and
  `skills/support`, but not plugin-only skill-authoring repos.
- Low finding: `SKILL.md` step 2 still mentioned `inventory-dispatch.md` before
  the planner step, leaving a small ordering ambiguity.

## Counterweight Pass

Act before ship: folded all three findings. The planner now carries all 27
on-demand reference triggers from the quality claim-fidelity classification,
falls back to checked-in `plugins/*/skills/*/SKILL.md` when no root skill source
exists, and the quality workflow now says inventory dispatch happens after the
planner primer.

Bundle anyway: the planner intentionally does not classify quality findings or
choose fixes. It only fixes phase order and repo-scope detection so the model
has to do judgment after the deterministic report.

Over-worry: root `skills/` remains the canonical source when present, so the
Charness checked-in plugin mirror is not double-counted as authored skill
surface.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/plan_quality_run.py | action: fix | note: expanded on-demand trigger map to all 27 on-demand refs
- F2 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/plan_quality_run.py | action: fix | note: added plugin-only skill authoring fallback when root skills are absent
- F3 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/SKILL.md | action: fix | note: clarified inventory dispatch follows the planner primer

## Reviewer Tier Evidence

- Requested tier: default inherited subagent
- Requested spawn fields: default inherited model, reasoning effort, and service tier
- Host exposure state: host-defaulted
- Application state: one fresh-eye read-only reviewer completed; findings folded
  before validator closeout
