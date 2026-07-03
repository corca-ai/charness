# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Reference-compaction: churn sweep + rationale-accuracy audit + inventory-dispatch demote CLOSED;
  the live frontier is the LAST open item — systemic context-tax measurement DESIGN** (see Next
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
- **This session DONE (both pass-tail items):** (1) **rationale-accuracy audit** — 15 INLINE-ref
  rationales grep-verified vs body; **4 FIXED** (drift is locator/attribution, not fabricated gist),
  1 refuted, 10 accurate ([rationale-accuracy-audit.md](../charness-artifacts/reference-compaction/rationale-accuracy-audit.md)).
  (2) **inventory-dispatch demote** — quality's ~297-line always-load moved required-primer->on-demand
  via a machine-readable `brief.inventory_dispatch` routing index the planner surfaces (prune-brief
  pilot pattern; consumer contract unchanged). **Deferred follow-up:** single-source the doc — trim the
  routing now duplicated in the brief; updates the 4 tests that pin its strings (mirror pilot 87922a7e).

## Next Session

1. **Systemic context-tax measurement (primary — the LAST open item; DESIGN, not code):** how a skill's
   overhead taxes reasoning across a WHOLE session (the single-run capture can't see); approach still
   unsolved (intent §"Held open"). A thinking pass — guard against building the measurement apparatus
   the intent warns is itself the overhead disease. Recommend running it as its own design session.
2. Optional: (a) the deferred inventory-dispatch doc single-source (Current State); (b) the borderline
   ~6-8 fn [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py) test-packaging
   subset — confirm cleaner (declarative, LOC-neutral) else skip; fresh-eye + commit each batch.

## Discuss

- KEPT deliberately: the 3 usage-episodes plugin bundle smokes — the only end-to-end proof the bundle runs.
- Brittle: [test_handoff_plan.py](../tests/test_handoff_plan.py) reds broad pytest on any >=60-line
  handoff — keep THIS file under 60 lines.
- Compaction lesson: INLINE != DUP. The reviewed docs keep real single-sourced depth beyond the inlined
  gist; the lever is NOT deletion but accurate rationales + demote-via-briefing (spec's proven shape).

## References

- pickup: [skill-anatomy-map.md](../charness-artifacts/reference-compaction/skill-anatomy-map.md) · [rationale-accuracy-audit.md](../charness-artifacts/reference-compaction/rationale-accuracy-audit.md) · [intent.md](../charness-artifacts/reference-compaction/intent.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
