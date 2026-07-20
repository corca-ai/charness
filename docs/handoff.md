# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- v2.4.1 is PUBLISHED (tag `v2.4.1 -> e36a0b93`, unauthenticated https 200,
  installed `charness version -> 2.4.1` after refresh). Scope: the #448
  scoped-rebaseline parity fix and the #446 CI test-determinism fix. The
  v2.4.1 observer JSON now carries `distinct_channel_verification.observer`
  (v2.4.0 caveat resolved) —
  [release critique](../charness-artifacts/critique/2026-07-20-v2-4-1-release-critique.md).
- #448 stays OPEN by design: shipped fix covers within-invocation universe
  parity only ([slice critique](../charness-artifacts/critique/2026-07-20-dup-ratchet-scoped-rebaseline-parity-critique.md)).
  Residuals: wrapper cached-inventory / fingerprint-normalization hypothesis,
  cross-invocation drift. Closure proof = Ceal re-verification against v2.4.1.
- #446 root cause re-diagnosed and fixed in `6dda14c0`: NOT the basetemp
  flake — the xdist test hardcoded `-n 16` while CI runners have 4 cores
  (deterministic host dependence; class fully drained per fresh-eye review).
  Only a scheduled green `Mutation Tests` run auto-closes it.
- Sibling scan closed through Tier 2; Tier 3 (E-J) stays boy-scout only.

## Next Session

1. Check the next scheduled `Mutation Tests` run (00:17/12:17 UTC cadence,
   cron delay up to ~45 min) on post-`6dda14c0` main: green auto-closes #446;
   red now falsifies the cpu-pin diagnosis — read the failing nodeid before
   theorizing.
2. Ask/verify the Ceal-side #448 scenario against v2.4.1 (accept the exact
   suggested rotations) before any #448 closure; then #449 (machine-distinct
   CI observer) remains the open release-proof design item.
3. Deferred discovery follow-ups remain available: inline `.rglob`/`ls-files`
   pathspec discovery, `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero
   test-surface advisory.
4. Keep D18 ignored unless the operator explicitly reopens it. Stale
   `charness-run-*` basetemp reaping stays intentionally deferred.
5. For mutation-pool changes, ask the selector before widening a producer by
   hand; for new dynamic-call syntax, add wrong-path/loader/receiver and
   disconnected-control-flow fixtures first.

## Discuss

- #448 scoped-accept deferred items (recorded in the critique): overlay-missing
  advisory in scoped mode, advisories on the refused early-return, explicit
  `--accept-family` of an intentional id test — pick up only with the next
  dup-ratchet slice.

## References

- [abstracted-pattern sibling scan (next-session fix backlog)](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [retention RCA](../charness-artifacts/debug/2026-07-20-debug-review.md)
- [basetemp deletion-race RCA](../charness-artifacts/debug/2026-07-20-standing-pytest-basetemp-deletion-race.md)
- [release state](../charness-artifacts/release/latest.md)
- [quality review](../charness-artifacts/quality/latest.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
