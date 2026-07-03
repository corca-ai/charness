# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Primary next action: reference-compaction churn sweep** (test-value audit +
  Batch C are DONE). Read its contract first:
  [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
  and [intent.md](../charness-artifacts/reference-compaction/intent.md) (fewer-is-better;
  prune what doesn't earn its place).

## Current State

- **Test-value audit + Batch C DONE.** Audit removed 23 redundant tests + 2 dead
  source fns; Batch C (`7a2f8892`) folded the 2 genuinely-homogeneous prose-pin
  clusters into `parametrize` (−9 test fns, **0 collected-item delta**, LOC ~neutral).
  Standing suite green (3974); every change fresh-eye reviewed. Owning artifact:
  [test-value-audit](../charness-artifacts/quality/history/2026-07-03-pytest-suite-test-value-audit.md)
  (archived to `history/`; `quality/latest.md` now = the 0.59.0 release quality review).
- Batch C skipped 4 non-homogeneous anchors by design (rationale in the audit
  §"Deferred"). One BORDERLINE optional remains: a ~6–8 fn "dispatch + one lens ref"
  subset of [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py) could fold, but the win is marginal.
- **Reference-compaction diagnosis DONE this session (2 threads closed, do not re-open):**
  redundancy = 0/17 delete-safe (census stale, mislabels RCF floors); apparatus =
  claim-fidelity floors 76%+ well-shaped, RCF→RSF token fix DEAD (0/9 trivially-green),
  and the mis-checks are *measurement-validity, NOT a runtime tax* (faithful runs ignore
  the floors, gather 0/8) — substance-judge redesign optional/non-urgent. See
  [apparatus-floor-audit.md](../charness-artifacts/reference-compaction/apparatus-floor-audit.md),
  [compaction-plan.md](../charness-artifacts/reference-compaction/compaction-plan.md).

## Next Session

1. **Churn sweep (primary, the live-agent lever):** issue/achieve/hotl static confirm
   (predicted ABSENT) + persist-helper transfer + debug-memory RCF. Scope:
   [anti-churn-patterns.md](../charness-artifacts/reference-compaction/anti-churn-patterns.md).
   Note: churn found was trim-loop/scaffold-ceiling, NOT ritual doc-open (runs ignore those).
2. Held-open frontier (intent): systemic context-tax per-artifact audits can't see.
3. Optional test-packaging tail: the borderline [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py)
   subset — confirm genuinely cleaner (declarative, LOC-neutral) else skip; fresh-eye + commit each batch.

## Discuss

- KEPT deliberately: the 3 usage-episodes plugin bundle smokes — the only end-to-end
  proof the shipped plugin bundle runs. Do not delete.
- Brittle: [test_handoff_plan.py](../tests/test_handoff_plan.py) reds broad pytest on any
  >=60-line handoff — keep this file under 60 lines.
- Batch C lesson: `parametrize` does NOT cut collected-item count (each case is an item);
  its lever is test-FUNCTION count + declarativeness, not "count↓". Fold only genuinely
  homogeneous clusters; a multi-column flag schema is "procedure hidden in data".
- DONE (was an open follow-up; audit §"Blind spots"): test-suite duplication swept —
  `5d1684ac` (66 read_text re-reads → module constants, −111 LOC), `22ebc31a` (fixture
  helpers, −34 LOC), `e2b32f14` (AST `intra_test_reread` detector so the class is caught
  going forward). Coverage byte-identical; prod code was already clean.

## References

- pickup: [test-value-audit](../charness-artifacts/quality/history/2026-07-03-pytest-suite-test-value-audit.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
