# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Big picture:** skills satisfy two axes, evals verify each SEPARATELY —
  **correctness** (claim-fidelity, proven by live capture) and **efficiency** (advisory).

## Current State

- **v0.58.0 SHIPPED** — tag pushed, `main`==`origin/main`, all three `--release`
  gate blockers cleared honestly; #412/#413 closed on push. Historical runbook:
  [v0.58.0-blockers.md](../charness-artifacts/release/v0.58.0-blockers.md).
- **Slice-7 setup (#413) + handoff (#412) claim-fidelity floors DONE** — goal
  [2026-07-02 setup+handoff floor](../charness-artifacts/goals/2026-07-02-issue-410-411-412-413-reference-compaction-slice-7-per-condition-claim-fidelity-fl.md).
- **Method locked (operator-directed):** every skill path/condition gets its OWN
  falsifiable fixture; capture VERIFIES, docs+routing DESIGN; token OBSERVED never assumed.
- Deferred honestly (not captured): setup greenfield + narrow host-docs-only
  normalization — greenfield not in-repo capturable (#410).

## Next Session

1. **Continue the correctness sweep** — same per-condition-falsifiable +
   capture-before-pin method, next ranked chunks:
   - **#411** gather claim-fidelity floor redesign (public-URL output-floor;
     private-SaaS half done).
   - correctness sweep of the untested HYPOTHESIS floors.
   - **#415** matcher honesty (RCF floor met by a prompt name-mention, not a real Read).
2. **File the deferred guard idea:** a validator cross-checking each planner's
   intent/condition-keyed required-reads against scenario specs (auto-detect a
   conditionally-required doc no scenario forces).

## Discuss

- Brittle test: [test_handoff_plan.py](../tests/test_handoff_plan.py)
  `..._derives_refresh_and_pickup` reds broad pytest on any >=60-line handoff. Keep this
  file under 60 lines until the test is decoupled from live state.

## References

- pickup: [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
- proofs: [session retro](../charness-artifacts/retro/2026-07-02-session-retro.md) · [cautilus latest](../charness-artifacts/cautilus/latest.md)
