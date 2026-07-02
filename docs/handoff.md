# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **Slice-7 setup (#413) + handoff (#412) claim-fidelity floors DONE** — goal
  [2026-07-02 setup+handoff floor](../charness-artifacts/goals/2026-07-02-issue-410-411-412-413-reference-compaction-slice-7-per-condition-claim-fidelity-fl.md),
  6 commits `69552811..551a1f49`, all gates green (broad pytest 3981), 5 fresh-eye
  critiques SOUND.
- setup floor moved RCF→RSF `[Repo mode:, Normalization non-claims:]` via live
  capture (+ `## Closeout Vocabulary` + `outcome-assertions.json` substance judge).
  handoff planner conditionalized, and the pickup floor split into two
  per-condition falsifiable fixtures — a clear
  [pickup](../evals/cautilus/handoff-claim-fidelity/pickup.spec.json) arm and an
  ambiguous [pickup-ambiguous](../evals/cautilus/handoff-claim-fidelity/pickup-ambiguous.spec.json)
  arm, both capture-proven; continuation-sequence.md reclassified on-demand DEPTH.
- **Method locked (operator-directed):** every skill path/condition gets its OWN
  falsifiable fixture; capture VERIFIES, docs+routing DESIGN; token OBSERVED never assumed.
- Deferred honestly (not captured): setup greenfield + narrow host-docs-only
  normalization (greenfield not in-repo capturable, #410).

## Next Session

1. **Operator-gated closeout of the DONE work:** close #412 + #413, check #410
   setup+handoff rows, `git push` (branch 30+ ahead). Fixes landed + captured locally.
2. **Continue the sweep** (next ranked chunks): gather #411 public-URL output-floor
   (private-SaaS half already done), then the correctness sweep of untested HYPOTHESIS
   floors (announcement/create-skill/find-skills/ideation/narrative/release/spec),
   then matcher-honesty #415 — same per-condition-falsifiable + capture-before-pin method.
3. **File the deferred guard idea:** a validator cross-checking each planner's
   intent/condition-keyed required-reads against scenario specs (auto-detect a
   conditionally-required doc no scenario forces) — would have caught the ambiguous-fixture gap.

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [session retro](../charness-artifacts/retro/2026-07-02-session-retro.md) · [cautilus latest](../charness-artifacts/cautilus/latest.md)
