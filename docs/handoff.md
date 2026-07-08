# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session: issue-backlog sweep (chunked-routing pick, operator-directed).**
  #420 CLOSED (advisory-only ratio verified live, fresh-eye critique);
  #371 CLOSED by operator decision (residuals recorded in the close comment:
  upstream `vercel-labs/agent-browser#1334`, Tier 1b deferred); #413 found
  already closed (v0.58.0); **#422 fixed + auto-CLOSED** (`8b28ab3e` pushed
  2026-07-08 ~12:30 UTC): sampler baseline-pytest aborts now write
  `reports/mutation/baseline-abort.json` and both summary scripts lead with
  the failing nodeids instead of the StrykerJS-missing collateral. Full
  ledger in the commit body + `charness-artifacts/issue/2026-07-08-issue-422-*.md`.
- The 2026-07-08 12:17 UTC scheduled mutation run had NOT fired as of 12:37
  (cron lag); when it runs it judges `57af3d2b..8b28ab3e` — all changed pool
  lines have local coverage proof (`check_changed_line_mutation_coverage`
  green post-commit) and dup-ratchet was scoped-re-baselined (1 rotation + 7
  #395-class fingerprint rotations accepted).

## Next Session

1. **Watch #421 auto-close (machine-owned; do not close manually)**: the next
   scheduled run (`17 */12 * * *` UTC) judges `57af3d2b..8b28ab3e`, expected
   green. If red, the summary now names the real blocking signal (#422 fix) —
   read it first.
2. **Test-debt rotation (standing)**: sweep the post-2026-07-03-audit
   test-LOC delta (~+3.2k); deletions need mutation proof + fresh-eye review;
   never headroom-pressured.
3. **#410 remaining handoff flips (capture-gated, ~1.7-2.4M tokens each)**;
   method + queue:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
   The #413 setup/greenfield fresh-sandbox capture rides this queue's method.
4. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
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
