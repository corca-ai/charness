# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Reference-compaction churn sweep is COMPLETE** (see Current State). Primary next
  action is the intent's held-open **systemic context-tax** frontier — read
  [intent.md](../charness-artifacts/reference-compaction/intent.md) §"Held open" +
  [churn-sweep-completion.md](../charness-artifacts/reference-compaction/churn-sweep-completion.md) first.

## Current State

- **Churn sweep DONE + released (v0.60.0).** Every scaffold-gated artifact skill cold
  static-confirmed (fresh-eye each); pure-writer/no-gate skills ABSENT-by-construction.
  Only quality/debug/retro/achieve had real churn — all
  FIXED (achieve false-green = `591c1652`, surfaces `invalid_early_close_reports`). All
  others ABSENT (surfaced-format, no-gate, or one-pass persist-helper). Owning record:
  [churn-sweep-completion.md](../charness-artifacts/reference-compaction/churn-sweep-completion.md).
- **The two old open items are dispositioned — do NOT re-open as fixes:** persist-helper
  transfer = NOT warranted (no un-fixed churn skill; release already is one); debug-memory
  RCF = DEFERRED (measurement-validity + DEAD token swap per apparatus-floor-audit; the
  real sub-lever is a behavioral memory-consumption internalization needing a capture).
- Earlier diagnosis threads stay closed: redundancy 0/17 delete-safe; apparatus 76%+
  well-shaped ([apparatus-floor-audit.md](../charness-artifacts/reference-compaction/apparatus-floor-audit.md)).

## Next Session

1. **Systemic context-tax frontier (primary, genuinely open):** how a skill's overhead
   taxes reasoning across a WHOLE session (the symptom single-run capture can't see).
   The measurement approach is unsolved — design it. Scope: intent.md §"Held open".
2. Optional test-packaging tail: the borderline ~6-8 fn
   [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py) subset —
   confirm genuinely cleaner (declarative, LOC-neutral) else skip; fresh-eye + commit each batch.

## Discuss

- KEPT deliberately: the 3 usage-episodes plugin bundle smokes — the only end-to-end
  proof the shipped plugin bundle runs. Do not delete.
- Brittle: [test_handoff_plan.py](../tests/test_handoff_plan.py) reds broad pytest on any
  >=60-line handoff — keep THIS file under 60 lines.
- Churn-sweep lesson: churn is RARE; the fix is always surface-it (channel intelligence via
  planner/scaffold stdout) or a persist-helper stamp — never a new floor. Fresh-eye
  refutation, not a capture, earns each PRESENT/ABSENT call.

## References

- pickup: [churn-sweep-completion.md](../charness-artifacts/reference-compaction/churn-sweep-completion.md) · [intent.md](../charness-artifacts/reference-compaction/intent.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
