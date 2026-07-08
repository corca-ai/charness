# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session: completed the #421 mutation-gate recovery goal**
  ([goal artifact](../charness-artifacts/goals/2026-07-08-fix-421-mutation-regression.md),
  Status: complete; chunked-routing pick). Key facts: the 4 recurring nightly
  failures were a time-armed red baseline test (Boundary Ownership
  `RULE_DATE=2026-07-06` detonating a truncating roundtrip test) whose fix
  was ALREADY local (`38219d95`); the #421 proof targets are now covered
  (100% both files); the post-push judgment range `57af3d2b..HEAD` audits
  clean; 8 mutants killed, 8 accepted with empirical equivalence proofs.
  #422 filed (gate misreports baseline-pytest aborts). `main` still ahead of
  `origin/main`, **NOT pushed**.

## Next Session

1. **Operator lane**: push `main`; the next scheduled mutation run
   (`17 */12 * * *`) judges `57af3d2b..HEAD`, expected green, and
   auto-closes #421 (machine-owned close; do not close manually).
2. **#420 close**: already resolved by Slice R (`6415175b`, advisory-only
   ratio); verify + resolution critique + comment/close via `issue`.
3. **Test-debt rotation (standing)**: sweep the post-2026-07-03-audit
   test-LOC delta (~+3.2k); deletions need mutation proof + fresh-eye review;
   never headroom-pressured.
4. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each)**;
   method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
5. **#413 setup/greenfield** RCF→RSF — needs a fresh-sandbox capture.
6. **#371 residuals (open by decision)** — upstream
   `vercel-labs/agent-browser#1334`; Tier 1b gated on a pinned-CLI probe.
7. **#422 gate misreporting** (small): surface failing baseline nodeids in
   the mutation summary instead of the missing-report symptom.
8. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a
  grandfathered-floor's landing day, run the suite as-of tomorrow's
  enforcement date (or the post-cutoff pin tests) so truncating consumers
  detonate before push — first occurrence recorded (#421 debug artifact);
  promote to a gate only on recurrence per floor-addition restraint.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
