# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session (2026-07-08): issue-backlog sweep + test-debt rotation.**
  #420 CLOSED (advisory-only verified live); #371 CLOSED by operator decision
  (residuals in the close comment); #413 already closed; **#422 fixed +
  auto-CLOSED** (`8b28ab3e`) — and provider-roundtrip PROVEN: the 12:50 UTC
  scheduled red posted the real failing nodeid instead of the
  StrykerJS-missing collateral.
- That 12:50 red was a new env-dependent test (`test_migrate_dup_fingerprints`
  live-scan CLI pin; no nose binary in the mutation env) — nose-guard skipif
  landed (`28d76718`), mirroring the sibling idiom.
- **Test-debt rotation DONE for this cycle** (`8e1fd200`): 193 delta tests
  judged, 4 verified-redundant deleted, 2 candidates rejected as
  load-bearing. Full method + evidence:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md).
  Next rotation baseline = `8e1fd200`.

## Next Session

1. **Watch #421 auto-close (machine-owned; do not close manually)**: the next
   scheduled run (`17 */12 * * *` UTC, next ~2026-07-09 00:17) judges
   `57af3d2b..8e1fd200`, expected green. If red, the summary now names the
   real blocking signal (#422 fix, roundtrip-proven) — read it first.
2. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each)**;
   method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
   The #413 setup/greenfield fresh-sandbox capture rides this queue's method.
3. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a grandfathered-floor's
  landing day, run the suite as-of tomorrow's enforcement date so truncating
  consumers detonate before push; promote to a gate only on recurrence.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).
- Deferred from #420 close: nothing pins the `--advisory` flag at
  `run-quality.sh:505`; add a pin only if the hard-block posture regresses.

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
