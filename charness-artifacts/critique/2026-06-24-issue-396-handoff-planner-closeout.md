# issue 396 handoff planner closeout
Date: 2026-06-24

## Decision Under Review

Close #396 with a direct commit that moves stale rolling-pointer freshness
checks from pre-push into the staged commit plan and converts `handoff`
startup to a planner-first flow.

## Failure Angles

- Handoff operator path: the first staged SKILL bootstrap command omitted
  invocation context, so a bare `/handoff` following the documented command
  would not deterministically fire chunked routing. Finding: act before ship.
  The bootstrap now passes `--invocation-text "<current user request>"` and
  says to add `--invoked-directly` for a bare direct invocation; tests pin
  `/handoff` routing.
- Freshness gate coverage: the first staged gate list covered named pointer
  surfaces but not generic `scripts/*.py` renames/deletes that
  `charness-artifacts/quality/latest.md` can cite in backticked commands.
  Finding: act before ship. The staged plan now pulls the freshness validator
  for `scripts/*.py` changes too.
- Exported-skill portability: `required_reads` mixed repo-relative artifact
  paths with skill-relative references/scripts without labeling their base.
  Finding: act before ship. Planner read entries now include `base: repo` or
  `base: skill`.

## Counterweight Pass

- Act before ship: apply the three fresh-eye fixes before committing, then rerun
  staged closeout and mutation coverage.
- Bundle anyway: keep the planner-first handoff change and #396 timing-layer
  gate in the same commit because they share the handoff lifecycle problem.
- Valid but defer: #399's StrykerJS score failure is real but separate and stays
  open.
- Over-worry: do not add a maintained Cautilus scenario for this slice; the
  handoff adapter bootstrap scenario is unchanged and deterministic planner
  tests cover the new behavior.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/SKILL.md:26 | action: fix | note: documented planner command must carry invocation context so bare `/handoff` can route to chunked routing
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/staged_commit_gate_plan.py:128 | action: fix | note: freshness commit-time trigger must include `scripts/*.py` because quality latest can cite repo scripts
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/plan_handoff_run.py:67 | action: fix | note: planner read entries need an explicit repo-vs-skill base for exported plugin consumers
- F4 | bin: valid-but-defer | evidence: strong | ref: https://github.com/corca-ai/charness/issues/399 | action: defer | note: #399 changed into a real JS mutation-score issue and is not closed by this slice

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none; parent used `multi_agent_v1.spawn_agent` with
  default inherited model/effort per host tool guidance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: `multi_agent_v1.spawn_agent` returned
  agent `019ef6ab-0af4-7de1-b6d1-bc018e37d68d`, and it completed via
  `wait_agent`.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. One bounded fresh-eye reviewer
completed the staged-diff review for #396 and the handoff planner change. It
found three blockers; all three were fixed before closeout was retried.
