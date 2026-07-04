# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Reference-compaction: the LAST open item (systemic context-tax measurement) is now
  DESIGNED and CLOSED as a frontier item** — the effort's open questions are all resolved
  or explicitly gated; see Current State.

## Current State

- **Context-tax measurement DESIGN done (this session).** Deliverable:
  [context-tax-measurement-design.md](../charness-artifacts/reference-compaction/context-tax-measurement-design.md).
  Core: T1 (in-session tax) / T2 (surface-encoded ritual, incl. carried-artifact loop)
  decomposition; 3 pieces — symptom ledger (seeded:
  [symptom-ledger.md](../charness-artifacts/reference-compaction/symptom-ledger.md) + one
  pointer line in operating-contract Session Discipline) · on-demand session tax audit
  (case-list, symmetric rubric, NOT built) · escalation contrast (reuses
  `run_skill_efficiency_ab.py`, own gate ≠ cautilus gate). Zero standing apparatus.
  Premortem (3 angles + counterweight, 9 edits applied):
  [2026-07-04 critique](../charness-artifacts/critique/2026-07-04-context-tax-measurement-design-premortem.md).
- **Build is deliberately GATED, not queued:** rubric + pilot audit run only after a NEW
  (post-2026-07-02) symptom-ledger entry AND a live contested decision, with operator
  approval. Do not build ahead of that trigger — that is the design's own guard.
- Churn sweep + rationale-accuracy audit + inventory-dispatch demote remain CLOSED
  (v0.60.0); do NOT re-open
  ([churn-sweep-completion.md](../charness-artifacts/reference-compaction/churn-sweep-completion.md)).

## Next Session

1. No mandatory reference-compaction work remains. Pick up from open issues
   (`/handoff` chunked routing) or operator direction.
2. Optional carry-overs: (a) inventory-dispatch doc single-source — trim routing now
   duplicated in quality's brief; updates the 4 tests pinning its strings (mirror pilot
   87922a7e); (b) borderline ~6-8 fn
   [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py)
   test-packaging subset — confirm cleaner (declarative, LOC-neutral) else skip.

## Discuss

- KEPT deliberately: the 3 usage-episodes plugin bundle smokes — the only end-to-end
  proof the bundle runs.
- Brittle: [test_handoff_plan.py](../tests/test_handoff_plan.py) reds broad pytest on any
  >=60-line handoff — keep THIS file under 60 lines.
- Evidence posture on context tax: one pre-effort anecdote FOR, two post-effort audits
  cold — the design leads with that balance; the ledger is the only standing sensor.

## References

- pickup: [context-tax-measurement-design.md](../charness-artifacts/reference-compaction/context-tax-measurement-design.md) · [intent.md](../charness-artifacts/reference-compaction/intent.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
