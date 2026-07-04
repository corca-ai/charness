# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it now, not `find-skills`); bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session (all pushed to origin/main; three issues CLOSED):**
  - **#404 mutation regression CLOSED + CI-verified** — the "StrykerJS JSON
    missing" auto-comment was a symptom: a hardcoded `'16'` xdist assertion failed
    cosmic-ray's baseline probe, short-circuiting the `&&` so StrykerJS never ran.
    The fix (`2c0d5c7c`) was committed-but-unpushed; published the 5-commit stack
    after clearing a `dup-ratchet` blocker (`_package_root` bootstrap → intentional,
    `94d37223`). `workflow_dispatch` run `28722214682` = **success**.
  - **#415 matcher honesty CLOSED** — `collectCommandLog` no longer counts
    `Agent`/`Task` spawn-prompt strings, so an RCF doc-open floor cannot pass on a
    name-mention (`06c122ff`). Regression test + fresh-eye SHIP.
  - **#411 gather floor CLOSED** — public-URL RCF doc-opens retired → substance
    floor, both tagged INLINE (`51a40874`); rode the already-proven 2026-07-02
    capture + framework support `325909f7`, no new capture.
- **Prior work now published:** the vulture triage, dup_ratchet split, vulture
  wiring, and D36 advisory commits were local-only (origin/main was 5 behind); this
  session's push published them.

## Next Session

1. **#410 remaining RCF→RSF sweep (heavyweight, ask-before-run captures).** The
   doc-opening skills `handoff`×4 + `hotl/ledger-and-dispositions` need fresh
   ask-before-run Cautilus captures to OBSERVE an honest RSF token before flipping
   (capture-before-pin; each capture ~1M tokens); `setup`×4 is #413 (same
   substance-floor shape as gather). Queue + method:
   [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
2. **#416 / #414 / #408 concept-boundary discipline (operator design interview).**
   Shape an adapter-owned boundary checkpoint for the lifecycle skills
   (impl/critique/issue/quality/spec/achieve), keeping Charness portable (no
   repo-local taxonomy). Design conversation first; no code until agreed.
3. **81-site argparse-help debt (largest, churn-heavy, run LAST).** Default-off;
   baseline rotation runs alone. Trip-wire **D33**: `run_skill_efficiency_ab.py` at
   479/480 — extract a module before appending.

## Discuss

- **D34/D35 DECLINED** (2026-07-04) — disclosed presence-floor residuals; reopen
  only if the recorded failure materializes. See [deferred-decisions.md](./deferred-decisions.md).

## References

- [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
