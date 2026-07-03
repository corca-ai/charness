# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Reference-compaction: churn sweep + rationale-accuracy audit CLOSED; the live frontier is the
  SKILLS-WIDE pass tail** — context-tax measurement design + inventory-dispatch demote (see Next
  Session), grounded in [skill-anatomy-map.md](../charness-artifacts/reference-compaction/skill-anatomy-map.md)
  and [intent.md](../charness-artifacts/reference-compaction/intent.md) §"Held open".

## Current State

- **Churn sweep DONE + released (v0.60.0); do NOT re-open.** Only quality/debug/retro/achieve had
  real churn — all FIXED; everything else ABSENT. Two old items dispositioned (persist-helper transfer
  not warranted; debug-memory RCF deferred = measurement-validity). Record:
  [churn-sweep-completion.md](../charness-artifacts/reference-compaction/churn-sweep-completion.md).
- **This session mapped the skill surface + tested the inlining.** Built
  [skill-anatomy-map.md](../charness-artifacts/reference-compaction/skill-anatomy-map.md) (20 skills:
  intent · body support · 185 refs grouped engage-always/on-demand/gate-sufficient). Fresh-eye
  delete-safety on 6 INLINE/DEPTH candidates = **0/6 delete-safe** — the inlining is SOUND (gist in
  body, real trigger-gated depth in the doc; not DUP), re-confirming the 0/17 finding.
- **Rationale-accuracy audit DONE (1b):** all 15 INLINE-ref spec rationales grep-verified vs their
  SKILL.md body (fan-out + adversarial verify + fresh-eye). **4 FIXED** (achieve/coordination,
  announcement/adapter-contract, impl/review-gate, spec/fixed-probe-defer), 1 refuted, 10 accurate.
  Drift is locator/attribution, not fabricated gist; census INLINE calls all sound. Record:
  [rationale-accuracy-audit.md](../charness-artifacts/reference-compaction/rationale-accuracy-audit.md).

## Next Session

1. **Reference-compaction pass tail (primary, grounded in the anatomy map):**
   a. **Systemic context-tax** — how a skill's overhead taxes reasoning across a WHOLE session (the
      symptom capture can't see); measurement approach still unsolved — design it (intent §"Held open").
   b. **inventory-dispatch demote** — quality's 297-line always-load is DEPTH, not deletable; add a
      machine-readable `scripts:` routing layer to catalog.yaml so the planner briefs the routing, then
      the doc demotes (mirror the prune-brief pilot). Touches skills broadly.
2. Optional test-packaging tail: the borderline ~6-8 fn
   [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py) subset — confirm
   cleaner (declarative, LOC-neutral) else skip; fresh-eye + commit each batch.

## Discuss

- KEPT deliberately: the 3 usage-episodes plugin bundle smokes — the only end-to-end proof the bundle runs.
- Brittle: [test_handoff_plan.py](../tests/test_handoff_plan.py) reds broad pytest on any >=60-line
  handoff — keep THIS file under 60 lines.
- Compaction lesson: INLINE != DUP. The reviewed docs keep real single-sourced depth beyond the inlined
  gist; the lever is NOT deletion but accurate rationales + demote-via-briefing (spec's proven shape).

## References

- pickup: [skill-anatomy-map.md](../charness-artifacts/reference-compaction/skill-anatomy-map.md) · [rationale-accuracy-audit.md](../charness-artifacts/reference-compaction/rationale-accuracy-audit.md) · [intent.md](../charness-artifacts/reference-compaction/intent.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
