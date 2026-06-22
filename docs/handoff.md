# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff entries + live open issues. `## Next Session` is
  sequencing judgment, not the full queue — **body-read the issues, don't trust it flat.**
- Refresh: `git status -sb`, `git log --oneline origin/main..HEAD`,
  `gh issue list --state open --limit 50`, and skim `git log --oneline -10`
  (de-stale the queue against what recently shipped). Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Quality reference disposition SETTLED** (2026-06-21): 41-ref merit map → **7
  route-it + 2 merge-retire, 0 deletes**; "un-routed ≠ worthless, defect is a
  discoverability gap not bloat"; blind A/B **7/7 reach-via-pointer**. Treat ref
  value as decided; deletion reopens only on the gate-sufficiency axis (see START
  HERE). [disposition](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).
- **Skill claim-fidelity harness DONE; first verdict `reject`.** A real isolated
  `/charness:quality` run opened **0/39** of its references; cautilus → `reject`
  (failed `skill_task_fidelity` + `runtime_budget_respect`). KEY: **execution
  shape** (gate-driven run never reaches the judgment/ref phase), NOT a ref-value
  verdict (settled above).
  [finding](../charness-artifacts/cautilus/quality-claim-fidelity-2026-06-22/finding.md)
  · [harness](../evals/cautilus/quality-claim-fidelity/README.md);
  issues charness#397 (open), cautilus#49 (closed-resolved).
- **Gotcha:** `/charness:quality` loads from the INSTALLED clone
  `~/.agents/src/charness` — isolate per-run via
  [capture-skill-run.sh](../scripts/agent-runtime/capture-skill-run.sh) (never edit
  the clone). `cautilus evaluate *` is operator-gated. Cautilus is now **0.17.1**
  (harness re-verified); `charness tool update` warns when a manual tool is behind.

## Next Session

- **START HERE — skill claim-fidelity + doc-philosophy across ALL skills
  (public + support).** Framing is **SETTLED** (operator 2026-06-22): the
  **per-doc 3-way axis** — **engage-always** (a real run must read it; 0 reads =
  execution-shape defect), **on-demand** (read only when sought; claim must say
  so), **gate-sufficient** (a deterministic gate already yields its conclusion →
  **deletable**, but ONLY via this axis, NOT the rejected reachability heuristic;
  ref-value stays settled). **First move: write the methodology `spec` encoding
  the axis** — do NOT re-litigate the framing — then **pilot quality (#397)**:
  classify its 39 docs, add per-ref engagement tags to `spec.json` (the
  gates-green-but-lens discriminator), pick remediation (front-load gate triage /
  wire refs into gate findings), then fan out. Each run = expensive `claude -p`
  capture + gated `cautilus evaluate observation` (cautilus 0.17.1, re-verified).
- **C — #387 one-pass goal-closeout shape report.** Fits
  `describe_goal_closeout_shape.py` (describe-first preflight), not a new floor.
- **D — #392 gather-X honest-failure contract.** Typed result
  (`exact-acquired | blocked-by-X | auth/browser-route-required | unsupported`) +
  route-level trace + a regression fixture. Scope call at pickup (see Discuss).
- **Parked:** #394 (mutation cron-only). #371 (upstream agent-browser#1334). #391.

## Discuss

- **#392 scope (decide at pickup of D):** attempt a real exact-X route
  (browser/auth — likely infeasible) vs commit to the typed-unsupported contract.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale.

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred-decisions](./deferred-decisions.md); pin-sweep convention lives in the
  [`check_skill_contracts.py`](../scripts/check_skill_contracts.py) gate header.
