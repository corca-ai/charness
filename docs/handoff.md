# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Governing intent** (read first):
  [intent.md](../charness-artifacts/reference-compaction/intent.md) — the point is a
  SMARTER agent, not proof/surface; prune gates/refs that don't earn their place;
  the ONLY test is "그게 정말 최선인가?" (no proxy metric). claim-fidelity/cautilus is
  the *instrument*, read for "does this ref meaningfully help," not "floor passed."

## Current State

- **All contract slices SHIPPED** (Slice 1 keystone → Slice 7 deferred sweep) plus
  the quality prune+brief pilot. The effort is now a per-skill **capture-then-
  diagnose** pass: run the real skill (ungated capture harness), find the DOMINANT
  cost, and pull a lever ONLY if a real one exists.
- **Two H0 diagnoses now bracket the method:**
  - **quality** — lever FOUND+FIXED: dominant cost was artifact **closeout churn**
    (validator re-run 6×), not refs → report-all default + scaffold-first.
  - **spec** — lever NONE (this session):
    [spec-h0-capture-diagnosis.md](../charness-artifacts/reference-compaction/spec-h0-capture-diagnosis.md).
    Costs are load-bearing (fresh-eye critique caught 2 real defects; repo-truth
    ingest), refs NOT dominant (3rd confirmation), the 2 RCF floors genuinely
    opened, the 4 DEPTH refs correctly un-forced. Spec's real compaction already
    was Slices 3/6. **One NAMED candidate survives:** the Bootstrap blanket scans
    (`spec/SKILL.md:21,28,32`) the capable run executed 0× — a lower-context
    capture would prove/kill it (option 3 below); not trimmed blind.

## Next Session

**Do NOT H0-sweep the remaining skills for coverage — that is the proxy disease.**
The two biggest overhead skills (quality #1, spec #2 by refs) are done; the lesson
is that reference count ≠ overhead lever. Decide the direction with the operator:

1. **Close the per-skill lever hunt.** All slices shipped; the method and its honest
   null case are proven. Route future work by a named hypothesis, not ref-count.
2. **The real open problem is SYSTEMIC** (intent.md "Held open"): the context tax a
   skill's overhead levies across a whole session — single captures can't see it,
   so it needs a different instrument. Design it or explicitly defer it.
3. **Named hypothesis on the table:** re-capture `spec` in a *low-context /
   unfamiliar* repo to test whether the Bootstrap blanket scans are globally dead
   weight (prune/brief them) or just redundant-when-you-know-the-repo (keep). Any
   other skill qualifies only with a named avoidable cost stated before capturing.

## Discuss

- The close-vs-continue routing is the operator's call; the evidence says the clear
  per-skill levers are exhausted.
- Ungated evidence path = `capture-skill-run.sh` + `build-observation.mjs`; only
  `cautilus evaluate` scoring is ask-before-run, `cautilus improve` disabled.
- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
