# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Reference-compaction Slice-7 census reconciliation DONE (commit `52a64799`).** All 13
  contested doc-open floors re-examined census-FIRST via an adversarial analyze->verify
  workflow (26 agents): **12 MOVE, 1 MIXED (hotl/ledger-and-dispositions), 0 KEEP** — every
  prior "keep because the capture opened it" was the flagged method error (an INLINE/DUP doc
  opens redundantly). Full verdicts + queue:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- **Execution + METHOD CORRECTION (operator-directed).** Design fixtures **per condition** from the
  docs+routing (what each ref is FOR + WHEN read); the capture only VERIFIES — no capture needed to
  design. See the reconciliation doc's "METHOD CORRECTION" +
  [gather-fixture-redesign.md](../charness-artifacts/reference-compaction/gather-fixture-redesign.md). Done:
  ✅ hotl/proof-rules (fresh capture, `ceb87340`), ✅ critique/counterweight-triage (existing evidence,
  `bf2fdeef`), ✅ gather per-condition redesign — NEW private-SaaS scenario PROVEN, corrects #411
  (`4f4586b5`). Next: **setup + handoff by the same per-condition method** — re-examine their
  MOVE/INLINE verdicts (some may be genuine DEPTH under a condition no fixture exercises → design that
  scenario, don't retire) — plus gather's public-URL output-floor. hotl/ledger token-lift deferred.
- Issues: **#411**/**#413** reframed (census INLINE is the driver, not a live "refutation";
  artifact/substance-judge fix stands; #411 capability-contract corrected DEPTH->INLINE),
  **#412** sharpened (continuation-sequence.md is INLINE too), **#415** filed (matcher honesty:
  RCF satisfied by a subagent-prompt name-mention, not a Read).

## Next Session

1. **Continue the per-condition fixture work** (see the reconciliation doc's METHOD CORRECTION):
   **setup** then **handoff** — trace each ref to its trigger, design a scenario per genuinely-DEPTH
   condition, retire only truly-inlined docs; then gather's public-URL output-floor + hotl/ledger
   token-lift. Mechanics: `capture-skill-run.sh` needs an ABSOLUTE `--out-dir` OUTSIDE the repo (its
   `config/settings.json` pollutes `check_doc_links`); grade with
   `build-skill-execution-observation.mjs --spec <spec> --stream <out>/stream.jsonl`; broad pytest
   BEFORE the critique (grep misses path-built consumers).
2. **Continue correctness sweep** for the remaining untested HYPOTHESIS floors (announcement,
   create-skill, find-skills, ideation, narrative, release, spec), one at a time — expect
   keeps/refutes, not just moves.
3. **AGENTS.md lesson-internalization live capture (operator-raised)** — the deferred
   "live-session capture unit" of the existing `lesson-internalization-claim-fidelity` eval
   (offline instrument DONE). Spec-level: arbitrary-session harness + vacuous-pass guard + rotation.

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [cautilus latest](../charness-artifacts/cautilus/latest.md) · [reconciliation](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md)
