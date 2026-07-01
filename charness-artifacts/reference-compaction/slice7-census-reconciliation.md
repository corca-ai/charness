# Slice 7 needs a census reconciliation pass (method error — read this first)

**2026-07-01, operator-surfaced.** The Slice 7 sweep decided each skill's floor
from the LIVE CAPTURE ALONE and never cross-referenced `census.json` — the audit
that had ALREADY classified all 196 references. The result: most "keep" decisions
CONTRADICT the census, and two "refuted" findings mis-framed census-INLINE
confirmations as new mysteries. The audit was done; the sweep just didn't align the
fixtures/specs to it.

## The cross-check (census bucket vs the Slice-7 decision)

| skill | Slice-7 decision | ref | census bucket | verdict |
|---|---|---|---|---|
| create-cli | MOVE (drop) | command-conventions.md | INLINE | ✅ aligned (dropped) — but tagged DEPTH, should be INLINE |
| achieve | MOVE (drop) | goal-artifact.md, lifecycle.md | INLINE | ✅ aligned (dropped) — tag should be INLINE |
| hitl | MOVE (drop) | chunk-contract.md | INLINE | ✅ aligned (dropped) — tag should be INLINE |
| handoff | del | document-seams.md | DUP | ✅ aligned (deleted) |
| handoff | keep | chunked-routing.md | DEPTH | ✅ aligned (kept) |
| critique | keep | premortem-decision.md, autonomous-trigger.md | DEPTH | ✅ aligned (kept) |
| **hotl** | **KEEP** | proof-rules.md | **DUP** | ❌ CONTRADICTS — census says redundant |
| **hotl** | **KEEP** | ledger-and-dispositions.md | **INLINE** | ❌ CONTRADICTS |
| **handoff** | **KEEP** | workflow-trigger.md, state-selection.md, spill-targets.md | **INLINE** | ❌ CONTRADICTS |
| **critique** | **KEEP** | counterweight-triage.md | **INLINE** | ❌ CONTRADICTS |
| **gather** | **refuted→#411** | source-priority.md, capability-contract.md | **INLINE** | ❌ mis-framed — INLINE, not a mystery |
| **setup** | **refuted→#413** | normalization-flow.md, agent-docs-policy.md, default-surfaces.md | **INLINE** | ❌ mis-framed — INLINE |

The 3 MOVES align with the census (drop INLINE docs). Everything I "kept" because a
capture OPENED it contradicts the census, which says those docs are INLINE/DUP.

## The method error (do NOT repeat)

I inferred "the run opened the doc → it is load-bearing → keep the doc-open floor."
That inference is invalid: **a run can open an INLINE/DUP doc redundantly.** The
census already judged the content is duplicated in SKILL.md, so the open is wasteful
whether or not a given run does it. Deciding floors from captures alone, ignoring the
existing audit, produced answers that contradict the audit.

## Correct method for the reconciliation pass

For each Slice-7 skill, per RCF ref:

1. **Read the census bucket FIRST** (`census.json` `per_skill[].references[].bucket`
   + `evidence`). The census is the audit of record.
2. **INLINE / DUP** → the compaction move applies: verify the gist is actually in
   SKILL.md (INLINE it if the census says "inline X" and it isn't yet — that is the
   compaction), then RETIRE the doc-open floor. Floor on an emitted token (if
   distinctive, create-cli pattern) or output/substance (setup/gather have no clean
   token → artifact/substance, the honest core of #411/#413). Do NOT keep a doc-open
   floor for an INLINE/DUP doc because a capture happened to open it.
3. **DEPTH** → the doc-open CAN be a floor; verify the fixture exercises the DEPTH.
4. **Census ⟷ capture DISAGREE** (census INLINE, but the capture opened it — e.g.
   hotl proof-rules.md opened for the proof-LEVEL ladder that is NOT in SKILL.md's
   `## Proof Rules` preview): the doc is MIXED (INLINE part + DEPTH part). The census
   flattened it to one bucket and may have UNDER-counted the DEPTH. DIG: split the
   compactable part (inline it) from the genuine DEPTH (keep on-demand), and set the
   floor to the DEPTH signal or the output. This reconciliation is the ACTUAL work
   the sweep skipped.

## What this means for the committed Slice-7 slices

- **MOVES (create-cli/achieve/hitl) + document-seams delete + the DEPTH keeps
  (chunked-routing/premortem-decision/autonomous-trigger): census-aligned, stand.**
  (Minor: the classTag on dropped INLINE docs should be INLINE, not DEPTH.)
- **The INLINE/DUP "keeps" (hotl both, handoff workflow-trigger/state-selection/
  spill-targets, critique counterweight-triage.md): re-examine — they likely should
  be compaction moves, not keeps.** My captures showed opens; the census says
  INLINE/DUP; reconcile per step 4 before trusting the keep.
- **gather #411 / setup #413: re-frame from "harness redesign for a refuted mystery"
  to "census says INLINE → inline the gist + retire the doc-open; floor on output
  because there is no clean single emitted token."** The artifact/substance floor is
  the right REPLACEMENT floor, but the driver is the census INLINE verdict, not a
  surprise.

Bottom line: **census bucket first, capture to verify, reconcile on disagreement** —
never decide a floor from a capture while ignoring the audit.
