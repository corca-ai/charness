# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slice 7 — all 8 skills captured + committed, but the sweep decided
  floors FROM CAPTURES ALONE and never checked [census.json](../charness-artifacts/reference-compaction/census.json)
  (the audit). Cross-check shows most
  "keep" decisions CONTRADICT the census. NEEDS a reconciliation pass FIRST — see
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).**
  Census-aligned + standing: the 3 MOVES (create-cli `323f14a6`, achieve `cf0edb5f`, hitl `1397731a`
  — all dropped INLINE docs), document-seams.md DUP delete (`92d7f2aa`), and the DEPTH keeps. Suspect
  (INLINE/DUP kept as doc-open floors, contradict census → likely compaction moves): hotl `65d12860`
  (both DUP/INLINE), handoff `92d7f2aa` (workflow-trigger/state-selection/spill-targets INLINE),
  critique `4fc6389c` (counterweight-triage.md INLINE). gather **#411** / setup **#413** are INLINE,
  not "refuted mysteries" — re-frame. Also filed **#412** (handoff planner).

## Next Session

1. **Slice-7 census reconciliation (DO FIRST) — see
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).**
   Method: census bucket FIRST, capture to verify, reconcile on disagreement; INLINE/DUP → inline the
   gist + retire the doc-open floor (never keep it because a capture opened it — an INLINE doc opens
   redundantly). Re-examine the suspect keeps (hotl/handoff/critique) and re-frame #411/#413 (gather/setup
   are INLINE → inline + output-floor, not "refuted"). Where census (per-doc single bucket) disagrees with
   a capture, the doc is MIXED — split the INLINE part from the genuine DEPTH (e.g. hotl proof-level ladder).
   Then #412 (handoff planner) + the matcher nuance (subagent-prompt name-mention counts as RCF engagement).
2. **Continue correctness sweep** for the remaining untested HYPOTHESIS floors (announcement,
   create-skill, find-skills, ideation, narrative, release, spec), one at a time — expect
   keeps/refutes, not just moves. Mechanics: `capture-skill-run.sh` needs an ABSOLUTE `--out-dir`;
   grade mjs `--stream stream.jsonl`; scrub the worktree/config before ANY commit — its
   `config/settings.json` pollutes repo-wide `check_doc_links` (never commit while a capture is live);
   broad pytest BEFORE the critique (grep misses path-built consumers, e.g.
   [test_handoff_skill.py](../tests/quality_gates/test_handoff_skill.py)).
3. **AGENTS.md lesson-internalization live capture (operator-raised)** — does AGENTS.md make
   an agent READ+ACT on recent-lessons? = the deferred "live-session capture unit" of the
   existing `lesson-internalization-claim-fidelity` eval (offline instrument DONE; #3 unblocks
   the capture side). Spec-level: arbitrary-session harness + vacuous-pass guard + rotation.

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [impl finding](../charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md)
