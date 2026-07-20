# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- v2.4.0 is PUBLISHED, confirmed by distinct channels (gh API, remote tag
  `v2.4.0 -> 2ae99627`, unauthenticated https 200, installed
  `charness version -> 2.4.0`). Caveat: the v2.4.0 observer JSON predates the
  new `observer` field; it applies from the next release.
- #448 charness-side fix LANDED, issue stays OPEN: scoped dup-ratchet accepts
  (`--accept-rotation`/`--accept-family`) now exempt overlay-intentional
  families and unnamed membership reductions (evaluate-path parity; never
  absorbed) —
  [critique](../charness-artifacts/critique/2026-07-20-dup-ratchet-scoped-rebaseline-parity-critique.md).
  Residuals NOT fixed: wrapper cached-inventory / fingerprint-normalization
  hypothesis, cross-invocation drift. Closure proof = Ceal re-verification
  against a released build.
- #446 (mutation-test regression on main): both failing scheduled runs were on
  pre-fix `5235228e`; the fix (`1834090b`) landed after. The next scheduled
  `Mutation Tests` run (12:17 UTC cadence) on current main should auto-close it;
  a dispatch-green run must NOT be used to close (workflow false-proof note).
- Sibling scan closed through Tier 2; Tier 3 (E-J) stays boy-scout only.

## Next Session

1. Check the scheduled `Mutation Tests` run after 2026-07-20 ~12:40 UTC: green
   auto-closes #446; red means the basetemp fix is insufficient — debug on
   current main with a full-suite scope-matched reproduction.
2. After the next release, ask/verify the Ceal-side #448 scenario (accept the
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
