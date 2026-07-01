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
- **RECORD-ONLY this session** (no floor moved, nothing claimed proven). `classTag`/RCF are NOT
  flipped: `claim_fidelity_lib` forbids DUP/INLINE-tagging a live RCF floor, so the flip is
  COUPLED to the MOVE. Blockers to executing the MOVEs: Cautilus is gate-refused (ask-before-run,
  no auth this session), NO substance judge exists (`outcome-assertions.json` absent everywhere),
  and bundles retain no `stream.jsonl` — so each MOVE needs a **fresh authorized capture**.
- Issues: **#411**/**#413** reframed (census INLINE is the driver, not a live "refutation";
  artifact/substance-judge fix stands; #411 capability-contract corrected DEPTH->INLINE),
  **#412** sharpened (continuation-sequence.md is INLINE too), **#415** filed (matcher honesty:
  RCF satisfied by a subagent-prompt name-mention, not a Read).

## Next Session

1. **Execute the 12 capture-gated MOVEs + the hotl/ledger INLINE-token lift** — needs operator
   Cautilus authorization (ask-before-run). Per skill: inline the gist into SKILL.md (watch the
   critique 194/200-line ceiling), drop the RCF filename, prove the RSF/output floor from a FRESH
   capture. No substance judge => an RSF is a FORM floor (over-relax risk); script-driven
   gather/setup (0-coverage) need an `outcome-assertions.json` judge = the #411/#413 redesign.
   Mechanics: `capture-skill-run.sh` needs an ABSOLUTE `--out-dir`; grade mjs `--stream stream.jsonl`;
   scrub the worktree/config before ANY commit (its `config/settings.json` pollutes repo-wide
   `check_doc_links`); broad pytest BEFORE the critique (grep misses path-built consumers).
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
